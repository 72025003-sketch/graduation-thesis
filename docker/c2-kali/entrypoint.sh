#!/bin/bash
# c2-server エントリーポイント
# ルーティング設定を行ってからttydを起動

# デフォルトゲートウェイはDockerのままにする (外部アクセス用)
# 内部ネットワークへのルーティングをFW1 (192.168.5.1) 経由で追加
ip route add 192.168.10.0/24 via 192.168.5.1
ip route add 192.168.20.0/24 via 192.168.5.1
ip route add 10.254.0.0/24 via 192.168.5.1

echo "Added static routes to Business/Navi/DMZ via FW1 (192.168.5.1)"

# ttyd経由でbashを起動
exec ttyd -p 7681 -W bash
