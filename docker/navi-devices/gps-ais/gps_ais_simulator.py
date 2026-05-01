#!/usr/bin/env python3
"""
GPS/AIS シミュレータ

GPS位置情報とAISメッセージをIEC 61162-450（UDPブロードキャスト）で送信
- 自船: GGA/RMC で GPS 位置を配信
- 他船: !AIVDM (AIS Type 1) で複数の幽霊船を配信
"""

import socket
import time
import math
from datetime import datetime, timezone


# ────────────────────────────────────────────
# NMEA ユーティリティ
# ────────────────────────────────────────────

def nmea_checksum(sentence: str) -> str:
    """$ と * の間の文字列をXORしてチェックサムを返す"""
    checksum = 0
    for ch in sentence:
        checksum ^= ord(ch)
    return f"{checksum:02X}"


# ────────────────────────────────────────────
# GPS センテンス生成
# ────────────────────────────────────────────

def _lat_lon_fields(lat: float, lon: float):
    """緯度・経度をNMEA形式に変換"""
    lat_deg = int(abs(lat))
    lat_min = (abs(lat) - lat_deg) * 60
    lat_str = f"{lat_deg:02d}{lat_min:07.4f}"
    lat_dir = "N" if lat >= 0 else "S"

    lon_deg = int(abs(lon))
    lon_min = (abs(lon) - lon_deg) * 60
    lon_str = f"{lon_deg:03d}{lon_min:07.4f}"
    lon_dir = "E" if lon >= 0 else "W"

    return lat_str, lat_dir, lon_str, lon_dir


def create_gga_sentence(lat: float, lon: float, ts: datetime) -> str:
    """NMEA GGA（GPS Fix Data）センテンスを生成"""
    time_str = ts.strftime("%H%M%S.00")
    lat_str, lat_dir, lon_str, lon_dir = _lat_lon_fields(lat, lon)
    body = f"GPGGA,{time_str},{lat_str},{lat_dir},{lon_str},{lon_dir},1,08,1.0,10.0,M,0.0,M,,"
    return f"${body}*{nmea_checksum(body)}\r\n"


def create_rmc_sentence(lat: float, lon: float, speed: float, course: float, ts: datetime) -> str:
    """NMEA RMC（Recommended Minimum）センテンスを生成"""
    time_str = ts.strftime("%H%M%S.00")
    date_str = ts.strftime("%d%m%y")
    lat_str, lat_dir, lon_str, lon_dir = _lat_lon_fields(lat, lon)
    body = (f"GPRMC,{time_str},A,{lat_str},{lat_dir},{lon_str},{lon_dir},"
            f"{speed:.1f},{course:.1f},{date_str},,,")
    return f"${body}*{nmea_checksum(body)}\r\n"


# ────────────────────────────────────────────
# AIS エンコーダー
# ────────────────────────────────────────────

def _int_to_bits(value: int, width: int, signed: bool = False) -> str:
    """整数を指定ビット幅のビット文字列に変換（符号付き対応）"""
    if signed and value < 0:
        value = value + (1 << width)
    return format(value & ((1 << width) - 1), f"0{width}b")


def _bits_to_armored(bits: str) -> tuple[str, int]:
    """
    ビット文字列をAISアーマードASCIIに変換
    戻り値: (payload文字列, fill_bits数)
    """
    # 6の倍数になるようにゼロパディング
    fill_bits = (6 - len(bits) % 6) % 6
    bits = bits + "0" * fill_bits

    payload = ""
    for i in range(0, len(bits), 6):
        val = int(bits[i:i + 6], 2) + 48
        if val > 87:
            val += 8
        payload += chr(val)
    return payload, fill_bits


def create_ais_type1(mmsi: int, lat: float, lon: float,
                     speed: float, course: float) -> str:
    """
    AIS Message Type 1（Position Report Class A）の !AIVDM センテンスを生成

    Parameters
    ----------
    mmsi   : 9桁のMMSI番号
    lat    : 緯度（度）
    lon    : 経度（度）
    speed  : 対地速力（ノット）
    course : 対地針路（度）
    """
    bits = ""
    bits += _int_to_bits(1, 6)                    # Message Type = 1
    bits += _int_to_bits(0, 2)                    # Repeat Indicator
    bits += _int_to_bits(mmsi, 30)                # MMSI
    bits += _int_to_bits(0, 4)                    # Nav Status: underway engine
    bits += _int_to_bits(-128, 8, signed=True)    # Rate of Turn: N/A
    bits += _int_to_bits(int(speed * 10), 10)     # SOG: 1/10 knot
    bits += _int_to_bits(0, 1)                    # Position Accuracy: low

    # 経度: 1/10000分（符号付き28ビット）
    lon_raw = round(lon * 600000)
    bits += _int_to_bits(lon_raw, 28, signed=True)

    # 緯度: 1/10000分（符号付き27ビット）
    lat_raw = round(lat * 600000)
    bits += _int_to_bits(lat_raw, 27, signed=True)

    bits += _int_to_bits(int(course * 10) % 3600, 12)  # COG: 1/10 degree
    bits += _int_to_bits(511, 9)                        # True Heading: N/A
    bits += _int_to_bits(60, 6)                         # Time Stamp: N/A
    bits += _int_to_bits(0, 2)                          # Maneuver Indicator
    bits += _int_to_bits(0, 3)                          # Spare
    bits += _int_to_bits(0, 1)                          # RAIM flag
    bits += _int_to_bits(0, 19)                         # Radio status

    payload, fill_bits = _bits_to_armored(bits)
    body = f"AIVDM,1,1,,A,{payload},{fill_bits}"
    return f"!{body}*{nmea_checksum(body)}\r\n"


