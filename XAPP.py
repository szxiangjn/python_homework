# -*- coding: utf-8 -*-
"""
Created on Sat Mar 16 20:33:48 2019

@author: 70437
"""

import sys
import cv2 as cv
import numpy as np
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import (QDialog, QApplication, QFileDialog, QGridLayout,
                             QLabel, QPushButton)
from subWindow import Child, MatchWindow, SaveWindow




class Example(QDialog):
    
    def __init__(self):
        #初始化用于存储两张图片的list
        self.img = [np.ndarray(()), np.ndarray(())]
        self.img_num = 0
        
        #初始化子窗口类
        self.child = Child(self)
        self.MatchWindow = MatchWindow(self.img)
        self.SaveWindow = SaveWindow(self.img)
        
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.resize(350, 500) 
        self.setWindowTitle('XApp')
        
        self.btnOpen = QPushButton('Open', self)
        self.btnSave = QPushButton('Save', self)
        self.btnProcess = QPushButton('Process', self)
        self.btnMatch = QPushButton('Match', self)
        self.btnQuit = QPushButton('Quit', self)
        
        #用于分别显示两张图片
        self.label = [QLabel(), QLabel()]             
        
        layout = QGridLayout(self)

        #窗口布局
        layout.addWidget(self.label[0], 0, 1, 3, 4)
        layout.addWidget(self.label[1], 0, 4, 3, 4)
        layout.addWidget(self.btnOpen, 4, 1, 1, 1)
        layout.addWidget(self.btnProcess, 4, 2, 1, 1)
        layout.addWidget(self.btnMatch, 4, 3, 1, 1)
        layout.addWidget(self.btnSave, 4, 4, 1, 1)
        layout.addWidget(self.btnQuit, 4, 5, 1, 1)
        
        #信号与相应的槽函数连接
        self.btnOpen.clicked.connect(self.openSlot)
        self.btnSave.clicked.connect(self.SaveWindow.show)        
        self.btnQuit.clicked.connect(self.close)
        self.btnProcess.clicked.connect(self.child.show)
        self.btnMatch.clicked.connect(self.MatchWindow.showtext)
        
    def openSlot(self):
        
        #最多同时打开两张图片
        if self.img_num > 1:
            return
        
        # 调用打开文件diglog
        fileName, tmp = QFileDialog.getOpenFileName(
            self, 'Open Image', './__data', '*.png *.jpg *.bmp')

        if fileName is '':
            return
        
        # 采用opencv函数读取数据
        img = cv.imread(fileName, 1)
        self.img[self.img_num] = img
        if img.size == 1:
            return
        
        #图片显示在相应位置
        self.refreshShow(img, self.label[self.img_num])
        
        self.img_num = self.img_num + 1
       
    def refreshShow(self, img, label):
        # 提取图像的尺寸和通道, 用于将opencv下的image转换成Qimage
        height, width, channel = img.shape
        bytesPerLine = 3 * width
        self.qImg = QImage(img.data, width, height, bytesPerLine,
                           QImage.Format_RGB888).rgbSwapped()

        # 将Qimage显示出来
        label.setPixmap(QPixmap.fromImage(self.qImg))


if __name__ == '__main__':
    if not QApplication.instance():
        a = QApplication(sys.argv)
    else:
        a = QApplication.instance()
    example = Example()
    example.show()
    sys.exit(a.exec_())        