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
        start = time.time()
        unixtime = utils.get_unix_time_now(start)
        temp, hum = sht.measurements
        vpd = utils.vpd_calculator(temp, hum)

        try:
            if not db.put(
                time=int(unixtime),
                temp=temp,
                hum=hum,
                fan_speed=out_fan.fan_speed,
                vpd=vpd,
            ):
                raise

        except Exception as e:
            utils.log(f"error in data sending: {e}")
            smd.queue.append(
                {
                    "time": int(unixtime),
                    "temp": temp,
                    "hum": hum,
                    "fan_speed": out_fan.fan_speed,
                    "vpd": vpd,
                }
            )
            if not sta_if.isconnected():
                reset()

        if temp > points.POINT_TEMP + 0.1:
            out_fan.set_speed(out_fan.fan_speed + 1)
        elif temp < points.POINT_TEMP - 0.1:
            out_fan.set_speed(out_fan.fan_speed - 1)

        gc.collect()

        time.sleep(20 - (time.time() - start))


try:
    _thread.start_new_thread(smd.send_missed_data, ())
    main_loop()
except Exception as e:
    utils.log(e)
    reset()
