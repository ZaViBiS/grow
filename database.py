import requests

URL = "https://158.180.54.159:8080/put"


class Database:
    def __init__(self) -> None:
        pass

    def put(
        self, time: int, temp: float, hum: float, fan_speed: int, vpd: float
    ) -> bool:
        data = {
            "time": time,
            "temp": temp,
            "hum": hum,
            "fan_speed": fan_speed,
            "vpd": vpd,
        }
        r = requests.post(URL, json=data, timeout=20)
        print(r.status_code)

        if r.status_code == 200:
            return True
        return False
