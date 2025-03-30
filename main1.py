import _thread
import time
import os

from micropyserver import MicroPyServer
from machine import Pin, I2C, SPI, PWM
from micropython_sht4x import sht4x
from sdcard import SDCard
import config
import smartplug

from ssd1306 import SSD1306_I2C
from writer import Writer
import tuny

POINT_HUM = 60


# I2C
i2c = I2C(0, sda=Pin(8), scl=Pin(9), freq=100_000)
# sht = sht4x.SHT4X(i2c)
o = SSD1306_I2C(128, 64, i2c)
ssd = Writer(o, tuny)

out_fan = FanControl(0)
out_fan.set_speed(100)
smart = smartplug.SmarkPlugContorl()

server = MicroPyServer()


temp_now = 0
hum_now = 0


def main_page(request):
    server.send(f"Temperature: {temp_now:.2f} °C\nRelative Humidity: {hum_now:.2f} %")


server.add_route("/", main_page)

_thread.start_new_thread(server.start, ())

while True:
    # temp_now, hum_now = sht.measurements
    start = time.ticks_ms()
    if temp_now > config.POINT_TEMP + 1:
        out_fan.set_speed(out_fan.fan_speed + 1)
    elif temp_now < config.POINT_TEMP - 1:
        out_fan.set_speed(out_fan.fan_speed - 1)

    if int(hum_now) == POINT_HUM and not smart.last_status:
        smart.change(False)
    else:
        if hum_now > POINT_HUM + 5:
            smart.change(True)
        elif hum_now < POINT_HUM - 5:
            smart.change(False)

    log(
        f"temp: {temp_now:.2f}C, hum: {hum_now:.2f}% | out_fan speed: {out_fan.fan_speed}"
    )

    o.fill(0)
    ssd.set_textpos(o, 0, 0)
    # ssd.printstring(f"TEMP/avg: {temp_now:.2f}C\n")
    # ssd.printstring(f"HUM/avg:  {hum_now:.2f}%\n")
    ssd.printstring(f"OUT/IN fan speed: {out_fan.fan_speed}%|{in_fan.fan_speed}%\n")
    ssd.printstring(f"mydb size: {os.stat('/sd/db')[6] / 1024} KB\n")
    o.show()

    delay_time = 5 - ((time.ticks_ms() - start) / 1000)
    if delay_time > 0:
        time.sleep(delay_time)
