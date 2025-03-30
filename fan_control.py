import time
from machine import Pin, PWM


class FanControl:
    def __init__(self, control_pin: int):
        self.fan = PWM(Pin(control_pin))
        self.fan.freq(25000)

        self.fan.duty_u16(0)
        self.fan_speed = 0

    def set_speed(self, percent: int) -> None:
        """Функція керування швидкістю (0-100%)"""
        if percent > 100:
            percent = 100
        elif percent < 0:
            percent = 0

        duty = int(percent * 65535 / 100)  # Перетворення у 16-бітне значення

        if percent <= 15 and percent > 5:
            self.set_speed(100)
            time.sleep(0.4)

        self.fan.duty_u16(duty)
        self.fan_speed = percent
