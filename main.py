import _thread
import time
import gc

from machine import Pin, I2C, reset
from micropython_sht4x import sht4x

from pid import PID
from machine import Pin, PWM
from database import Database
import utils

smd = utils.SendMissedData()
db = Database()
points = utils.Points()

# PID controller initialization
# Kp, Ki, Kd values are initial guesses and may need tuning
# setpoint is the target temperature
# output_limits (0, 1023) correspond to PWM duty cycle range
pid_controller = PID(Kp=50.0, Ki=0.1, Kd=0.1, setpoint=26, output_limits=(0, 1023))

# Fan PWM setup
fan_pin = Pin(1) # Assuming fan is connected to Pin(1) as per previous fan_control.py
fan_pwm = PWM(fan_pin)
fan_pwm.freq(1000) # Set PWM frequency to 1000 Hz
fan_pwm.duty(0) # Start with fan off

temp, hum = 0.0, 0.0
points.update_data_in_class()


def sender():
    """thread that send data every 60 second"""
    global temp, hum
    while temp == 0:
        time.sleep(1)
    while True:
        try:
            start = time.ticks_ms()
            unixtime = int(utils.get_unix_time_now(time.time()))

            if not db.put(
                time=unixtime,
                temp=temp,
                hum=hum,
                fan_speed=int(pid_controller.output),
                vpd=utils.vpd_calculator(temp, hum),
            ):
                utils.log("Exception: проблема при відпраці даних")
                raise

        except Exception as e:
            utils.log(f"error in data sending: {e}")
            smd.queue.append(
                {
                    "time": int(unixtime),
                    "temp": temp,
                    "hum": hum,
                    "fan_speed": int(pid_controller.output),
                    "vpd": utils.vpd_calculator(temp, hum),
                }
            )
            if not sta_if.isconnected():
                reset()
        time.sleep(60 - time.ticks_diff(time.ticks_ms(), start) / 1000)


def main_loop():
    # I2C
    global temp, hum
    i2c = I2C(0, sda=Pin(8), scl=Pin(9), freq=100000)
    sht = sht4x.SHT4X(i2c)

    while True:
        start = time.ticks_ms()

        temp, hum = sht.measurements
        pid_output = pid_controller.update(temp)
        fan_pwm.duty(int(pid_output))

        # No learning phase needed for PID, as it's a direct control loop
        # The sleep(1) and sleep(2 - ...) are still relevant for sensor readings and loop timing

        time.sleep(2 - time.ticks_diff(time.ticks_ms(), start) / 1000)

        gc.collect()


try:
    _thread.start_new_thread(sender, ())
    _thread.start_new_thread(smd.send_missed_data, ())
    main_loop()
except Exception as e:
    utils.log(e)
    reset()
