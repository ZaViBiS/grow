import asyncio
import json
import time
import gc
import os

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
        unixtime = utils.get_unix_time_now(start)
        temp, hum = sht.measurements
        vpd = utils.vpd_calculator(temp, hum)

        try:
            if not await db.put(
                time=int(unixtime),
                temp=temp,
                hum=hum,
                fan_speed=out_fan.fan_speed,
                vpd=vpd,
            ):
                raise
            datalistdir = os.listdir("/data")
            if datalistdir:
                with open("/data/" + datalistdir[0], "r") as f:
                    data = json.loads(f.read())

                if await db.put(
                    time=data["time"],
                    temp=data["temp"],
                    hum=data["hum"],
                    fan_speed=data["fan_speed"],
                    vpd=data["vpd"],
                ):
                    os.remove("/data/" + datalistdir[0])
        except Exception as e:
            utils.log(f"error in data sending: {e}")
            with open(f"/data/{unixtime}", "w") as f:
                f.write(
                    json.dumps(
                        {
                            "time": int(unixtime),
                            "temp": temp,
                            "hum": hum,
                            "fan_speed": out_fan.fan_speed,
                            "vpd": vpd,
                        }
                    )
                )
            reset()

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
