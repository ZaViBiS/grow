import math
import time


def log(text: str) -> None:
    t = time.localtime()  # Отримуємо локальний час
    date_str = "{:02}-{:02}-{:04} {:02}:{:02}:{:02}".format(
        t[2], t[1], t[0], t[3], t[4], t[5]
    )
    print(f"{date_str} - INFO - {text}")


def html_load(
    temp: float,
    avg_temp: float,
    hum: float,
    avg_hum: float,
    fan_speed: int,
    avg_fan_speed: float,
    dihumidefier: bool,
    vpd: float,
    avg_vpd: float,
) -> str:
    with open("index.html", "r") as file:
        html = file.read()

    html = html.replace("{{TEMP}}", str(temp))
    html = html.replace("{{HUM}}", str(hum))
    html = html.replace("{{AVGTEMP}}", str(avg_temp))
    html = html.replace("{{AVGHUM}}", str(avg_hum))
    html = html.replace("{{FANSPEED}}", str(fan_speed))
    html = html.replace("{{AVGFANSPEED}}", str(avg_fan_speed))
    html = html.replace("{{DIHUMIDEFIER}}", str(dihumidefier))
    html = html.replace("{{VPD}}", str(vpd))
    html = html.replace("{{AVGVPD}}", str(avg_vpd))
    return html


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
        self.data = []

    def __delete_outdated_data(self) -> None:
        for x in self.data:
            if x[2] < time.time() - (24 * 60 * 60):  # 24h
                del self.data[self.data.index(x)]
                return
            else:
                return

    def statistics_for_24h(self) -> tuple[float, float, float, float]:
        self.__delete_outdated_data()
        temp_avg, hum_avg, vpd_avg, avg_fan_speed = 0, 0, 0, 0
        num = 0
        for x in self.data:
            temp_avg += x[0]
            hum_avg += x[1]
            vpd_avg += x[3]
            avg_fan_speed += x[4]
            num += 1

        return temp_avg / num, hum_avg / num, vpd_avg / num, avg_fan_speed / num
