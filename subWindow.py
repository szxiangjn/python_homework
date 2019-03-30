# -*- coding: utf-8 -*-
"""
Created on Mon Mar 25 15:04:23 2019

@author: 70437
"""

import base64, requests, json
from PyQt5.QtWidgets import (QDialog, QFileDialog, QGridLayout,
                             QLabel, QPushButton, QWidget, QVBoxLayout, QMainWindow)
import cv2 as cv
import numpy as np



#子窗口，用于选择要处理的图片以及处理方式
class Child(QDialog):
    
    def __init__(self, MainWindow):
        super().__init__()
        
        
        self.main = MainWindow              #与主窗口连接
        self.flag = 0                       #指示操作的图片（左或右）
        self.text = ['Left', 'Right']
        self.resize(50,200)
        self.btnSharpen = QPushButton('Sharpen', self)
        self.btnFlip = QPushButton('Flip', self)
        self.btnBlur = QPushButton('Blur', self)
        self.btnEdge = QPushButton('Edge', self)
        self.btnObject = QPushButton('Left', self)
        
        #窗口布局
        layout = QGridLayout(self)
        layout.addWidget(self.btnObject, 4, 1, 1, 1)
        layout.addWidget(self.btnBlur, 4, 2, 1, 1)
        layout.addWidget(self.btnSharpen, 4, 3, 1, 1)
        layout.addWidget(self.btnFlip, 4, 4, 1, 1)
        layout.addWidget(self.btnEdge, 4, 5, 1, 1)
         
        #信号与相应图像处理函数连接
        self.btnSharpen.clicked.connect(self.Sharpen)
        self.btnFlip.clicked.connect(self.Flip)
        self.btnBlur.clicked.connect(self.Blur)
        self.btnEdge.clicked.connect(self.Edge)
        
        #改变操作对象
        self.btnObject.clicked.connect(self.Object)

    def Object(self):
        self.flag = 1 - self.flag
        self.btnObject.setText(self.text[self.flag])
    
    #模糊处理
    def Blur(self):
        img = self.main.img[self.flag]
        if img.size == 1:
            return

        img = cv.blur(img, (5, 5))

        self.main.refreshShow(img, self.main.label[self.flag])
        self.main.img[self.flag] = img
   
    #锐化处理     
    def Sharpen(self):
        img = self.main.img[self.flag]
        if img.size == 1:
            return
        #kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]], np.float32)
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]], np.float32)
        img = cv.filter2D(img, -1, kernel=kernel)
        self.main.refreshShow(img, self.main.label[self.flag])
        self.main.img[self.flag] = img
    
    #翻转处理    
    def Flip(self):
        img = self.main.img[self.flag]
        if img.size == 1:
            return
        img = cv.flip(img, -1)
        self.main.refreshShow(img, self.main.label[self.flag])
        self.main.img[self.flag] = img
    
    #提取边缘
    def Edge(self):
        img = self.main.img[self.flag]
        if img.size == 1:
            return
        blurred = cv.GaussianBlur(img, (3, 3), 0)
        gray = cv.cvtColor(blurred, cv.COLOR_RGB2GRAY)
        img = cv.Canny(gray, 50, 150)
        
        #将灰度图转化为RGB图
        img = img[:, :, np.newaxis]
        img = np.concatenate((img, img, img), axis=2)
        
        self.main.refreshShow(img, self.main.label[self.flag])
        self.main.img[self.flag] = img





#显示人脸匹配结果
class MatchWindow(QMainWindow):
    
    def __init__(self, img):
        super().__init__()
        self.resize(250,150)
        self.img = img        
        
        #设置文字位置
        self.central_widget = QWidget()               
        self.setCentralWidget(self.central_widget)    
        lay = QVBoxLayout(self.central_widget)        
        self.label = QLabel(self)
        lay.addWidget(self.label)
    
    #向API发送请求并接收结果
    def showtext(self):
        img_str = self.Encode()
        request_url = "https://aip.baidubce.com/rest/2.0/face/v3/match"
        
        #存储图片信息
        data = []
        for i in range(2):
            a = {"image": img_str[i], "image_type": "BASE64"}
            data.append(a)
        data = json.dumps(data)
        
        access_token = '24.9f1ce0354f0651d68307b77fa6bf9211.2592000.1555860813.282335-15827967'
        request_url = request_url + "?access_token=" + access_token
        header = {'Content-Type': 'application/json'}
        r = requests.post(request_url, data=data, headers=header)
        r = r.json()
        
        if r['error_code'] == 222202:
            text = 'No face in the image!'
        elif r['error_code'] ==222203:
            text = 'Please open two images!'
        else:
            score = r['result']['score']
            text = ('The matching score is %.2f' %score)
        self.label.setText(text)
        self.show()
        

    #将图片转为BASE64编码       
    def Encode(self):
        img_str = []
        for i in range(2):
            _, buffer = cv.imencode('.jpg', self.img[i])
            str = base64.b64encode(buffer)
            str = str.decode()
            img_str.append(str)
        return img_str






#选择要存储的图片（左或右）        
class SaveWindow(QDialog):
    
    def __init__(self, img):
        self.img = img
        super().__init__()
        self.resize(250, 150)
        self.btnLeft = QPushButton('Left', self)
        self.btnRight = QPushButton('Right', self)
        self.label = QLabel()
        
        
        layout = QGridLayout(self)
        layout.addWidget(self.label, 0, 1, 1, 4)
        layout.addWidget(self.btnLeft, 1, 1, 1, 1)
        layout.addWidget(self.btnRight, 1, 3, 1, 1)
        
        self.label.setText('Which image do you want to save?')
        
        self.btnLeft.clicked.connect(self.Left)
        self.btnRight.clicked.connect(self.Right)
        
        
    def Left(self):
        self.flag = 0
        self.saveSlot()
    def Right(self):
        self.flag = 1
        self.saveSlot()
        
    def saveSlot(self):
        fileName, tmp = QFileDialog.getSaveFileName(
        self, 'Save Image', './__data', '*.png *.jpg *.bmp', '*.png')
        
        img = self.img[self.flag]
        
        if fileName is '':
            return
        if img.size == 1:
            return

        # 调用opencv写入图像
        cv.imwrite(fileName, img)