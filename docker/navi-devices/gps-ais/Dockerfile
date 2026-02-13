FROM python:3.12-slim

# GPS/AIS シミュレータ

RUN apt-get update && apt-get install -y \
    iputils-ping \
    iproute2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

CMD ["python3", "/app/gps_ais_simulator.py"]
