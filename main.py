import asyncio
import time
import gc

from microdot import Microdot, Response
from machine import Pin, I2C
from micropython_sht4x import sht4x

from fan_control import FanControl
from smartplug import SmarkPlugContorl
import utils

from ssd1306 import SSD1306_I2C
from writer import Writer
import tuny

POINT_TEMP = 26
POINT_HUM = 40

# I2C
i2c = I2C(0, sda=Pin(8), scl=Pin(9), freq=100_000)
sht = sht4x.SHT4X(i2c)
o = SSD1306_I2C(128, 64, i2c)
ssd = Writer(o, tuny)

out_fan = FanControl(1)
out_fan.set_speed(0)

Response.default_content_type = "text/html"
app = Microdot()

smart = SmarkPlugContorl()
stat = utils.Statistics()


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


@app.route("/history")
async def history(request):
    gc.collect()
    return stat.data


@app.route("/chart.js")
async def chart(request):
    return Response.send_file("chart.js", content_type="application/javascript")


@app.route("/min.js")
async def min_js(request):
    return Response.send_file("min.js", content_type="application/javascript")


async def main_loop():
    while True:
        data_now["temp"], data_now["hum"] = sht.measurements
        data_now["vpd"] = utils.vpd_calculator(data_now["temp"], data_now["hum"])

        stat.data["time"].append(time.time())
        stat.data["temp"].append(data_now["temp"])
        stat.data["hum"].append(data_now["hum"])
        stat.data["vpd"].append(data_now["vpd"])
        stat.data["fan_speeds"].append(out_fan.fan_speed)

        if int(data_now["hum"]) == POINT_HUM and not smart.last_status:
            smart.change_condition(False)
        else:
            if data_now["hum"] > POINT_HUM + 5:
                smart.change_condition(True)
            elif data_now["hum"] < POINT_HUM - 5:
                smart.change_condition(False)

        if data_now["temp"] > POINT_TEMP + 1:
            out_fan.set_speed(out_fan.fan_speed + 1)
        elif data_now["temp"] < POINT_TEMP - 1:
            out_fan.set_speed(out_fan.fan_speed - 1)

        data_avg = stat.statistics_for_24h()
        o.fill(0)
        ssd.set_textpos(o, 0, 0)
        ssd.printstring(
            f"TEMP/avg: {data_now['temp']:.2f}C | {data_avg['temp']:.2f}C\n"
        )
        ssd.printstring(f"HUM/avg:  {data_now['hum']:.2f}% | {data_avg['hum']:.2f}%\n")
        ssd.printstring(
            f"OUT fan speed: {out_fan.fan_speed}% | {data_avg['fan_speed']}%\n"
        )
        ssd.printstring(f"VPD: {data_now['vpd']:.2f} avg: {data_avg['vpd']:.2f}\n")
        ssd.printstring(f"ram free: {gc.mem_free()} bytes\n")
        o.show()
        gc.collect()

        await asyncio.sleep(2.5 * 60)


async def main():
    server = asyncio.create_task(app.start_server(port=80, debug=True))

    asyncio.create_task(antidead_signal())
    asyncio.create_task(main_loop())

    await server


asyncio.run(main())
