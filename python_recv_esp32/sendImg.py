import random
import time
import base64
from paho.mqtt import client as mqtt_client
import math
import requests
import cv2
import numpy as np

broker = 'test.ranye-iot.net'
port = 1883
topic = "Wechat2Esp/"
client_id = f'python-mqtt-{random.randint(0, 1000)}'
mode = "win"
if mode == 'win':
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 256)  # 设置宽度
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 192)  # 设置长度
elif mode == 'esp32':
    url = "http://192.168.1.102:81/stream"
    res = requests.get(url, stream=True)


def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def publish(client, sendList):
    client.publish(topic + "start", "")
    for index, content in enumerate(sendList):
        client.publish(topic + str(index), content, qos=0)
    client.publish(topic + "end", "")


def sendVideo():
    success, img = cap.read()
    retval, buffer = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 40])
    pic_str = base64.b64encode(buffer)
    sendData = pic_str.decode()
    sendList = []
    batchsNum = math.ceil(len(sendData) / 100)
    for i in range(batchsNum):
        try:
            sendList.append(sendData[i * 100:(i + 1) * 100])
        except:
            sendList.append(sendData[i * 100:])
    return sendList


def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        sendList = sendVideo()
        publish(client, sendList)

    client.subscribe("esp32Ready")
    client.on_message = on_message


def runByEsp32():
    client = connect_mqtt()
    while True:
        if res.raw.readline() == b'\r\n' and res.raw.readline() == b'--123456789000000000000987654321\r\n':
            res.raw.readline()
            # 图片的字节流的长度
            length = res.raw.readline()[16:-2]
            res.raw.readline()
            # 在这之前都是类似于响应头，这些信息用处不大，除了那个长度，下面这个才是整个图片
            imgData = res.raw.read(int(length))
            sendData = (base64.b64encode(imgData)).decode('utf8')
            sendList = []
            batchsNum = math.ceil(len(sendData) / 100)
            for i in range(batchsNum):
                try:
                    sendList.append(sendData[i * 100:(i + 1) * 100])
                except:
                    sendList.append(sendData[i * 100:])
            publish(client, sendList)


def runByWin():
    client = connect_mqtt()
    subscribe(client)
    sendList = sendVideo()
    publish(client, sendList)
    client.loop_forever()
    # 发送


if __name__ == '__main__':
    runByWin()
