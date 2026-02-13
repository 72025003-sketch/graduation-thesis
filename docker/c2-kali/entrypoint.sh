#!/bin/bash
# c2-server エントリーポイント
# ルーティング設定を行ってからttydを起動

# デフォルトゲートウェイは変更せず（DockerのGWのまま）、
# 内部ネットワークへのルーティングを追加する
# 192.168.10.0/24 (Business NW) -> fw2 (192.168.5.254)
# 192.168.20.0/24 (Navi NW)     -> fw2 (192.168.5.254)

ip route add 192.168.10.0/24 via 192.168.5.254
ip route add 192.168.20.0/24 via 192.168.5.254

echo "Routes added for Business NW and Navi NW via FW2"

# ttyd経由でbashを起動
exec ttyd -p 7681 -W bash
