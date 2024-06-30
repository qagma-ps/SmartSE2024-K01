# GPS_latitude_longitude_get.py

# 「L76K GPS Module」と「Raspberry Pi 4 Model B」を使って、緯度、経度を取得します。
# コンソールに表示し、CSVファイルに書き込みます。

# serialライブラリを使用して、「GPS Module」と通信し、
# 「NMEA(エヌエムイーエー)プロトコル」(=シリアル通信プロトコル)に従って位置データを解析します。

# Raspberry Piのシリアルポートが正しく設定されていることを確認してください。

# まず、必要なライブラリをインストールします。pyserial ライブラリを使用するので、
# 以下のコマンドをターミナルで実行してください。
# pip install pyserial

import csv
import time

import serial


# Parse the GNGGA sentence to extract the latitude and longitude.
# GNGGA文を解析して、緯度と経度を抽出します。
def parse_gngga(sentence):

    parts = sentence.split(",")

    if parts[0] != "$GNGGA":
        return None, None

    try:
        lat = float(parts[2])
        lat_dir = parts[3]
        lon = float(parts[4])
        lon_dir = parts[5]

        # Convert latitude and longitude to decimal degrees
        # 緯度と経度を度分表記から10進数表記に変換します。
        lat_dd = int(lat / 100) + (lat % 100) / 60.0
        lon_dd = int(lon / 100) + (lon % 100) / 60.0

        if lat_dir == "S":
            lat_dd = -lat_dd
        if lon_dir == "W":
            lon_dd = -lon_dd

        return lat_dd, lon_dd
    except (ValueError, IndexError):
        return None, None


# Read the GPS data from the serial port and extract the latitude and longitude.
# シリアルポートからデータを読み取り、GNGGA文が見つかった場合に解析して緯度と経度を取得します。
# デフォルトでは、Raspberry Piのシリアルポート/dev/ttyS0を使用します。
def get_gps_data(serial_port="/dev/ttyS0", baud_rate=9600, timeout=1):

    with serial.Serial(serial_port, baud_rate, timeout=timeout) as ser:
        while True:
            line = ser.readline().decode("ascii", errors="replace")
            if "$GNGGA" in line:
                lat, lon = parse_gngga(line)
                if lat is not None and lon is not None:
                    return lat, lon


# メインプログラム
# 緯度と経度を取得し、コンソールに表示し、CSVファイルに書き込みます。
# エラー処理とユーザによる中断を考慮しています。
if __name__ == "__main__":
    # CSVファイルの準備
    csv_filename = "gps_data.csv"
    with open(csv_filename, mode="w", newline="") as csv_file:
        csv_writer = csv.writer(csv_file)
        # ヘッダーの書き込み
        csv_writer.writerow(["Timestamp", "Latitude", "Longitude"])

    try:
        while True:
            latitude, longitude = get_gps_data()
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
            print(
                f"Timestamp: {timestamp}, Latitude: {latitude}, Longitude: {longitude}"
            )

            # CSVファイルに書き込み
            with open(csv_filename, mode="a", newline="") as csv_file:
                csv_writer = csv.writer(csv_file)
                csv_writer.writerow([timestamp, latitude, longitude])

            # 適度なインターバルを設定(sec)
            time.sleep(1)

    except KeyboardInterrupt:
        print("Program interrupted by user")
    except Exception as e:
        print(f"Error: {e}")
