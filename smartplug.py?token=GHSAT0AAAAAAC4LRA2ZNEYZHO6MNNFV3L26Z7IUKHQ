import time
import hashlib
import hmac
import requests
import json
import binascii


CLIENT_ID = "j8khm73xeq8jws3eaqds"
SECRET = "2c3f69535f994b429e8e8682e4e6cd0d"
DEVICE_ID = "eb6d4cb88b8052f5e74iin"

# Базовий URL для серверів Tuya у США
BASE_URL = "https://openapi.tuyaus.com"


class SmarkPlugContorl:
    def __init__(self) -> None:
        self.last_status = False

    def __gettime_ms(self) -> str:
        # 946684800 - це конвертація часу в unix
        return str(int((time.time() + 946684800) * 1000))

    @staticmethod
    def __command(status: bool):
        return {"commands": [{"code": "switch_1", "value": status}]}

    def __get_access_token(self):
        """Отримує access token від Tuya API."""
        t = self.__gettime_ms()
        method = "GET"
        url = "/v1.0/token?grant_type=1"

        sha256_body = binascii.hexlify(
            hashlib.sha256(b"").digest()
        ).decode()  # Хеш пустого тіла
        string_to_sign = CLIENT_ID + t + method + "\n" + sha256_body + "\n\n" + url
        sign = (
            hmac.new(SECRET.encode(), string_to_sign.encode(), hashlib.sha256)
            .hexdigest()
            .upper()
        )

        headers = {
            "client_id": CLIENT_ID,
            "t": t,
            "sign": sign,
            "sign_method": "HMAC-SHA256",
            "mode": "cors",
            "Content-Type": "application/json",
        }

        response = requests.get(BASE_URL + url, headers=headers)
        data = response.json()

        if data["success"]:
            return data["result"]["access_token"]
        else:
            raise Exception("Не вдалося отримати access token: " + data["msg"])

    def __send_command(self, set_status: bool):
        """Відправляє команду для вимкнення пристрою."""
        access_token = self.__get_access_token()
        t = self.__gettime_ms()
        method = "POST"
        url = f"/v1.0/devices/{DEVICE_ID}/commands"
        body = json.dumps(self.__command(set_status))  # Перетворюємо команду в JSON
        sha256_body = binascii.hexlify(
            hashlib.sha256(body.encode()).digest()
        ).decode()  # Хеш тіла запиту
        string_to_sign = (
            CLIENT_ID + access_token + t + method + "\n" + sha256_body + "\n\n" + url
        )
        sign = (
            hmac.new(SECRET.encode(), string_to_sign.encode(), hashlib.sha256)
            .hexdigest()
            .upper()
        )

        headers = {
            "client_id": CLIENT_ID,
            "access_token": access_token,
            "t": t,
            "sign": sign,
            "sign_method": "HMAC-SHA256",
            "mode": "cors",
            "Content-Type": "application/json",
        }

        response = requests.post(BASE_URL + url, headers=headers, data=body)
        data = response.json()

        if data["success"]:
            print(f"Розетка успішно змінила свій статус на {set_status}")
        else:
            print("Не вдалося відправити команду: " + data["msg"])

    def update_device_status(self) -> bool:
        t = self.__gettime_ms()
        access_token = self.__get_access_token()
        url = f"/v1.0/devices/{DEVICE_ID}/status"
        sha256_body = binascii.hexlify(hashlib.sha256(b"").digest()).decode()
        string_to_sign = f"{CLIENT_ID}{access_token}{t}GET\n{sha256_body}\n\n{url}"
        sign = (
            hmac.new(SECRET.encode(), string_to_sign.encode(), hashlib.sha256)
            .hexdigest()
            .upper()
        )

        headers = {
            "client_id": CLIENT_ID,
            "access_token": access_token,
            "t": t,
            "sign": sign,
            "sign_method": "HMAC-SHA256",
        }

        response = requests.get(BASE_URL + url, headers=headers)
        data = response.json()
        if data["success"]:
            self.last_status = data["result"][0]["value"]

            return True
        return False

    def change(self, status: bool = False):
        if self.last_status != status:
            self.last_status = status
            try:
                self.__send_command(status)
            except Exception as e:
                print(e)
