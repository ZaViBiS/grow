import json
import _thread
import time
import gc

from machine import Pin, I2C, reset
from micropython_sht4x import sht4x

from fan_control import FanControl
from database import Database
import utils

smd = utils.SendMissedData()


def main_loop():
    # I2C
    i2c = I2C(0, sda=Pin(8), scl=Pin(9), freq=100000)
    sht = sht4x.SHT4X(i2c)

    out_fan = FanControl(1)
    out_fan.set_speed(0)

    points = utils.Points()
    db = Database()

    points.update_data_in_class()
    while True:
        datafor = []
        for _ in range(6):
            start = time.time()
            temp, hum = sht.measurements
            vpd = utils.vpd_calculator(temp, hum)

            if temp > points.POINT_TEMP + 0.1:
                out_fan.set_speed(out_fan.fan_speed + 1)
            elif temp < points.POINT_TEMP - 0.1:
                out_fan.set_speed(out_fan.fan_speed - 1)

            datafor.append([temp, hum, vpd, out_fan.fan_speed])

            gc.collect()

            time.sleep(10 - (time.time() - start))

        data = {
            "time": utils.get_unix_time_now(),
            "temp": 0,
            "hum": 0,
            "fan_speed": 0,
            "vpd": 0,
        }
        for d in datafor:
            data["temp"] += d[0]
            data["hum"] += d[1]
            data["vpd"] += d[2]
            data["fan_speed"] += d[3]
        data["temp"] = data["temp"] / 6
        data["hum"] = data["hum"] / 6
        data["vpd"] = data["vpd"] / 6
        data["fan_speed"] = data["fan_speed"] / 6

        try:
            if not db.put(data):
                raise

        except Exception as e:
            utils.log(f"error in data sending: {e}")
            smd.queue.append(data)
            if not sta_if.isconnected():
                reset()


try:
    _thread.start_new_thread(smd.send_missed_data, ())
    main_loop()
except Exception as e:
    utils.log(e)
    reset()
