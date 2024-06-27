# coding: utf-8

import wiringpi as pi
import time
import dht11 # DHT11用モジュールを取り込む

pi.wiringPiSetupGpio()
sensor = dht11.DHT11(pin=4)

while True:
    # DHT11を読み取る
    result = sensor.read()
    # 正しく読み取れたら処理する
    if result.is_valid():
        print("Temperature: %d C" % result.temperature)
        print("Humidity: %d %%" % result.humidity)
    # 3秒おきに繰り返す
    time.sleep(3)
