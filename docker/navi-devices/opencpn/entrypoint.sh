#!/bin/bash
# OpenCPN エントリーポイント
# ルーティング設定を行ってからSupervisorを起動

# デフォルトゲートウェイは変更せず（DockerのGWのまま）、
# 内部ネットワークへのルーティングを追加する
# 192.168.5.0/24 (CrewNW) -> fw2 (192.168.20.1)
# 192.168.10.0/24 (Business NW) -> fw2 (192.168.20.1)

ip route add 192.168.5.0/24 via 192.168.20.1
ip route add 192.168.10.0/24 via 192.168.20.1

echo "Routes added for CrewNW and Business NW via FW2"

# Supervisor起動
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
