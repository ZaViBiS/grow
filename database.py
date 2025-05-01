import requests

URL = "https://data.ygryk.de/put"


class Database:
    def __init__(self) -> None:
        pass

    async def put(
        self, time: int, temp: float, hum: float, fan_speed: int, vpd: float
    ) -> None:
        data = {
            "time": time,
            "temp": temp,
            "hum": hum,
            "fan_speed": fan_speed,
            "vpd": vpd,
        }

        requests.post(URL, json=data)
