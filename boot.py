import network
from machine import reset as r

import ntptime
import time
import gc

sta_if = network.WLAN(network.WLAN.IF_STA)
if not sta_if.isconnected():
    print("connecting to network...")
    sta_if.active(True)
    sta_if.connect("define", "M74Ra3GMT6R3PrhF")
    while not sta_if.isconnected():
        pass
print("network config:", sta_if.ipconfig("addr4"))
if time.localtime()[0] == 2000:
    ntptime.settime()

# 🔹 Створення власної точки доступу (AP mode)
ap_if = network.WLAN(network.AP_IF)
ap_if.active(True)
ap_if.config(essid="ESP32_Network", password="12345678")
print("Створено Wi-Fi AP! IP:", ap_if.ifconfig()[0])

gc.collect()
