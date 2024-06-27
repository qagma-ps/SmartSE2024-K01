# LINE_Ambient_send.py
# coding: utf-8

# 熱中症(heatstroke)
# 暑さ指数(WBGT)
# 気温は英語でtemperatureですが、「℃(度)」と具体的に温度を表現したいときは「degree」を使います。
# 複数形の"s"も忘れないようにつけましょう。

# Ambientチャネル名「k01_team5_チャネル」
channelId = 79809
writeKey = b658c06ea738afef

# LINE
token = Zb3WbcdSec1YnQjr2JEM7KzO2Vc93C6lUFj2O6d1sVQ
message = "厳重警戒レベル(暑さ指数WBGT値=30℃)"

# 温度、湿度、暑さ指数(WBGT)
temp = 30.0
humid = 70.0
wbgt = 27

# ■モジュールのインストールコマンド
# pi$ sudo pip install git+https://github.com/AmbientDataInc/ambient-python-lib.git
# ■(参考)今インストールされているパッケージを requirements.txt に書き出すコマンド
# pi$ pip freeze | grep ambient
# ambient==0.1.0

# Ambient送信関数
import ambient
def send_ambient(channelId, writeKey, temp, humid):
    ambi = ambient.Ambient(channelId, writeKey)
    r = ambi.send({'d1': temp, 'd2': humid})

# LINEメッセージ送信関数
import requests
def send_line_message(token, message):
    url = "https://notify-api.line.me/api/notify" 
    token = (token)
    headers = {"Authorization" : "Bearer" + token}
    message = (message)
    payload = {"message" : message} 
    r = requests.post(url, headers = headers, params = payload)

