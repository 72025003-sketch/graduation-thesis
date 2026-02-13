FROM alpine:latest

RUN apk add --no-cache \
    iptables \
    ip6tables \
    iproute2 \
    tcpdump \
    bash

# IPフォワーディングを有効化
RUN echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf

COPY fw1-startup.sh /fw1-startup.sh
COPY fw2-startup.sh /fw2-startup.sh
RUN chmod +x /fw1-startup.sh /fw2-startup.sh

CMD ["/bin/sh", "-c", "sysctl -w net.ipv4.ip_forward=1 && tail -f /dev/null"]
