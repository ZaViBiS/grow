import btree
import math
import json
import time
import os
import gc

from database import Database

database = Database()


def log(text: str | Exception) -> None:
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
    return round(svp - avp, 2)


class Statistics:
    def __init__(self) -> None:
        self.data = {"time": [], "temp": [], "hum": [], "vpd": [], "fan_speeds": []}

    def __delete_outdated_data(self) -> None:
        for x in self.data["time"]:
            if x < time.time() - (12 * 60 * 60):  # 24h
                del self.data["time"][self.data["time"].index(x)]
                return
            else:
                return

    async def statistics_for_24h(self) -> dict[str, float]:
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


class Points:
    def __init__(self) -> None:
        self.POINT_TEMP = 0
        self.POINT_HUM = 0

    def get_data(self):
        """return: {temp: int, hum: int}"""
        with open("points.json", "r") as file:
            return json.loads(file.read())

    def change_data(self, data: dict):
        with open("points.json", "w") as file:
            file.write(json.dumps(data))

    def update_data_in_class(self):
        data = self.get_data()
        self.POINT_TEMP = data["temp"]
        self.POINT_HUM = data["hum"]


def append_to_file(text, filename):
    """
    Додає переданий текст у кінець файлу.
    Якщо файл не існує - створює новий файл.

    Аргументи:
        text (str): Текст для запису
        filename (str): Шлях до файлу
    """
    with open(filename, "a", encoding="utf-8") as file:
        file.write(text)


def get_unix_time_now(now: float | bool = False) -> float:
    if now:
        return now
    return int(time.time() + 946684800)


class SendMissedData:
    def __init__(self) -> None:
        self.queue = []

    class BTreeDB:
        def __init__(self, filename="data"):
            self.filename = filename
            self.file = None
            self.db = None

        def __enter__(self):
            try:
                self.file = open("mydb", "r+b")
            except OSError:
                self.file = open("mydb", "w+b")

            self.db = btree.open(self.file)
            return self.db

        def __exit__(self, exc_type, exc_val, exc_tb):
            if self.db:
                self.db.flush()
                self.db.close()
            if self.file:
                self.file.close()

    def add_data_tothe_database(self, data: dict):
        with self.BTreeDB() as db:
            db[str(data["time"]).encode()] = json.dumps(data)

    def send_missed_data(self):
        while True:
            # adding to the database from the queue
            for data in self.queue:
                self.add_data_tothe_database(data)
                self.queue.remove(data)

            with self.BTreeDB() as db:
                for x in db:
                    data = json.loads(db[x])
                    try:
                        if database.put(data):
                            del db[x]
                    except Exception as e:
                        time.sleep(10)
                        log(f"error in resending: {e}")
                    gc.collect()

            time.sleep(3 * 60)
