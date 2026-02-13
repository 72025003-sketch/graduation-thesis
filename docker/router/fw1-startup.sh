#!/bin/sh
# FW1 起動スクリプト
# Internet ⟷ CrewNW のルーティングとNAT設定

echo "=== FW1 起動中 ==="

# インターフェースの自動特定
WAN_IF=$(ip -4 addr show | grep '192.168.1.254' | awk '{print $NF}')
LAN_IF=$(ip -4 addr show | grep '192.168.5.1' | awk '{print $NF}')

echo "FW1 Detected: WAN=$WAN_IF, LAN=$LAN_IF"

# IPフォワーディング有効化
sysctl -w net.ipv4.ip_forward=1

# iptablesのデフォルトポリシー設定
iptables -P FORWARD DROP
iptables -P INPUT ACCEPT
iptables -P OUTPUT ACCEPT

# NAT設定（CrewNW → Internet）
iptables -t nat -A POSTROUTING -s 192.168.5.0/24 -o $WAN_IF -j MASQUERADE

# CrewNW → Internet の通信を許可
iptables -A FORWARD -i $LAN_IF -o $WAN_IF -s 192.168.5.0/24 -j ACCEPT
iptables -A FORWARD -i $WAN_IF -o $LAN_IF -m state --state RELATED,ESTABLISHED -j ACCEPT

echo "=== FW1 設定完了 ==="
echo "Internet ($WAN_IF): 192.168.1.254"
echo "CrewNW ($LAN_IF): 192.168.5.1"

# 内部ネットワークへのルーティング (to FW2)
ip route add 192.168.10.0/24 via 192.168.5.254
ip route add 192.168.20.0/24 via 192.168.5.254

# ルーティングテーブル表示
ip route

# 無限ループで起動を維持
tail -f /dev/null
