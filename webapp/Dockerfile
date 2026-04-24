# ────────────────────────────────────────────────
# nginx:alpine ベースの軽量静的ファイルサーバー
# ────────────────────────────────────────────────
FROM nginx:alpine

# iproute2（ip route）と curl（marked.min.js 取得）を追加
RUN apk add --no-cache iproute2 curl

# marked.min.js をビルド時に取得してローカル同梱（実行時に外部依存なし）
RUN curl -fsSL "https://cdn.jsdelivr.net/npm/marked@13/marked.min.js" \
    -o /usr/share/nginx/html/marked.min.js

# Nginx 設定を配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 静的ファイルを配置
COPY index.html /usr/share/nginx/html/index.html
COPY style.css  /usr/share/nginx/html/style.css

# 攻撃手順ドキュメント（Markdown）を配置
COPY docs/ /usr/share/nginx/html/docs/

# エントリポイントスクリプトを配置して実行権限を付与
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 80

ENTRYPOINT ["/entrypoint.sh"]
