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


temp_now = 0.0
hum_now = 0.0
vpd_now = 0.0

temp_avg, hum_avg, avg_vpd, fan_speed_avg = 0.0, 0.0, 0.0, 0.0


async def antidead_signal():
    while True:
        for x in ["|", "/", "-", "\\"]:
            o.fill_rect(0, 50, 50, 20, 0)
            o.text(x, 0, 50, 1)
            o.show()
            await asyncio.sleep(0.8)


@app.route("/")
async def index(request):
    return Response(
        utils.html_load(
            temp_now,
            temp_avg,
            hum_now,
            hum_avg,
            out_fan.fan_speed,
            fan_speed_avg,
            False,
            vpd_now,
            avg_vpd,
        )
    )


async def main_loop():
    global temp_now, hum_now, vpd_now, temp_avg, hum_avg, avg_vpd, fan_speed_avg
    stat = utils.Statistics()
    while True:
        temp_now, hum_now = sht.measurements
        vpd_now = utils.vpd_calculator(temp_now, hum_now)

        stat.data.append(
            (
                temp_now,
                hum_now,
                time.time(),
                utils.vpd_calculator(temp_now, hum_now),
                out_fan.fan_speed,
            )
        )

        # if int(hum_now) == POINT_HUM and not smart.last_status:
        #     smart.change_condition(False)
        # else:
        #     if hum_now > POINT_HUM + 5:
        #         smart.change_condition(True)
        #     elif hum_now < POINT_HUM - 5:
        #         smart.change_condition(False)

        if temp_now > POINT_TEMP + 1:
            out_fan.set_speed(out_fan.fan_speed + 1)
        elif temp_now < POINT_TEMP - 1:
            out_fan.set_speed(out_fan.fan_speed - 1)

        utils.log(
            f"temp: {temp_now:.2f}C, hum: {hum_now:.2f}% | out_fan speed: {out_fan.fan_speed}"
        )
        temp_avg, hum_avg, avg_vpd, fan_speed_avg = stat.statistics_for_24h()
        o.fill(0)
        ssd.set_textpos(o, 0, 0)
        ssd.printstring(f"TEMP/avg: {temp_now:.2f}C | {temp_avg:.2f}C\n")
        ssd.printstring(f"HUM/avg:  {hum_now:.2f}% | {hum_avg:.2f}%\n")
        ssd.printstring(f"OUT fan speed: {out_fan.fan_speed}% | {fan_speed_avg}%\n")
        ssd.printstring(f"VPD: {vpd_now:.2f} avg: {avg_vpd:.2f}\n")
        ssd.printstring(f"ram free: {gc.mem_free()} bytes\n")
        o.show()
        gc.collect()

        await asyncio.sleep(2.5 * 60)


async def main():
    server = asyncio.create_task(app.start_server())

    asyncio.create_task(antidead_signal())
    asyncio.create_task(main_loop())

    await server


asyncio.run(main())
