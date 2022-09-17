import requests
import cv2
import numpy as np

# 192.168.1.113是你的esp32返回的服务器ip地址
url = "http://192.168.1.113:81/stream"
res = requests.get(url, stream=True)

while True:
    if res.raw.readline() == b'\r\n' and res.raw.readline() == b'--123456789000000000000987654321\r\n':
        res.raw.readline()
        # 图片的字节流的长度
        length = res.raw.readline()[16:-2]
        res.raw.readline()
        # 在这之前都是类似于响应头，这些信息用处不大，除了那个长度，下面这个才是整个图片
        img = cv2.imdecode(np.frombuffer(res.raw.read(int(length)), dtype=np.uint8), cv2.IMREAD_COLOR)
        cv2.imshow("img", img)
        cv2.waitKey(1)
