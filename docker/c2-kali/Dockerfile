FROM kalilinux/kali-rolling:latest

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    kali-linux-headless \
    iputils-ping \
    iproute2 \
    net-tools \
    vim \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ttydのインストール (バイナリから)
RUN curl -L https://github.com/tsl0922/ttyd/releases/download/1.7.7/ttyd.x86_64 -o /usr/bin/ttyd \
    && chmod +x /usr/bin/ttyd

EXPOSE 7681

# エントリーポイントスクリプト設定
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

WORKDIR /root

CMD ["/entrypoint.sh"]