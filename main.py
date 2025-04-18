import asyncio
import time
import gc

from machine import Pin, I2C, reset
from micropython_sht4x import sht4x

from fan_control import FanControl
from database import Database
import utils

# I2C
i2c = I2C(0, sda=Pin(8), scl=Pin(9), freq=100000)
sht = sht4x.SHT4X(i2c)

out_fan = FanControl(1)
out_fan.set_speed(0)

# smart = SmarkPlugContorl()
points = utils.Points()
db = Database()


async def main_loop():
    await points.update_data_in_class()
    while True:
        try:
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
        except:
            await asyncio.sleep(60)
            reset()


asyncio.run(main_loop())
