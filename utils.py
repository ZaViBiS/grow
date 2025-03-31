import math
import time


def log(text: str) -> None:
    t = time.localtime()  # Отримуємо локальний час
    date_str = "{:02}-{:02}-{:04} {:02}:{:02}:{:02}".format(
        t[2], t[1], t[0], t[3], t[4], t[5]
    )
    print(f"{date_str} - INFO - {text}")


def saturation_vapor_pressure(temp):
    """
    Розрахунок насиченого парціального тиску (SVP) за температури (°C).
    """
    return 0.6108 * math.exp((17.27 * temp) / (temp + 237.3))


def vpd_calculator(temp, rh):
    """
    Розрахунок VPD (дефіциту парціального тиску).
    :param temp_c: температура в градусах Цельсія
    :param rh: відносна вологість у відсотках (0-100)
    :return: VPD у кПа
    """
    svp = saturation_vapor_pressure(temp)
    avp = svp * (rh / 100)
    return svp - avp


class Statistics:
    def __init__(self) -> None:
        self.data = {"time": [], "temp": [], "hum": [], "vpd": [], "fan_speeds": []}

    def __delete_outdated_data(self) -> None:
        for x in self.data["time"]:
            if x < time.time() - (24 * 60 * 60):  # 24h
                del self.data["time"][self.data["time"].index(x)]
                return
            else:
                return

    def statistics_for_24h(self) -> dict[str, float]:
        self.__delete_outdated_data()
        temp_avg, hum_avg, vpd_avg, avg_fan_speed = 0, 0, 0, 0
        num = 0
        for temp, hum, vpd, fan in zip(
            self.data["temp"],
            self.data["hum"],
            self.data["vpd"],
            self.data["fan_speeds"],
        ):
            temp_avg += temp
            hum_avg += hum
            vpd_avg += vpd
            avg_fan_speed += fan
            num += 1
        res = {}
        res["temp"] = temp_avg / num
        res["hum"] = hum_avg / num
        res["vpd"] = vpd_avg / num
        res["fan_speed"] = avg_fan_speed / num
        return res
