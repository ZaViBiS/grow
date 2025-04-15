import asyncio
import random
import json
import time
import gc

from microdot import Microdot, Response
from machine import Pin, I2C
from micropython_sht4x import sht4x

from fan_control import FanControl
from database import Database
import utils

from ssd1306 import SSD1306_I2C
from writer import Writer
import tuny

# I2C
i2c = I2C(0, sda=Pin(8), scl=Pin(9), freq=100000)
sht = sht4x.SHT4X(i2c)
o = SSD1306_I2C(128, 64, i2c)
ssd = Writer(o, tuny)

out_fan = FanControl(1)
out_fan.set_speed(0)

Response.default_content_type = "text/html"
app = Microdot()

# smart = SmarkPlugContorl()
points = utils.Points()
db = Database()


data_now = {"temp": 0, "hum": 0, "vpd": 0}
data_avg = {"temp": 0, "hum": 0, "vpd": 0, "fan_speed": 0}


async def antidead_signal():
    while True:
        for x in ["|", "/", "-", "\\"]:
            o.fill_rect(0, 50, 50, 20, 0)
            o.text(x, 0, 50, 1)
            o.show()
            await asyncio.sleep(0.8)


@app.route("/")
async def index(request):
    return Response.send_file("index.html", content_type="text/html")


@app.route("/data")
async def data(request):
    data_now["fan_speed"] = out_fan.fan_speed
    return data_now


@app.route("/set_points", methods=["POST"])
async def set_points(request):
    data = json.loads(request.body)

    if "temp" in data and "hum" in data:
        await points.change_data(data)
        await points.update_data_in_class()
        # Оновлюємо глобальний об'єкт points.data
        return {"status": "success"}
    else:
        return {"status": "error", "message": "Неправильні дані"}, 400


@app.route("/chart.js")
async def chart(request):
    return Response.send_file("chart.js", content_type="application/javascript")


@app.route("/min.js")
async def min_js(request):
    return Response.send_file("min.js", content_type="application/javascript")


async def main_loop():
    await points.update_data_in_class()
    try:
        while True:
            start = time.time()
            data_now["temp"], data_now["hum"] = sht.measurements
            data_now["vpd"] = utils.vpd_calculator(data_now["temp"], data_now["hum"])

            await db.put(
                time=time.time(),
                temp=data_now["temp"],
                hum=data_now["hum"],
                fan_speed=out_fan.fan_speed,
                vpd=data_now["vpd"],
            )

            if data_now["temp"] > points.POINT_TEMP + 0.1:
                out_fan.set_speed(out_fan.fan_speed + 1)
            elif data_now["temp"] < points.POINT_TEMP - 0.1:
                out_fan.set_speed(out_fan.fan_speed - 1)

            o.fill(0)
            ssd.set_textpos(o, 0, 0)
            ssd.printstring(f"TEMP/avg: {data_now['temp']:.2f}C\n")
            ssd.printstring(f"HUM/avg:  {data_now['hum']:.2f}%\n")
            ssd.printstring(f"OUT fan speed: {out_fan.fan_speed}%\n")
            ssd.printstring(f"VPD: {data_now['vpd']:.2f}\n")
            ssd.printstring(f"ram free: {gc.mem_free()} bytes\n")
            o.show()
            gc.collect()

            await asyncio.sleep(20 - (time.time() - start))
    except Exception as e:
        utils.log(e)


async def main():
    server = asyncio.create_task(app.start_server(port=80, debug=True))

    asyncio.create_task(antidead_signal())
    asyncio.create_task(main_loop())

    await server


asyncio.run(main())
