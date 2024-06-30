# coding: utf-8

# pip install wiringpi
import time

# DHT11のモジュールをクローンし、本スクリプトと同じ階層にDHT11のフォルダを配置する。
# git clone https://github.com/szazo/DHT11_Python.git
import dht11  # DHT11用モジュールを取り込む
import RPi.GPIO as GPIO
import wiringpi as pi

# initialize GPIO
GPIO.setwarnings(True)
GPIO.setmode(GPIO.BCM)

pi.wiringPiSetupGpio()
sensor = dht11.DHT11(pin=4)

try:
    while True:
        # DHT11を読み取る
        result = sensor.read()
        # 正しく読み取れたら処理する
        if result.is_valid():
            print("Temperature: %d C" % result.temperature)
            print("Humidity: %d %%" % result.humidity)
        # 3秒おきに繰り返す
        time.sleep(3)

except KeyboardInterrupt:
    print("Cleanup")
    GPIO.cleanup()
