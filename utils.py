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
    fan_speed: int,
    avg_fan_speed: float,
    dihumidefier: bool,
    vpd: float,
    avg_vpd: float,
) -> str:
    with open("index.html", "r") as file:
        html = file.read()

    return html.replace()
