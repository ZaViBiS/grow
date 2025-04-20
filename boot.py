import utils
from machine import reset as r

try:
    import network

    import ntptime
    import time
    import gc

    sta_if = network.WLAN(network.WLAN.IF_STA)
    if not sta_if.isconnected():
        print("connecting to network...")
        sta_if.active(True)
        sta_if.connect("Villa Antonia", "4815267381122898")
        while not sta_if.isconnected():
            pass
    print("network config:", sta_if.ipconfig("addr4"))
    if time.localtime()[0] == 2000:
        ntptime.settime()

    gc.collect()
except Exception as e:
    utils.append_to_file(str(e), "log.txt")
    r()
