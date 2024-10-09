# This work is licensed under the MIT license.
# Copyright (c) 2013-2023 OpenMV LLC. All rights reserved.
# https://github.com/openmv/openmv/blob/master/LICENSE
# Code samples from OPEN MV examples: mqttt_pub and find_apriltags_3d_pose1
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
# ---- Camera Setup -----
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QQVGA)
sensor.skip_frames(time=2000)
sensor.set_auto_gain(False)  # must turn this off to prevent image washout...
sensor.set_auto_whitebal(False)  # must turn this off to prevent image washout...
clock = time.clock()
# ----- HELPER FUNCTIONS -----
# Takes the change in z-distance, uses proportional control to determine pwm
# Big change in position will mean big position change
def propControl(val):
    Kp = 1000
    minPWM = 15000
    maxPWM = 65335
    setPWM = Kp * val + minPWM
    if setPWM >= maxPWM:
        setPWM = maxPWM
    return int(setPWM)
# --------- MAIN CODE ---------------
lastDist = 0
stopDist = -5.5 # Where the camera is mounted on the car, distance of 5.5 is right before impact
targetDist = 10
while True:
    clock.tick()
    img = sensor.snapshot()
    for tag in img.find_apriltags():  # No arguments for now
        count = 0
        img.draw_rectangle(tag.rect, color=(255, 0, 0))
        img.draw_cross(tag.cx, tag.cy, color=(0, 255, 0))
        dist = abs(tag.z_translation) # distance from the camera is Z translation
        change = dist - targetDist
        #lastDist = dist›
        print("distance: " + str(dist) + " change: " +str(change))
        print("x-translation: "+str(tag.x_translation))
        if change > 0.5:
            client.publish("ME35-24/potato", "F" + str(propControl(abs(change))))
        elif change < -0.5:
            client.publish("ME35-24/potato", "B" + str(propControl(abs(change))))
        else:
            client.publish("ME35-24/potato", "F0") # if no change, don't move
