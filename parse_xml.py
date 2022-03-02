from xml.dom.minidom import parse
import os
from numpy import float32
def getTargetFileTypePath(currentPath,target,targetList):
    #列出当前路径下的所有子文件和文件夹
    FolderList=os.listdir(currentPath)
    for x in FolderList:
        #寻找对应后缀名的文件，找到后加入列表中
        if x.endswith(target):
            targetList.append(currentPath+"\\"+x)
            continue
        #防止程序尝试进入非文件夹类的目录
        elif x.find(".")!=-1:
            continue
        #递归调用
        sonPath=currentPath+"\\"+x
        getTargetFileTypePath(sonPath,target,targetList)
    return
# 整理xml文件中的类名
def sortClasses(filepath,keywords,savepath=os.getcwd()+"\\sortedClasses\\classes.txt"):
    wordsList=[]
    for file in filepath:
        xml=parse(file)
        document=xml.documentElement
        targets=document.getElementsByTagName(keywords)
        for target in targets:
            words=target.childNodes[0].data
            if words not in wordsList:
                wordsList.append(words)
    classfile=open(savepath,'w') 
    for classname in wordsList:
        classfile.write(classname)
        classfile.write('\n')
    classfile.close()
    print(wordsList)
    return
# 生成类的字典，键为类名，值为类序号
def createDictionary(classpath=os.getcwd()+"\\sortedClasses\\classes.txt"):
    classDictionary={}
    classfile=open(classpath,'r')
    classList=classfile.readlines()
    classfile.close()
    classCount=1
    for classname in classList:
        classname=classname.replace("\n","")
        classDictionary.update({classname:classCount})
        classCount+=1
    return classDictionary
# 将xml格式文件转换为class x,y,w,h格式（x,y,w,h为相对值）,存储在XML文件的同级文件夹中
def XML_TO_YOLO(filepath,mode='centralized'):
    classDictionary=createDictionary()
    if mode =='seperated':
        for file in filepath:
            xml=parse(file)
            document=xml.documentElement
            size=document.getElementsByTagName("size")
            items=document.getElementsByTagName("object")
            width=float32(size[0].getElementsByTagName("width")[0].childNodes[0].data)
            height=float32(size[0].getElementsByTagName("height")[0].childNodes[0].data)
            labelpath=file.replace(".xml",".txt")
            labelfile=open(labelpath,'w')
            # 将单个xml文件中的所有objects包含的参数转换为yolo格式，并写入txt文件中
            for item in items:
                name=item.getElementsByTagName("name")[0].childNodes[0].data
                xmin=float32(item.getElementsByTagName("xmin")[0].childNodes[0].data)
                ymin=float32(item.getElementsByTagName("ymin")[0].childNodes[0].data)
                xmax=float32(item.getElementsByTagName("xmax")[0].childNodes[0].data)
                ymax=float32(item.getElementsByTagName("ymax")[0].childNodes[0].data)
                xcenter=(xmax-xmin)/(2.0*width)
                ycenter=(ymax-ymin)/(2.0*height)
                relative_width=(xmax-xmin)/width
                relative_height=(ymax-ymin)/height
                classIndex=classDictionary[name]
                labelfile.write(str(classIndex)+' '+str(xcenter)+' '+str(ycenter)+' '+str(relative_width)+' '+str(relative_height)+'\n')
            labelfile.close()
    elif mode=='centralized':
        labelpath=os.getcwd()+"\\labels\\labels.txt"
        labelfile=open(labelpath,'w')
        for file in filepath:
            xml=parse(file)
            document=xml.documentElement
            size=document.getElementsByTagName("size")
            items=document.getElementsByTagName("object")
            width=float32(size[0].getElementsByTagName("width")[0].childNodes[0].data)
            height=float32(size[0].getElementsByTagName("height")[0].childNodes[0].data)
            # 将所有xml的数据写入到一个txt文件中
            for item in items:
                name=item.getElementsByTagName("name")[0].childNodes[0].data
                xmin=float32(item.getElementsByTagName("xmin")[0].childNodes[0].data)
                ymin=float32(item.getElementsByTagName("ymin")[0].childNodes[0].data)
                xmax=float32(item.getElementsByTagName("xmax")[0].childNodes[0].data)
                ymax=float32(item.getElementsByTagName("ymax")[0].childNodes[0].data)
                xcenter=(xmax-xmin)/(2.0*width)
                ycenter=(ymax-ymin)/(2.0*height)
                relative_width=(xmax-xmin)/width
                relative_height=(ymax-ymin)/height
                classIndex=classDictionary[name]
                labelfile.write(str(classIndex)+' '+str(xcenter)+' '+str(ycenter)+' '+str(relative_width)+' '+str(relative_height)+'\n')
        labelfile.close()  
    return
filepath=os.getcwd()
filelist=[]
getTargetFileTypePath(filepath,".xml",filelist)
sortClasses(filelist,"name")
XML_TO_YOLO(filelist,mode='centralized')