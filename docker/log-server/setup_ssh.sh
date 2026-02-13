#!/bin/bash
# LOG server の SSH設定スクリプト
# 意図的に脆弱なパスワードを設定

echo "=== LOG server 起動中 ==="

# デフォルトゲートウェイをFW2に設定
ip route del default
ip route add default via 192.168.10.1

# 脆弱なユーザーアカウントを作成
useradd -m -s /bin/bash admin
echo "admin:password123" | chpasswd

echo "[!] 脆弱なユーザーを作成: admin / password123"

# ログディレクトリ作成
mkdir -p /var/log/nmea

# rsyslogdを起動
service rsyslog start

# SSHサーバーを起動
/usr/sbin/sshd -D &

echo "=== LOG server 設定完了 ==="
echo "SSH: 192.168.10.20:22"
echo "ユーザー: admin"
echo "パスワード: password123 (脆弱!)"
echo ""
echo "NMEA送信スクリプト: /opt/inject_nmea.py"
