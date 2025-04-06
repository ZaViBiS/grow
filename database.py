import firebase

URL = "https://grow-192db-default-rtdb.europe-west1.firebasedatabase.app/"


class Database:
    def __init__(self) -> None:
        firebase.setURL(URL)

    async def put(
        self, time: int, temp: float, hum: float, fan_speed: int, vpd: float
    ) -> None:
        data = {
            "temp": temp,
            "hum": hum,
            "fan_speed": fan_speed,
            "vpd": vpd,
        }
        firebase.put(f"/data/{time + 946684800}", data, bg=False)
