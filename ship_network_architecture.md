# 🚢 船内ネットワークアーキテクチャとサイバーセキュリティ演習環境

本資料は、コンテナ（Docker）ベースで構築された「船舶ネットワーク（GPSスプーフィング攻撃シミュレーション環境）」のネットワーク構成と各コンポーネントの役割について解説する教材です。

---

## 1. ネットワークの全体像 (Network Topology)

現代の船舶は「浮かぶオフィス」とも呼ばれ、単なる航海機器だけでなく、乗組員の生活用ネットワークや業務管理用ネットワークが混在しています。本環境では、実船のセキュアな設計を模倣し、ルータ/ファイアウォール（FW1, FW2）によってネットワークを複数の「ゾーン（セグメント）」に分割しています。

```mermaid
flowchart TD
    subgraph InternetZone ["Internet (模擬外部)"]
        internet([Internet<br>192.168.1.0/24])
    end

    subgraph Router1 ["エッジ境界"]
        fw1{{FW1<br>エッジルータ}}
    end

    subgraph CrewZone ["Crew NW (乗組員ネットワーク) - 信頼度: 低"]
        crew_switch[192.168.5.0/24]
        c2_server[C2 Server<br>攻撃元 (Kali)]
        crew_pc[Crew PC<br>一般端末]
    end

    subgraph DMZZone ["DMZ (FW間接続)"]
        dmz_switch[10.254.0.0/24]
    end

    subgraph Router2 ["内部境界"]
        fw2{{FW2<br>内部ルータ}}
    end

    subgraph BizZone ["Business NW (業務ネットワーク) - 信頼度: 中"]
        biz_switch[192.168.10.0/24]
        log_server[Log Server<br>脆弱なSSH]
        webapp[Dashboard<br>Web画面]
    end

    subgraph NaviZone ["Navi NW (航海機器ネットワーク) - 信頼度: 高"]
        navi_switch[192.168.20.0/24]
        gps_ais[GPS/AIS<br>シミュレータ]
        opencpn[OpenCPN<br>海図/ECDIS]
    end

    internet --- fw1
    fw1 --- crew_switch
    fw1 --- dmz_switch
    
    crew_switch --- c2_server
    crew_switch --- crew_pc

    dmz_switch --- fw2

    fw2 --- biz_switch
    fw2 --- navi_switch

    biz_switch --- log_server
    biz_switch --- webapp

    navi_switch --- gps_ais
    navi_switch --- opencpn

    classDef highSec fill:#ffcccc,stroke:#cc0000,stroke-width:2px;
    classDef medSec fill:#ffffcc,stroke:#cccc00,stroke-width:2px;
    classDef lowSec fill:#ccffcc,stroke:#00cc00,stroke-width:2px;
    classDef router fill:#dae8fc,stroke:#6c8ebf,stroke-width:2px;
    classDef attacker fill:#333333,stroke:#ff0000,color:#fff,stroke-width:3px;

    class navi_switch,gps_ais,opencpn highSec;
    class biz_switch,log_server,webapp medSec;
    class crew_switch,crew_pc lowSec;
    class fw1,fw2 router;
    class c2_server attacker;
```

---

## 2. 各ネットワークゾーンの解説

本環境は、セキュリティレベル（信頼度）の異なる4つの内部ネットワークと模擬インターネットで構成されています。

### 🌐 Internet (192.168.1.0/24)
外部のインターネットを模擬したネットワークです。FW1 を経由して船内の特定ネットワークと通信を行います。

### 📶 Crew NW (乗組員ネットワーク / 192.168.5.0/24)
* **セキュリティレベル:** 低
* **概要:** 乗組員が個人的なスマートフォンやPCを接続するネットワークです。外部インターネットに接続しやすく、私用デバイスが接続されるため、マルウェア感染リスクが最も高い領域です。
* **配置コンポーネント:** 
  * `crew-pc`: 乗組員の一般PC
  * `c2-server`: 攻撃者が仕込んだ、あるいは外部から操作する攻撃用サーバー（Kali Linux）

