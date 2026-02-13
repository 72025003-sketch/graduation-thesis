#!/usr/bin/env python3
"""
GPS/AIS シミュレータ

GPS位置情報とAISメッセージをIEC 61162-450（UDPマルチキャスト）で送信
"""

import socket
import time
import math
from datetime import datetime

def calculate_checksum(sentence):
    """NMEAチェックサムを計算"""
    checksum = 0
    for char in sentence:
        checksum ^= ord(char)
    return f"{checksum:02X}"

def create_gga_sentence(lat, lon, timestamp):
    """NMEA GGA（GPS Fix Data）センテンスを生成"""
    time_str = timestamp.strftime('%H%M%S.00')
    
    lat_deg = int(abs(lat))
    lat_min = (abs(lat) - lat_deg) * 60
    lat_str = f"{lat_deg:02d}{lat_min:07.4f}"
    lat_dir = 'N' if lat >= 0 else 'S'
    
    lon_deg = int(abs(lon))
    lon_min = (abs(lon) - lon_deg) * 60
    lon_str = f"{lon_deg:03d}{lon_min:07.4f}"
    lon_dir = 'E' if lon >= 0 else 'W'
    
    sentence = f"GPGGA,{time_str},{lat_str},{lat_dir},{lon_str},{lon_dir},1,08,1.0,10.0,M,0.0,M,,"
    checksum = calculate_checksum(sentence)
    
    return f"${sentence}*{checksum}\r\n"

def create_rmc_sentence(lat, lon, speed, course, timestamp):
    """NMEA RMC（Recommended Minimum）センテンスを生成"""
    time_str = timestamp.strftime('%H%M%S.00')
    date_str = timestamp.strftime('%d%m%y')
    
    lat_deg = int(abs(lat))
    lat_min = (abs(lat) - lat_deg) * 60
    lat_str = f"{lat_deg:02d}{lat_min:07.4f}"
    lat_dir = 'N' if lat >= 0 else 'S'
    
    lon_deg = int(abs(lon))
    lon_min = (abs(lon) - lon_deg) * 60
    lon_str = f"{lon_deg:03d}{lon_min:07.4f}"
    lon_dir = 'E' if lon >= 0 else 'W'
    
    sentence = f"GPRMC,{time_str},A,{lat_str},{lat_dir},{lon_str},{lon_dir},{speed:.1f},{course:.1f},{date_str},,,"
    checksum = calculate_checksum(sentence)
    
    return f"${sentence}*{checksum}\r\n"

def simulate_voyage():
    """仮想航海をシミュレート"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    
    target_ip = "192.168.20.255"
    target_port = 60001
    
    print("========================================")
    print("GPS/AIS シミュレータ起動")
    print("========================================")
    print(f"送信先: {target_ip}:{target_port}")
    print(f"初期位置: 東京湾（35.6°N, 139.8°E）")
    print("")
    
    base_lat = 35.6
    base_lon = 139.8
    speed_knots = 12.0
    course = 200.0
    
    iteration = 0
    
    try:
        while True:
            timestamp = datetime.utcnow()
            
            lat = base_lat + 0.0001 * math.sin(iteration * 0.01)
            lon = base_lon + 0.0001 * math.cos(iteration * 0.01)
            speed = speed_knots + 2.0 * math.sin(iteration * 0.05)
            current_course = course + 5.0 * math.cos(iteration * 0.03)
            
            gga = create_gga_sentence(lat, lon, timestamp)
            rmc = create_rmc_sentence(lat, lon, speed, current_course, timestamp)
            
            sock.sendto(gga.encode('ascii'), (target_ip, target_port))
            sock.sendto(rmc.encode('ascii'), (target_ip, target_port))
            
            if iteration % 10 == 0:
                print(f"[{timestamp.strftime('%H:%M:%S')}] 位置: {lat:.6f}°N, {lon:.6f}°E | "
                      f"速度: {speed:.1f}kt | 針路: {current_course:.1f}°")
            
            iteration += 1
            time.sleep(1.0)
            
    except KeyboardInterrupt:
        print("\nGPS/AIS シミュレータを停止しました")
    finally:
        sock.close()

if __name__ == '__main__':
    simulate_voyage()
