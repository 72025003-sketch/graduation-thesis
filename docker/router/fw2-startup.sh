#!/bin/sh
# FW2 起動スクリプト
# CrewNW ⟷ Business NW ⟷ Navi NW のルーティング設定
# 攻撃シナリオ用：CrewNW → Business NW の通信を許可

echo "=== FW2 起動中 ==="

# インターフェースの自動特定
# CREW_IF は削除 (DMZ経由で接続)
DMZ_IF=$(ip -4 addr show | grep '10.254.0.2' | awk '{print $NF}')
BIZ_IF=$(ip -4 addr show | grep '192.168.10.1' | awk '{print $NF}')
NAVI_IF=$(ip -4 addr show | grep '192.168.20.1' | awk '{print $NF}')

echo "FW2 Detected: DMZ=$DMZ_IF, Business=$BIZ_IF, Navi=$NAVI_IF"

# iptablesのデフォルトポリシー設定
iptables -P FORWARD DROP
iptables -P INPUT ACCEPT
iptables -P OUTPUT ACCEPT

# === 攻撃シナリオ用ルール ===
# CrewNW → Business NW の通信を許可（c2-server → LOG server）
# CrewNW (via DMZ) → Business NW の通信を許可
iptables -A FORWARD -i $DMZ_IF -o $BIZ_IF -s 192.168.5.0/24 -d 192.168.10.0/24 -j ACCEPT
iptables -A FORWARD -i $BIZ_IF -o $DMZ_IF -m state --state RELATED,ESTABLISHED -j ACCEPT

# Business NW → Navi NW の通信を許可（LOG server → OpenCPN）
iptables -A FORWARD -i $BIZ_IF -o $NAVI_IF -s 192.168.10.0/24 -d 192.168.20.0/24 -j ACCEPT
iptables -A FORWARD -i $NAVI_IF -o $BIZ_IF -m state --state RELATED,ESTABLISHED -j ACCEPT

# Navi NW内部通信の許可（GPS/AIS → OpenCPN）
iptables -A FORWARD -i $NAVI_IF -o $NAVI_IF -s 192.168.20.0/24 -d 192.168.20.0/24 -j ACCEPT

echo "=== FW2 設定完了 ==="
echo "DMZ ($DMZ_IF): 10.254.0.2"
echo "Business NW ($BIZ_IF): 192.168.10.1"
echo "Business NW ($BIZ_IF): 192.168.10.1"
echo "Navi NW ($NAVI_IF): 192.168.20.1"

# デフォルトゲートウェイをFW1(DMZ)に向ける
ip route del default
ip route add default via 10.254.0.1

# ルーティングテーブル表示
ip route

# iptablesルール表示
echo ""
echo "=== iptables FORWARD ルール ==="
iptables -L FORWARD -n -v

# 無限ループで起動を維持
tail -f /dev/null