# ────────────────────────────────────────────
# 幽霊船（Ghost Ships）定義
# ────────────────────────────────────────────

GHOST_SHIPS = [
    {
        "name":   "GHOST MARU 1",
        "mmsi":   123456001,
        "lat":    35.62,
        "lon":    139.78,
        "speed":  8.0,
        "course": 045.0,
        "orbit_r": 0.005,   # 円運動の半径（度）
        "orbit_w": 0.02,    # 角速度
    },
    {
        "name":   "GHOST MARU 2",
        "mmsi":   123456002,
        "lat":    35.58,
        "lon":    139.82,
        "speed":  14.0,
        "course": 180.0,
        "orbit_r": 0.008,
        "orbit_w": -0.015,
    },
    {
        "name":   "GHOST MARU 3",
        "mmsi":   123456003,
        "lat":    35.60,
        "lon":    139.75,
        "speed":  6.5,
        "course": 270.0,
        "orbit_r": 0.003,
        "orbit_w": 0.03,
    },
    {
        "name":   "SPOOFED TANKER",
        "mmsi":   987654321,
        "lat":    35.65,
        "lon":    139.80,
        "speed":  0.5,   # ほぼ停止（錨泊偽装）
        "course": 000.0,
        "orbit_r": 0.001,
        "orbit_w": 0.005,
    },
]


def get_ghost_position(ship: dict, t: int) -> tuple[float, float, float, float]:
    """時刻インデックスtに基づいて幽霊船の現在位置を計算"""
    lat = ship["lat"] + ship["orbit_r"] * math.sin(t * ship["orbit_w"])
    lon = ship["lon"] + ship["orbit_r"] * math.cos(t * ship["orbit_w"])
    # 速度・針路に±の揺らぎを加える
    speed  = ship["speed"]  + 0.5 * math.sin(t * 0.07)
    course = ship["course"] + 3.0 * math.cos(t * 0.05)
    course = course % 360
    return lat, lon, speed, course


# ────────────────────────────────────────────
# メインループ
# ────────────────────────────────────────────

def simulate_voyage():
    """自船GPS + 複数幽霊船AISをブロードキャスト"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    target_ip   = "192.168.20.255"
    target_port = 10110

    print("=" * 48)
    print("  GPS/AIS シミュレータ起動")
    print("=" * 48)
    print(f"  送信先 : {target_ip}:{target_port}")
    print(f"  自船   : 東京湾 (35.60°N, 139.80°E)")
    print(f"  幽霊船 : {len(GHOST_SHIPS)} 隻")
    print("=" * 48)
    print()

    # 自船初期値
    base_lat   = 35.60
    base_lon   = 139.80
    own_speed  = 12.0
    own_course = 200.0

    t = 0
    try:
        while True:
            ts = datetime.now(timezone.utc)

            # ── 自船 GPS ──
            lat = base_lat + 0.0001 * math.sin(t * 0.01)
            lon = base_lon + 0.0001 * math.cos(t * 0.01)
            speed  = own_speed  + 2.0 * math.sin(t * 0.05)
            course = own_course + 5.0 * math.cos(t * 0.03)

            for sentence in [
                create_gga_sentence(lat, lon, ts),
                create_rmc_sentence(lat, lon, speed, course, ts),
            ]:
                sock.sendto(sentence.encode("ascii"), (target_ip, target_port))

            # ── 幽霊船 AIS (Type 1) ──
            for ship in GHOST_SHIPS:
                g_lat, g_lon, g_spd, g_crs = get_ghost_position(ship, t)
                ais = create_ais_type1(ship["mmsi"], g_lat, g_lon, g_spd, g_crs)
                sock.sendto(ais.encode("ascii"), (target_ip, target_port))

            # ── ログ出力（10秒ごと）──
            if t % 10 == 0:
                print(f"[{ts.strftime('%H:%M:%S')} UTC]  自船: {lat:.5f}°N {lon:.5f}°E"
                      f"  {speed:.1f}kt  {course:.0f}°")
                for ship in GHOST_SHIPS:
                    g_lat, g_lon, g_spd, g_crs = get_ghost_position(ship, t)
                    print(f"  └─ {ship['name']:20s} MMSI={ship['mmsi']}"
                          f"  {g_lat:.5f}°N {g_lon:.5f}°E"
                          f"  {g_spd:.1f}kt  {g_crs:.0f}°")
                print()

            t += 1
            time.sleep(1.0)

    except KeyboardInterrupt:
        print("\nシミュレータを停止しました")
    finally:
        sock.close()


if __name__ == "__main__":
    simulate_voyage()
