# save_temp_geo_2csv.py

# 必要なモジュールをインストールする。
# pip install wiringpi pyserial
# DHT11のモジュールをクローンし、本スクリプトと同じ階層にDHT11のフォルダを配置する。
# git clone https://github.com/szazo/DHT11_Python.git

import csv
import time

import dht11  # DHT11用モジュールを取り込む
import RPi.GPIO as GPIO
import serial
import wiringpi as pi

# initialize GPIO
GPIO.setwarnings(True)
GPIO.setmode(GPIO.BCM)

pi.wiringPiSetupGpio()
sensor = dht11.DHT11(pin=4)

# CSVファイルの準備
csv_filename_temp = "temp_data.csv"
with open(csv_filename_temp, mode="w", newline="") as csv_file_temp:
    csv_writer_temp = csv.writer(csv_file_temp)
    # ヘッダーの書き込み
    csv_writer_temp.writerow(["Timestamp", "Temperature", "Humidity"])

# CSVファイルの準備
csv_filename = "geo_data.csv"
with open(csv_filename, mode="w", newline="") as csv_file:
    csv_writer = csv.writer(csv_file)
    # ヘッダーの書き込み
    csv_writer.writerow(["Timestamp", "Latitude", "Longitude"])


# 温度と湿度を取得し、コンソールに表示し、CSVファイルに書き込みます。
def save_temp_data():
    # DHT11を読み取る
    result = sensor.read()
    # 正しく読み取れたら処理する
    if result.is_valid():
        timestamp_temp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        print(
            f"Timestamp: {timestamp_temp}, Temperature: {result.temperature} °C, Humidity: {result.humidity} %"
        )

        # CSVファイルに書き込み
        with open(csv_filename_temp, mode="a", newline="") as csv_file_temp:
            csv_writer_temp = csv.writer(csv_file_temp)
            csv_writer_temp.writerow(
                [timestamp_temp, result.temperature, result.humidity]
            )


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
                else:
                    return None, None


# 緯度と経度を取得し、コンソールに表示し、CSVファイルに書き込みます。
# エラー処理とユーザによる中断を考慮しています。
def save_gps_data():
    latitude, longitude = get_gps_data()
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    print(f"Timestamp: {timestamp}, Latitude: {latitude}, Longitude: {longitude}")

    # CSVファイルに書き込み
    with open(csv_filename, mode="a", newline="") as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow([timestamp, latitude, longitude])


if __name__ == "__main__":
    try:
        while True:
            save_temp_data()
            save_gps_data()
            # 適度なインターバルを設定(sec)
            time.sleep(5)

    except KeyboardInterrupt:
        print("Program interrupted by user")
        GPIO.cleanup()
    except Exception as e:
        print(f"Error: {e}")
