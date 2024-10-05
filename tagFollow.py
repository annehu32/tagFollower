import time
import network
from machine import Pin, PWM
from mqtt import MQTTClient
from Motor import Motor #wrote a class for motor objects
import uasyncio as asyncio


# ---- MQTT THINGS ----
ssid = 'Tufts_Robot'
password = ''

mqtt_broker = 'broker.hivemq.com'
port = 1883
topic_sub = 'ME35-24/potato'

isOn = False

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    
    while not wlan.isconnected():
        time.sleep(1)
    print('----- connected to wifi -----')
        
def connect_mqtt(client):
    client.connect()
    client.subscribe(topic_sub.encode())
    print(f'Subscribed to {topic_sub}')
        
def callback(topic, msg):
    
    val = msg.decode()
    print((topic.decode(), val))
    percent = int(val[1:])
    pwm = 30000 + percent*(40000-30000)

    if val[0] == 'L':
        motor.goBackward(pwm)
        time.sleep(0.01)
        motor.stop()
    elif val[0] == 'R':
        motor.goForward(pwm)
        time.sleep(0.01)
        motor.stop()

        
async def mqtt_handler(client):
    while True:
        if network.WLAN(network.STA_IF).isconnected():
            try:
                client.check_msg()
            except Exception as e:
                print('MQTT callback failed')
                connect_mqtt(client)
        else:
            print('Wifi disconnected, trying to connect...')
            connect_wifi()
        await asyncio.sleep(0.01)


# --- Defining pins and motor objects ----
motor1A = Pin('GPIO1', Pin.OUT)
motor1B = Pin('GPIO2', Pin.OUT)
motor1PWM = PWM(Pin('GPIO3', Pin.OUT))
motor = Motor(motor1A, motor1B, motor1PWM, 'left')

connect_wifi()
client = MQTTClient('ME35_Anne', mqtt_broker, port, keepalive=60)
client.set_callback(callback)
client.connect()
client.subscribe(topic_sub.encode())
print(f'Subscribed to {topic_sub}')
asyncio.run(mqtt_handler(client))
