#!/usr/bin/python3
# coding: utf-8
# read_csv.py

# CSVファイルを読み込む。
# [温度湿度について]
#   1.温度湿度から暑さ指数(WBGT)を求め、その基準域 range を求める。
#   2.Ambient へ温度湿度データを送信する。
#   3.基準域 range が変化したら、LINEへメッセージ送信する。
# [緯度経度について]
#   1.緯度経度から距離を求める。
#   2.距離 distance_m が変化していないなら、LINEへメッセージ送信する。

# Ambientチャネル
channelId = 12345
channelId_geo = 12345
writeKey = "XXX"
writeKey_geo = "XXX"
channelUrl = "https://ambidata.io/bd/board.html?id=XXXX"
channelUrl_geo = "https://ambidata.io/bd/board.html?id=XXX"
# LINE
token = "XXX"


import sys
import csv
import time
from LINE_Ambient_send import send_line_message
# pip install geopy
from geopy.distance import geodesic

# これは室内用の指標です。屋外では使えません！
# 室内用のWBGT簡易推定図
# 日本生気象学会：日常生活における熱中症予防指針Ver.4, 2022.5
# https://seikishou.jp/cms/wp-content/uploads/008ab7fdbb0b958314827de9a7b8c74c.pdf
# 上から下へ乾球温度21, 22,..., 40degree,  index 0-19
# 左から右へ相対湿度20, 25,..., 100%RH,    index 0-16
WBGT=[
    [14,14,15,15,16,16,17,17,18,18,19,19,19,20,20,21,21],
    [15,15,16,16,17,17,18,18,19,19,20,20,20,21,21,22,22],
    [15,16,16,17,18,18,19,19,20,20,20,21,21,22,22,23,23],
    [16,17,17,18,18,19,19,20,20,21,21,22,22,23,23,24,24],
    [17,17,18,19,19,20,20,21,21,22,22,23,23,24,24,25,25],
    [18,18,19,20,20,21,21,22,22,23,23,24,24,25,25,26,26],
    [18,19,20,20,21,22,22,23,23,24,24,25,25,26,26,27,27],
    [19,20,21,21,22,22,23,24,24,25,25,26,26,27,27,28,28],
    [20,21,21,22,23,23,24,24,25,26,26,27,27,28,28,29,29],
    [21,21,22,23,23,24,25,25,26,26,27,28,28,29,29,30,30],
    [21,22,23,24,24,25,26,26,27,27,28,29,29,30,30,31,31],
    [22,23,24,24,25,26,26,27,28,28,29,29,30,31,31,32,32],
    [23,24,25,25,26,27,27,28,29,29,30,30,31,31,32,33,33],
    [24,25,25,26,27,28,28,29,30,30,31,31,32,32,33,34,34],
    [24,25,26,27,28,28,29,30,30,31,32,32,33,33,34,34,35],
    [25,26,27,28,29,29,30,31,31,32,33,33,34,34,35,35,36],
    [26,27,28,29,29,30,31,32,32,33,34,34,35,35,36,36,37],
    [27,28,29,29,30,31,32,33,33,34,35,35,36,36,37,37,38],
    [27,28,29,30,31,32,33,33,34,35,35,36,37,37,38,38,39],
    [28,29,30,31,32,33,34,34,35,36,36,37,38,38,39,39,40]
]

# 室内の暑さ指数(WBGT)を求める関数
def wbgt(temp, humid):
    try:
        # 小数点以下を四捨五入
        t = round(float(temp)-21)
        h = round((float(humid)-20)/5)
        # 小数点以下を切り上げ
        # t = math.ceil(float(temp)-21)
        # h = math.ceil((float(humid)-20)/5)
    except ValueError:
        t = 99
    if 0 <= t <= 19 and 0 <= h <= 16:
        wbgt_value = WBGT[t][h]
    else:
        wbgt_value = 99 #温湿度の範囲を外れると99[℃]を返す
    return wbgt_value

# 暑さ指数(WBGT)から基準域を返す関数
def wbgt_range(wbgt_value):
    if wbgt_value == 99:
        # print("Out of range. Should be in 21-40 degree, 20-100 %RH")
        print("暑さ指数は範囲外です(21-40℃,20-100%RH)")
    else:
        range = ""
        if wbgt_value < 25:
            range = "注意"
        if 25 <= wbgt_value < 28:
            range = "警戒"
        if 28 <= wbgt_value < 31:
            range = "厳重警戒"
        if 31 <= wbgt_value:
            range = "危険"
        print("{}レベル(暑さ指数WBGT値{}℃)".format(range, wbgt_value))
    return range

# main()関数
if __name__ == "__main__":
    range_old = ""                    # 空文字で変数初期化
    geo_old = ()
    while True:
        try:
            # CSVファイルから1行ずつ読み込む（温度湿度）
            with open('temp_data.csv', 'r') as file:
                csv_reader = csv.reader(file)
                rows = list(csv_reader)
                if rows:
                    last_row = rows[-1]
                    temp = last_row[1]
                    humid = last_row[2]
                    # 室内の暑さ指数(WBGT)を求める
                    wbgt_value = wbgt(temp, humid)
                    # 暑さ指数(WBGT)から基準域を返す
                    range = wbgt_range(wbgt_value)
                    if 10 <= wbgt_value:
                        msg = "{}! 気温が警戒レベル(WBGT値: {})になりました。\n温度: {}℃ 湿度: {}%\n見守り人の安全に気を付けてください。\n{}".format(range, wbgt_value, temp, humid, channelUrl)
                        send_line_message(msg)
                    # LINEメッセージ送信
                    # range が変化したら通知
                    #if range_old != range
                    #    message = range + "レベル(暑さ指数WBGT値" + wbgt_value + "℃)"
                    #    send_line_message(token, message)
                    #    range_old = range

            # CSVファイルから1行ずつ読み込む（緯度経度）
            with open('geo_data.csv', 'r') as file:
                if not geo_old :
                    geo_old = (36.00439983333333, 139.5749805)
                csv_reader = csv.reader(file)
                rows = list(csv_reader)
                if rows:
                    last_row = rows[-1]
                    lat = last_row[1]
                    lng = last_row[2]
                # 経度緯度セット
                if len(rows) > 60:
                    target_row = rows[-61]
                    lat_target = target_row[1]
                    lng_target = target_row[2]
                else:
                    print("The target row does not have enough columns.")
                geo = (lat, lng)
                geo_target = (lat_target, lng_target)
                # 距離計算(メートル)
                distance_m = geodesic(geo, geo_target).m
                distance_m_old = geodesic(geo, geo_old).m
                # 距離 distance_m が変化していないなら通知
                if distance_m > 1:
                    if distance_m_old > 1:
                        msg = "5分間動いていません！\n緯度: {} 経度: {}\n見守り人が安全な場所にいるか確認してください。\n{}".format(lat, lng, channelUrl_geo)
                        print("{} m".format(distance_m))
                        send_line_message(msg)
                        geo_old = geo
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        time.sleep(300)
