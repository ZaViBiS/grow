import requests

URL = "https://data.ygryk.de/put"


class Database:
    def __init__(self) -> None:
        pass

    def put(self, data: dict) -> bool:
        r = requests.post(URL, json=data, timeout=20)
        print(r.status_code)

        if r.status_code == 200:
            return True
        return False
