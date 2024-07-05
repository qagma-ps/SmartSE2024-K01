# LINE_Ambient_send.py
# coding: utf-8

# 熱中症(heatstroke)
# 暑さ指数(WBGT)
# 気温は英語でtemperatureですが、「℃(度)」と具体的に温度を表現したいときは「degree」を使います。
# 複数形の"s"も忘れないようにつけましょう。

# Ambientチャネル
channelId = 12345
channelId_geo = 12345
writeKey = "XXX"
writeKey_geo = "XXXX"

# LINE
token = "XXXXX"
msg = "厳重警戒レベル(暑さ指数WBGT値=30℃)"

# ■モジュールのインストールコマンド
# pi$ sudo pip install git+https://github.com/AmbientDataInc/ambient-python-lib.git
# ■(参考)今インストールされているパッケージを requirements.txt に書き出すコマンド
# pi$ pip freeze | grep ambient
# ambient==0.1.0

import csv

# Ambient送信関数
import ambient


def send_ambient(channelId, writeKey, data):
    ambi = ambient.Ambient(channelId, writeKey)
    r = ambi.send(data)


def convert_format_ambient(file_path):
    data = []
    with open(file_path, mode="rb") as file:
        file_content = file.read().replace(b"\x00", b"")  # Remove null bytes
        file_content = file_content.decode("utf-8").splitlines()

        csv_reader = csv.DictReader(file_content)

        for row in csv_reader:
            # Handle potential missing or invalid data
            try:
                created = row["Timestamp"]
                d1 = float(row["Temperature"])
                d2 = float(row["Humidity"])
                data.append({"created": created, "d1": d1, "d2": d2})
            except (ValueError, TypeError):
                # Skip rows with invalid data
                continue
    return data


def convert_geo_format_ambient(file_path_geo):
    data_geo = []
    with open(file_path_geo, mode="rb") as file:
        file_content = file.read().replace(b"\x00", b"")  # Remove null bytes
        file_content = file_content.decode("utf-8").splitlines()

        csv_reader = csv.DictReader(file_content)

        for row in csv_reader:
            # Handle potential missing or invalid data
            try:
                created = row["Timestamp"]
                lat = float(row["Latitude"])
                lng = float(row["Longitude"])
                data_geo.append(
                    {"created": created, "d1": 0, "d2": 0, "lat": lat, "lng": lng}
                )
            except (ValueError, TypeError):
                # Skip rows with invalid data
                continue
    return data_geo


# LINEメッセージ送信関数
import requests


def send_line_message(msg):
    url = "https://notify-api.line.me/api/notify"
    headers = {"Authorization": "Bearer " + token}
    message = msg
    payload = {"message": message}
    r = requests.post(url, headers=headers, params=payload)
    print(r)


# usage
if __name__ == "__main__":
    # file_path = '/home/pi/Documents/20240629K01/temp_data.csv'
    file_path_geo = "/home/pi/Documents/20240629K01/geo_data.csv"
    # converted_data = convert_format_ambient(file_path)
    converted_data_geo = convert_geo_format_ambient(file_path_geo)
    print(converted_data_geo[0])
    # send_ambient(channelId, writeKey, converted_data)
    send_ambient(channelId_geo, writeKey_geo, converted_data_geo)
# send_line_message(msg)
