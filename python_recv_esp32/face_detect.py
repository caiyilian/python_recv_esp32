import requests
import cv2
import numpy as np
import mediapipe as mp

# 初始化人脸检测器
mpFaceDetection = mp.solutions.face_detection  # 人脸识别

# 设置人脸检测的自信值，这个值设置得太高，可能会检测漏人脸，如果太低，可能会把不是人脸的检测成人脸
faceDetection = mpFaceDetection.FaceDetection(0.5)
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
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = faceDetection.process(imgRGB)
        bboxs = []
        if results.detections:
            # for循环，循环每一张人脸
            for id, detection in enumerate(results.detections):
                # 人脸信息，里面包括人脸左上角的x，y值，以及这张人脸的高度宽度h和w，不过它进行了归一化操作，需要进一步处理
                bboxC = detection.location_data.relative_bounding_box
                # 先拿到真实图片的尺寸
                ih, iw, ic = img.shape
                # 把归一化的数据回复回来,得到人脸的真实位置
                bbox = int(bboxC.xmin * iw), int(bboxC.ymin * ih), int(bboxC.width * iw), int(bboxC.height * ih)
                # 把这张人脸信息放到列表里面
                bboxs.append([id, bbox, detection.score])
                # 人脸的左上角点的x,y和宽度高度
                x, y, w, h = bbox
                # 把帽子放到人脸上面，思路是帽子的宽度和人脸的宽度相同
                img = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                # 展示图片
        cv2.imshow('img', img)
        # 图片刷新率，每隔多少ms刷新一次图片
        cv2.waitKey(1)
