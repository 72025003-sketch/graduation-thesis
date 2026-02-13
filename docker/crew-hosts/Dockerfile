FROM ubuntu:22.04

# CrewNW用ホスト（crew-pc）
# 一般的な乗組員PC

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    iputils-ping \
    iproute2 \
    net-tools \
    curl \
    wget \
    vim \
    && rm -rf /var/lib/apt/lists/*

CMD ["/bin/bash"]
