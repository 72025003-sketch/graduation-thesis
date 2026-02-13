# 海事サイバーセキュリティ演習環境: インストールガイド

## プロジェクト構成

本リポジトリは以下のコンポーネントで構成されています。

1.  **ネットワークシミュレーション (Docker)**
    *   実際の船舶ネットワーク（CrewNW, BusinessNW, NaviNW）をDockerコンテナで再現。
    *   攻撃者（Kali Linux）や被害者（脆弱なサーバー、ECDIS）を含みます。
2.  **Webアプリケーション (Next.js)**
    *   IDSの検知状況や船舶のステータスを可視化するダッシュボード。
3.  **解析・検知エンジン (Zeek & Python)** (開発中)
    *   **Zeek/Spicy**: プロトコルパースとログ生成。
    *   **Deep Learning (Python)**: 生成されたログに基づく異常検知。

## ネットワークトポロジー

```mermaid
graph TD
    Internet((Internet)) --- FW1
    subgraph "Crew Network (192.168.5.0/24)"
        FW1[FW1] --- FW2
        FW1 --- CrewPC[Crew PC]
        FW1 --- C2[C2 Server (Kali)]
    end
    
    subgraph "Business Network (192.168.10.0/24)"
        FW2[FW2] --- LogServer[LOG Server<br>(Target)]
    end
    
    subgraph "Navigation Network (192.168.20.0/24)"
        FW2 --- GPS[GPS/AIS Sim]
        FW2 --- OpenCPN[OpenCPN<br>(ECDIS)]
        GPS -->|NMEA| OpenCPN
    end
```

## クイックスタート

### 1. 動作環境・前提条件
*   Docker Engine 20.10以上
*   Docker Compose v2.0以上

### 2. インストール手順

リポジトリをクローン、またはdocker-compose.ymlをダウンロードし、ディレクトリ内で以下のコマンドを実行します。

```bash
docker compose up -d
```
※初回実行時は、Docker Hubからイメージ（FW, WebApp, OpenCPN等）がダウンロードされるため、時間がかかる場合があります。

### 3. 起動確認

*   **ダッシュボード**: ブラウザで [http://localhost:3000](http://localhost:3000) にアクセスしてください。

## ディレクトリ構造

```
.
├── docker/                 # Docker環境設定
│   ├── c2-kali/           # 攻撃用コンテナ
│   ├── router/            # ルーター/FW
│   ├── log-server/        # ターゲットサーバー
│   ├── navi-devices/      # 航海機器 (OpenCPN, GPS Sim)
│   └── crew-hosts/        # その他ホスト
├── webapp/                 # Next.js Webアプリケーション
├── docker-compose.yml      # コンテナ構成定義
└── README.md               # 本ドキュメント
```

## 今後の実装予定
*   IEC61162-450への対応
*   攻撃手順とOpenCPN画面のタブ切り替え 

## ライセンス
本プロジェクトは研究・教育目的で公開されています。
