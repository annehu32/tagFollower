# Librarys for mqtt
import time
import network
from mqtt import MQTTClient

# Libraries for aprilTags
import sensor
import time
import math

#motor library
import machine
from machine import Pin, PWM


# ---- Camera Setup -----
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QQVGA)
sensor.skip_frames(time=2000)
sensor.set_auto_gain(False)  # must turn this off to prevent image washout...
sensor.set_auto_whitebal(False)  # must turn this off to prevent image washout...
clock = time.clock()

# ----__- MQTT Setup --__---
SSID = "Tufts_Robot"  # Network SSID
KEY = ""  # Network key

# Init wlan module and connect to network
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, KEY)

while not wlan.isconnected():
    print('Trying to connect to "{:s}"...'.format(SSID))
    time.sleep_ms(1000)

# We should have a valid IP now via DHCP
print("WiFi Connected ", wlan.ifconfig())

client = MQTTClient('ME35_Anne_1', 'broker.hivemq.com', port=1883)
client.connect()

# ----- HELPER FUNCTIONS -----
# Takes the change in z-distance, uses proportional control to determine pwm
# Big change in position will mean big position change
def propControl(val):
    Kp = 0.5
    error = val - 5.5 #at z=-5.5, the car will hit something in front of it
    minPWM = 0
    rangePWM = 65335-minPWM

    return int(minPWM + abs(rangePWM*Kp*error))


# --------- MAIN CODE ---------------
lastDist = 0
stopDist = -5.5 # Where the camera is mounted on the car, distance of 5.5 is right before impact

while True:
    clock.tick()
    img = sensor.snapshot()

    for tag in img.find_apriltags():  # No arguments for now
        count = 0
        img.draw_rectangle(tag.rect, color=(255, 0, 0))
        img.draw_cross(tag.cx, tag.cy, color=(0, 255, 0))

        dist = abs(tag.z_translation) # distance from the camera is Z translation
        change = dist - lastDist
        lastDist = dist

        print("distance: " + str(dist))
        if change > 0.1:
            print("publishing.....")
            client.publish("ME35-24/potato", str(propControl(change)))
        else:
            client.publish("ME35-24/potato", "0") # if no change, don't move
