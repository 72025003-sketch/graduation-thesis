FROM ubuntu:22.04

# LOG server
# 脆弱なSSH設定 + NMEA送信機能

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    openssh-server \
    python3 \
    python3-pip \
    rsyslog \
    iputils-ping \
    iproute2 \
    net-tools \
    tcpdump \
    netcat \
    vim \
    && rm -rf /var/lib/apt/lists/*

# SSHディレクトリ作成
RUN mkdir /var/run/sshd

# Pythonライブラリ追加
RUN pip3 install pynmea2

# Pythonスクリプトコピー
COPY inject_nmea.py /home/admin/inject_nmea.py

# 初期化スクリプトコピー
COPY setup_ssh.sh /setup_ssh.sh
RUN chmod +x /setup_ssh.sh

# SSH設定（パスワード認証を許可）
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin no/' /etc/ssh/sshd_config && \
    sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config

# rsyslog設定
RUN echo '$ModLoad imudp\n$UDPServerRun 514' >> /etc/rsyslog.conf

EXPOSE 22 514/udp

CMD ["/bin/bash"]