### 🚧 DMZ (非武装地帯 / 10.254.0.0/24)
* **セキュリティレベル:** 中継
* **概要:** FW1 と FW2 を直接つなぐための中継用ネットワークです。Crew NW と内部ネットワーク（業務・航海機器）を直接ルーティングさせず、FW2 での厳密なアクセス制御を可能にする「緩衝地帯」として機能します。

### 🏢 Business NW (業務ネットワーク / 192.168.10.0/24)
* **セキュリティレベル:** 中
* **概要:** 船舶の運航管理、機関監視ログの収集、事務作業などを行うネットワークです。
* **配置コンポーネント:**
  * `log-server`: 各種ログを蓄積するサーバー。意図的に脆弱な設定（SSHパスワード認証の不備等）が残されています。
  * `webapp`: 監視ダッシュボード（Nginx配信）。船の現在地や攻撃用インターフェースをブラウザ上で表示します。

### ⚓ Navi NW (航海機器ネットワーク / 192.168.20.0/24)
* **セキュリティレベル:** 高
* **概要:** 船舶の安全な航行に直結する非常に重要なネットワーク（OTネットワーク）です。本来、他のネットワークから隔離（エアギャップ）されているべきですが、業務効率化のために Business NW などと接続されるケースが増えています。
* **配置コンポーネント:**
  * `opencpn`: 電子海図情報システム（ECDIS）。自船や他船の位置を画面上にプロットします。
  * `gps-ais`: NMEAデータを生成し、GPSとAIS（船舶自動識別装置）の信号を模擬的にブロードキャストするシミュレータ。

---

## 3. 境界防御（ファイアウォール）の役割

2つのルータ/ファイアウォールコンテナが、ゾーン間のトラフィックを制御（またはルーティング）しています。

1. **FW1 (`192.168.1.254` / `192.168.5.1` / `10.254.0.1`)**
   * インターネットと船内ネットワークの境界に位置します。
   * Crew NW や DMZ に対するルーティングを提供します。
2. **FW2 (`10.254.0.2` / `192.168.10.1` / `192.168.20.1`)**
   * Crew NW（低信頼）からの直接アクセスを遮断し、Business NW と Navi NW を保護する「内部の壁」です。
   * 本演習における最終防衛ラインとして機能します。

---

## 4. 想定されるサイバー攻撃シナリオ（ラテラルムーブメント）

本環境は、**「低セキュリティ領域（Crew NW）から高セキュリティ領域（Navi NW）へどのように侵入されるか」** を体験・検証するためのものです。典型的な攻撃フローは以下のようになります。

1. **初期潜入 (Initial Access):**
   攻撃者は乗組員の私用端末のマルウェア感染や、Wi-Fiのクラッキングを経て、`Crew NW` 内部に侵入（`c2-server` の配置）します。
2. **偵察と横展開 (Reconnaissance & Lateral Movement):**
   `c2-server` からポートスキャン等を実行し、DMZ を越えて `Business NW` に到達可能な脆弱な端末を探します。
3. **権限昇格・拠点確保 (Privilege Escalation):**
   `Business NW` にある `log-server` の脆弱な SSH やパスワードの使い回しを突き、`log-server` の制御を奪います。
4. **OT領域への攻撃 (Impact / Spoofing):**
   乗っ取った `log-server`（中セキュリティ）を踏み台にすることで、本来アクセスできないはずの `Navi NW` への通信を試みます。そこから偽の NMEA データ（AIS / GPS信号）を `opencpn` に送りつけ（GPSスプーフィング）、船の航路を意図的に狂わせるという物理的被害を引き起こします。

> **💡 教訓:**
> 「Navi NW（OT機器）はインターネットに繋がっていないから安全」という神話は、Crew NW や Business NW を踏み台にされることで崩れ去ります。各ゾーン間の厳密なアクセス制御と、ゼロトラストアーキテクチャの導入が現代の船舶ネットワークには求められています。
