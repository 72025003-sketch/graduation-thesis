FROM ubuntu:latest

RUN apt-get update \
&&  apt-get install -y software-properties-common \
&&  add-apt-repository --yes ppa:opencpn/opencpn \
&&  apt-get update \
&&  apt-get install -y \
    opencpn \
    x11vnc \
    xvfb \
    fluxbox \
    novnc \
    websockify \
    net-tools \
    supervisor \
    iproute2 \
&&  rm -rf /var/cache/apt/archives/* /var/lib/apt/lists/*

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