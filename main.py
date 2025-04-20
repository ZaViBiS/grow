import asyncio
import time
import gc

from machine import Pin, I2C, reset
from micropython_sht4x import sht4x

from fan_control import FanControl
from database import Database
import utils


async def main_loop():
    # I2C
    i2c = I2C(0, sda=Pin(8), scl=Pin(9), freq=100000)
    sht = sht4x.SHT4X(i2c)

    out_fan = FanControl(1)
    out_fan.set_speed(0)

    # smart = SmarkPlugContorl()
    points = utils.Points()
    db = Database()

    await points.update_data_in_class()
    while True:
        start = time.time()
        temp, hum = sht.measurements

        await db.put(
            time=time.time(),
            temp=temp,
            hum=hum,
            fan_speed=out_fan.fan_speed,
            vpd=utils.vpd_calculator(temp, hum),
        )

        if temp > points.POINT_TEMP + 0.1:
            out_fan.set_speed(out_fan.fan_speed + 1)
        elif temp < points.POINT_TEMP - 0.1:
            out_fan.set_speed(out_fan.fan_speed - 1)

        gc.collect()

        await asyncio.sleep(20 - (time.time() - start))


try:
    asyncio.run(main_loop())
except Exception as e:
    utils.append_to_file(e, "log.txt")
    reset()
