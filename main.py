import _thread
import time
import gc

from machine import Pin, I2C, reset
from micropython_sht4x import sht4x

from fan_control import FanControl
from database import Database
import utils

smd = utils.SendMissedData()
db = Database()
points = utils.Points()
out_fan = FanControl(1)
out_fan.set_speed(0)

temp, hum = 0.0, 0.0
points.update_data_in_class()


def sender():
    """thread that send data every 60 second"""
    try:
        while True:
            start = time.ticks_ms()
            unixtime = int(utils.get_unix_time_now(time.time()))

            if not db.put(
                time=unixtime,
                temp=temp,
                hum=hum,
                fan_speed=out_fan.fan_speed,
                vpd=utils.vpd_calculator(temp, hum),
            ):
                utils.log("Exception: проблема при відпраці даних")
                raise

            time.sleep(60 - time.ticks_diff(time.ticks_ms(), start))

    except Exception as e:
        utils.log(f"error in data sending: {e}")
        smd.queue.append(
            {
                "time": int(unixtime),
                "temp": temp,
                "hum": hum,
                "fan_speed": out_fan.fan_speed,
                "vpd": utils.vpd_calculator(temp, hum),
            }
        )
        if not sta_if.isconnected():
            reset()


def main_loop():
    # I2C
    i2c = I2C(0, sda=Pin(8), scl=Pin(9), freq=100000)
    sht = sht4x.SHT4X(i2c)
    pid = utils.PID(kp=5, ki=0.2, kd=2, setpoint=points.POINT_TEMP)

    while True:
        start = time.ticks_ms()
        temp, hum = sht.measurements

        speed = pid.compute(temp)
        out_fan.set_speed(int(speed))

        gc.collect()

        time.sleep(2 - time.ticks_diff(time.ticks_ms(), start))


try:
    _thread.start_new_thread(sender, ())
    _thread.start_new_thread(smd.send_missed_data, ())
    main_loop()
except Exception as e:
    utils.log(e)
    reset()
