# ────────────────────────────────────────────────
# nginx:alpine ベースの軽量静的ファイルサーバー
# ・Node.js / npm / ビルドステップは一切不要
# ・entrypoint.sh が環境変数を sed で index.html に注入する
# ────────────────────────────────────────────────
FROM nginx:alpine

# iproute2 を追加（ip route コマンドに必要）
RUN apk add --no-cache iproute2

# Nginx 設定を配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 静的ファイルを配置
COPY index.html /usr/share/nginx/html/index.html
COPY style.css  /usr/share/nginx/html/style.css

# エントリポイントスクリプトを配置して実行権限を付与
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 80

ENTRYPOINT ["/entrypoint.sh"]
