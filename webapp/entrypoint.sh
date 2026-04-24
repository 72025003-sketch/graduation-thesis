#!/bin/sh
# entrypoint.sh
# 1. 静的ルーティング設定（NET_ADMIN が必要）
# 2. 環境変数を sed でプレースホルダーに注入
# 3. Nginx 起動
set -e

# ── ルーティング設定 ──────────────────────────────────────
# Navi NW (192.168.20.0/24) への静的ルート追加
# すでにルートが存在する場合はエラーを無視して続行
ip route add 192.168.20.0/24 via 192.168.10.1 2>/dev/null || true

# ── 環境変数のデフォルト値 ───────────────────────────────
OPENCPN_URL="${OPENCPN_URL:-http://localhost:6080/vnc.html?autoconnect=true&resize=scale}"
C2_URL="${C2_URL:-http://localhost:7681}"

# ── プレースホルダー置換 ─────────────────────────────────
# NOTE: | を区切り文字にすることで URL 内の / のエスケープ不要
sed -i "s|__OPENCPN_URL__|${OPENCPN_URL}|g" /usr/share/nginx/html/index.html
sed -i "s|__C2_URL__|${C2_URL}|g" /usr/share/nginx/html/index.html

# ── Nginx をフォアグラウンドで起動 ───────────────────────
exec nginx -g 'daemon off;'
