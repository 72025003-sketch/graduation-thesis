FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    opencpn \
 && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y --no-install-recommends \
    x11vnc \
    xvfb \
    fluxbox \
    novnc \
    websockify \
    net-tools \
    supervisor \
    iproute2 \
 && rm -rf /var/lib/apt/lists/*

# noVNC用のリンク作成
RUN ln -s /usr/share/novnc/vnc.html /usr/share/novnc/index.html

# Supervisor設定
RUN mkdir -p /var/log/supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# 画面解像度設定
ENV DISPLAY=:0
ENV RESOLUTION=1280x800x24

EXPOSE 6080

# エントリーポイントスクリプト設定
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# OpenCPN設定ファイル (configディレクトリ) のコピー
RUN mkdir -p /root/.opencpn
COPY config/ /root/.opencpn/

CMD ["/entrypoint.sh"]