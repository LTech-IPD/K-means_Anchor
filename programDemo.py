import os,numpy as np
from turtle import width
import repository_getAnchorSize as rg
import cv2
instance=rg.getAnchorSize()
# instance.Run() //需要进行锚框聚类时，解注释
dataFile=open(os.getcwd()+"\\anchors\\anchors.txt",'r')
datas=dataFile.readlines()
dataFile.close()
# converF=open(os.getcwd()+"\\anchors\\acs.txt",'w')
anchors=[]
for data in datas:
    data=data.strip('\n')
    data=data.split(',')
    width=np.float32(data[0])
    height=np.float32(data[1])
    anchors.append([width,height])
#   converF.write("{},{} ".format(width,height))
#converF.close()
img=np.ones((416,416,3),np.uint8)
for anchor in anchors:
    (leftTop,rightBottom)=instance.getDiagonalAxis(anchor,(213,213),(0,0),(416,416),1)
    img=cv2.rectangle(img,leftTop,rightBottom,(0,0,255),1,cv2.LINE_8)
cv2.imencode('.jpg',img)[1].tofile('anchorDiagram\\anchors.jpg')
