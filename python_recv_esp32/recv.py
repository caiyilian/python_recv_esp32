import random
import numpy as np
import cv2
import base64
from paho.mqtt import client as mqtt_client
import time
broker = 'test.ranye-iot.net'
port = 1883
topic = "Wechat2Esp/#"
client_id = f'python-mqtt-{random.randint(0, 100)}'
recList = []
start = time.time()

def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        global recList
        if msg.topic == "Wechat2Esp/start":
            recList = []
        elif msg.topic == "Wechat2Esp/end":
            # client.publish("esp32Ready", "")
            total = "".join(recList)
            Bytes = total.encode('utf8')
            array = np.frombuffer(base64.b64decode(Bytes), dtype=np.uint8)
            cv2.imshow('img', cv2.imdecode(array, cv2.IMREAD_COLOR))
            cv2.waitKey(1)
        else:
            recList.append(msg.payload.decode())
    client.subscribe(topic)
    client.on_message = on_message


def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()


if __name__ == '__main__':
    run()
