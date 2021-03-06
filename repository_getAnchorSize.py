import os
from matplotlib.cbook import maxdict
import numpy as np
import cv2 as cv
import time
class getAnchorSize:
    """
    Description:
    ============
        Creating a runnable instance.By running `instance.Run()`,this instance will 
    automatically calculate `k` cluster centers based on the parameters given defaultly.
    User can also designate certain parameters in order to cultivate expected results.
    ------------
    Parameters:
    ============
        `labelPath`:Indicates the absolute path of ground_truth file.It defaultly points at
        where the python file lies.Default ground_truth file name is `labels.txt`.
        `k`:  Indicates the number of anchors to be generated using `k-means`.
        `maxIterNum`: Maximun number of iteration.
        `drawDiagram`:Whether program will draw dynamic graphic to show the change of all cluster centers.
        `diagramOutPut`:Whether program will save the final diagram.Valid only when `drawDiagram==True`.
        `maxDrawNum`:Limiting the amount of boxes of one cluster center,in order to save system resources.
        `boxColor/clusterCenterColor`:`(B,G,R)` format tuple,determins the color of box/cluster center edge line.
        `origin`:Origin point.Determins where should the program start to draw boxes.It is the central point of boxes.
        `imgSize`:Determins the width and height of the picture used for showing boxes.
        `clusterSpacing`:Determins the spacing of k cluster centers.
        `zoomRatio`:Determins the zoom ratio of box's width and height.Used for adjusting box size to fit the size of `imgSize`.
    """
    def __init__(self,labelPath=os.getcwd()+"\\labels\\labels.txt",k=9,maxIterNum=1000,drawDiagram=False,diagramOutPut=False,
                diagramPath=os.getcwd()+"\\diagrams\\diagram.jpg",maxDrawNum=10,boxColor=(255,0,0),clusterCenterColor=(0,0,255),origin=(200,500),
                imgSize=(2000,2000),clusterSpacing=150,zoomRatio=5):
        self.labelPath=labelPath
        self.boxList=[]
        self.clusterCenters=[]
        self.k=k
        self.maxIterNum=maxIterNum
        self.drawDiagram=drawDiagram
        self.diagramOutPut=diagramOutPut
        self.diagramPath=diagramPath
        self.maxDrawNum=maxDrawNum
        self.boxColor=boxColor
        self.clusterCenterColor=clusterCenterColor
        self.origin=origin
        self.imgSize=imgSize
        self.clusterSpacing=clusterSpacing
        self.zoomRatio=zoomRatio
        self.errorList=[]
        self.warningList=[]
        self.programLogList=[]
        self.__programLogPath=os.getcwd()+"\\programLogs\\log.txt"
        self.__anchorPath=os.getcwd()+"\\anchors\\anchors.txt"
        self.__diagramSuffix='.jpg'
    def __checkError(self):
        integerDict={'k':self.k,                          'maxIterNum':self.maxIterNum,'maxDrawNum':self.maxDrawNum,
                     'clusterSpacing':self.clusterSpacing,'zoomRatio':self.zoomRatio}
        ConfirmMask={'y':True,'Y':True,'n':False,'N':False}
        def checkFloat(value,name):
            if  value-int(value)!=0 and value >=1:
                self.warningList.append('Warning: {0} should be an integer. Casting {0} to {1} .\n'.format(name,int(value)))
                
            elif value<1:
                self.errorList.append('Error: {} must be greater than 1.\n'.format(name))
            else:
                pass
            return value
        def checkColor(color):
            isRight=True
            for val in color:
                if val<0 or val>255:
                    isRight=False
                else:
                    pass
            return isRight
        try:
            labels=open(self.labelPath,'r')
            labels.close()
        except:
            self.errorList.append('Error: Invalid labelPath. Please reset the path.\n')
        for name in integerDict.keys():
            integerDict[name]=checkFloat(integerDict[name],name)
        self.k=int(self.k)
        self.maxIterNum=int(self.maxIterNum)
        self.maxDrawNum=int(self.maxDrawNum)
        self.clusterSpacing=int(self.clusterSpacing)
        self.zoomRatio=int(self.zoomRatio)
        if self.drawDiagram==False and self.diagramOutPut==True:
            self.warningList.append('Warning: Diagram would be saved only when drawDiagram==True.\n')
        else:
            pass
        if os.path.exists(self.diagramPath) and self.diagramPath.endswith(self.__diagramSuffix) and self.drawDiagram:
            print('Warning: Diagram has already exist.Would you rewrite it with the new image?\n[y/n]:')
            command=input()
            if command not in ConfirmMask.keys():
                (year,month,day,clock,minute,second)=time.localtime()[0:6]
                self.programLogList.append('{0}-{1}-{2} {3}:{4}:{5} :Rewrite diagram.Permission command input error.Set diagramOutPut==False\n'.format(year,month,day,clock,minute,second))
                self.diagramOutPut=False
            else:
                (year,month,day,clock,minute,second)=time.localtime()[0:6]
                self.programLogList.append('{0}-{1}-{2} {3}:{4}:{5} :Rewrite diagram.Permission passed. Rewrite:{6}\n'.format(year,month,day,clock,minute,second,ConfirmMask[command]))
                self.diagramOutPut=ConfirmMask[command]
        elif not self.diagramPath.endswith(self.__diagramSuffix):
            print('Invalid type of diagram.Set diagramPath to suitable path.\n')
            (year,month,day,clock,minute,second)=time.localtime()[0:6]
            self.diagramPath=os.getcwd()+"\\validDiagram.jpg"
            self.programLogList.append('{0}-{1}-{2} {3}:{4}:{5} :Invalid type of diagram.Set diagramPath to suitable path: {6}\n'.format(year,month,day,clock,minute,second,self.diagramPath))
        else:
            pass
        if not checkColor(self.clusterCenterColor):
            (year,month,day,clock,minute,second)=time.localtime()[0:6]
            self.programLogList.append('{0}-{1}-{2} {3}:{4}:{5} :Cluster center color invalid.Set it to default value.\n'.format(year,month,day,clock,minute,second))
            self.clusterCenterColor=(0,0,255)
        else:
            pass
        if not checkColor(self.boxColor):
            (year,month,day,clock,minute,second)=time.localtime()[0:6]
            self.programLogList.append('{0}-{1}-{2} {3}:{4}:{5} :Box color invalid.Set it to default value.\n'.format(year,month,day,clock,minute,second))
            self.boxColor=(255,0,0)
        else:
            pass
        for size in self.imgSize:
            if size<0 or size>2000:
                (year,month,day,clock,minute,second)=time.localtime()[0:6]
                self.programLogList.append('{0}-{1}-{2} {3}:{4}:{5} :Image size invalid.Set it to default value.\n'.format(year,month,day,clock,minute,second))
                self.imgSize=(2000,2000)
                break
            else:
                pass
        if self.origin[0]*self.origin[1]<0 or self.origin[0]>self.imgSize[0] or self.origin[1]>self.imgSize[1]:
                (year,month,day,clock,minute,second)=time.localtime()[0:6]
                self.programLogList.append('{0}-{1}-{2} {3}:{4}:{5} :Origin out of range.Set it to fit the image.\n'.format(year,month,day,clock,minute,second))
                self.origin=np.divide(self.imgSize,(10,4))
        else:
            pass
        if len(self.errorList)==0:
            warningLength=len(self.warningList)
            print("State check passsed. {0} Errors, {1} Warnings:\n".format(0,warningLength))
            if warningLength!=0:
                for warning in self.warningList:
                    print(warning)
                print("Confirm to run the program with all the warnings above.\n[y/n]:")
                command=input()
                if command in ConfirmMask.keys():
                    return ConfirmMask[command]
                else:
                    (year,month,day,clock,minute,second)=time.localtime()[0:6]
                    self.programLogList.append('{0}-{1}-{2} {3}:{4}:{5} :Running permission command input error. Exited.\n'.format(year,month,day,clock,minute,second))
                    return False
            else:
                return True
        else:
            return False
    def __getBoxes(self):
        labels=open(self.labelPath,'r')
        # labels??????????????????????????????????????????x,y,w,h???????????????anchor?????????????????????????????????w,h???????????????
        dataList=labels.readlines()
        boxList=[]
        for data in dataList:
            # ???????????????????????????classNum x y w h'\n'???5???????????????
            # ??????????????????h????????????????????????????????????????????????????????????????????????????????????15???????????????
            # ???split???????????????1???5??????????????????????????????4???5?????????????????????float32??????
            data=data.split(' ')
            width=np.float32(data[3])
            height=np.float32(data[4].replace('\n',''))
            boxList.append([width,height])
        labels.close()
        # ???boxList?????????numpy???????????????
        boxList=np.array(boxList)
        return boxList
    def __getRandomClusterCenters(self,boxList,k):
        # boxList.shape?????????[row,col]???????????????boxList.shape[0]??????boxList?????????
        # ???boxList?????????????????????????????????k?????????clusterCenters
        # clusterCenters?????????k???2?????????????????????????????????????????????????????????????????????[width,height]
        clusterCenters=boxList[np.random.choice(boxList.shape[0],k,replace=False)]
        return clusterCenters
    def getDistanceByIOU(self,boxa,boxb):
        """
        Parameters:
        ==========
        `boxa/boxb`:Two lists.Each one contains box width and height as format:`[width,height]`.
        `[attention]`:width and height are relative value.
        ----------
        Returns:
        ==========
        Out: FloatType value
            1-IoU value which represents the distance of two boxes.
        """
        # ???????????????????????????????????????
        interWidth=np.min([boxa[0],boxb[0]])
        interHeight=np.min([boxa[1],boxb[1]])
        # ????????????????????????
        boxaSquare=boxa[0]*boxa[1]
        # ??????????????????????????????
        boxbSquare=boxb[0]*boxb[1]
        interSquare=interHeight*interWidth
        # ??????????????????????????????
        unionSquare=boxaSquare+boxbSquare-interSquare
        return (1-(interSquare/unionSquare))
    def __getClusters(self,k,boxList,clusterCenters):
        clusters=[[] for a in range(k)]
        for box in boxList:
            distances=[]
            # ????????????????????????box???k???clusterCenter???????????????,?????????distances???
            for clusterCenter in clusterCenters:
                distance=getAnchorSize.getDistanceByIOU(self,box,clusterCenter)
                distances.append(distance)
            # memberIndex???distances????????????????????????,????????????????????????box??????????????????????????????
            memberIndex=distances.index(min(distances))
            clusters[memberIndex].append(box)
        return clusters
    def __updateClusterCenters(self,clusters,clusterNum):
        clusterAvg=[]
        for index in range(clusterNum):
            average=np.divide(np.sum(clusters[index],axis=0),(np.count_nonzero(clusters[index])/2))
            clusterAvg.append(average)
        return clusterAvg
    def getDiagonalAxis(self,box,originAxis=(0,0),offSets=(0,0),imgSize=(1000,1000),zoomRatio=1):#????????????????????????
        """
        Parameters:
        ==========
        `box`:List.Relative axis of box's width and height.Format as`[with,height]`.
        `originAxis`:Tuple.Origin axis of the box center.
        `offSets`:Tuple.Indicates the offsets in `x-axis` and `y-axis`.
        `imgSize`:Tuple.Indicates the absolute `width` and `height` of image.
        `zoomRatio`:Determins the zoom ratio of box's absolute width and height.Used for adjusting box size to fit the size of `imgSize`.
        ----------
        Returns:
        ==========
        Out: TupleLike
            Tuple containing the box's absolute `left-top` and `right-bottom` axis.
        """
        leftTop=(int(offSets[0]+originAxis[0]-0.5*(box[0]*imgSize[0]/zoomRatio)),
                int(offSets[1]+originAxis[1]-0.5*(box[1]*imgSize[1]/zoomRatio)))
        rightBottom=(int(offSets[0]+originAxis[0]+0.5*(box[0]*imgSize[0]/zoomRatio)),
                int(offSets[1]+originAxis[1]+0.5*(box[1]*imgSize[1]/zoomRatio)))
        return (leftTop,rightBottom)
    def __RunAndDraw(self,clusterCenters):
        iterationNum=0
        preDistance=[[] for a in range(self.k)]
        while True:
            # ??????????????????
            img = np.ones((self.imgSize[0],self.imgSize[1], 3), np.uint8)
            # ??????????????????????????????k??????,????????????????????????????????????????????????????????????
            clusters=getAnchorSize.__getClusters(self,self.k,self.boxList,clusterCenters) 
            # ????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????
            distances=[[] for a in range(self.k)]
            if iterationNum<=self.maxIterNum:
                for i in range(self.k):
                    boxes=clusters[i]
                    drawNum=0
                    for box in boxes:
                        if drawNum<=self.maxDrawNum:
                            leftTopBox,rightBottomBox=getAnchorSize.getDiagonalAxis(self,box,self.origin,(i*self.clusterSpacing,0),self.imgSize,self.zoomRatio)
                            img=cv.rectangle(img,leftTopBox,rightBottomBox,self.boxColor,1,cv.LINE_8)
                            drawNum+=1
                        distance=getAnchorSize.getDistanceByIOU(self,box,clusterCenters[i])
                        distances[i].append(distance)
                        distances[i].sort()
                    leftTopCenter,rightBottomCenter=getAnchorSize.getDiagonalAxis(self,clusterCenters[i],self.origin,(i*self.clusterSpacing,0),self.imgSize,self.zoomRatio)
                    img=cv.rectangle(img,leftTopCenter,rightBottomCenter,self.clusterCenterColor,2,cv.LINE_8)
                if iterationNum==0:
                    preDistance=distances
                    clusterCenters=getAnchorSize.__updateClusterCenters(self,clusters,self.k)
                    iterationNum+=1
                    continue
                if np.equal(np.array(distances,dtype="object"),np.array(preDistance,dtype="object")).all():
                    if self.diagramOutPut:
                        cv.imencode(self.__diagramSuffix,img)[1].tofile(self.diagramPath)
                        if not os.path.exists(self.diagramPath):
                            (year,month,day,clock,minute,second)=time.localtime()[0:6]
                            self.programLogList.append('{0}-{1}-{2} {3}:{4}:{5} :Failed to save diagram. Path<{6}> invalid.\n'.format(year,month,day,clock,minute,second,self.diagramPath))
                            break
                        else:
                            break
                    else:
                        break
                else:
                    preDistance=distances
            else:
                break
            cv.namedWindow("image")
            cv.imshow('image', img)
            key = cv.waitKey(50)
            if key == ord('1'):   # ???????????????????????????
                break
            # ??????????????????.????????????????????????????????????????????????
            print('***************Iteration: {iteration}***************\n'.format(iteration=iterationNum))
            for j in range(self.k):
                AVG=1-np.sum(distances[j])/len(distances[j])
                print('Cluster : {0} AVG_IOU={1}'.format(j+1,AVG))
            clusterCenters=getAnchorSize.__updateClusterCenters(self,clusters,self.k)
            # ????????????+1
            iterationNum+=1
        return (iterationNum,clusterCenters)
    def __RunWithoutDraw(self,clusterCenters):
        iterationNum=0
        preDistance=[[] for a in range(self.k)]
        while True:
            # ??????????????????????????????k??????,????????????????????????????????????????????????????????????
            clusters=getAnchorSize.__getClusters(self,self.k,self.boxList,clusterCenters)
            distances=[[] for a in range(self.k)]
            if iterationNum<=self.maxIterNum:
                for i in range(self.k):
                    boxes=clusters[i]
                    for box in boxes:
                        distance=getAnchorSize.getDistanceByIOU(self,box,clusterCenters[i])
                        distances[i].append(distance)
                        distances[i].sort()
                if iterationNum==0:
                    preDistance=distances
                    clusterCenters=getAnchorSize.__updateClusterCenters(self,clusters,self.k)
                    iterationNum+=1
                    continue
                # ???????????????distances????????????,???????????????
                if np.equal(np.array(distances,dtype="object"),np.array(preDistance,dtype="object")).all():
                    break
                else:
                    preDistance=distances
            else:
                break
            # ??????????????????.????????????????????????????????????????????????
            print('***************Iteration: {iteration}***************\n'.format(iteration=iterationNum))
            for j in range(self.k):
                AVG=1-np.sum(distances[j])/len(distances[j])
                print('Cluster : {0} AVG_IOU={1}'.format(j+1,AVG))
            clusterCenters=getAnchorSize.__updateClusterCenters(self,clusters,self.k)
            # ????????????+1
            iterationNum+=1
        return (iterationNum,clusterCenters)
    def Run(self):
        runningMask=getAnchorSize.__checkError(self)
        if runningMask:
            self.boxList=getAnchorSize.__getBoxes(self)
            self.clusterCenters=getAnchorSize.__getRandomClusterCenters(self,self.boxList,self.k)
            if self.k==1:
                iterationNum=0
                clusters=getAnchorSize.__getClusters(self,self.k,self.boxList,self.clusterCenters)
                self.clusterCenters=getAnchorSize.__updateClusterCenters(self,clusters,self.k)
                print("Notice: When k equals 1, program will only calculate average width and height of all ground_truth to generate the final cluster center.\n")
                print("Notice: When k equals 1, program will not save any diagram even if diagramOutPut is set to be True.\n")
            elif self.drawDiagram: 
                (iterationNum,self.clusterCenters)=getAnchorSize.__RunAndDraw(self,self.clusterCenters)
            elif not self.drawDiagram:
                (iterationNum,self.clusterCenters)=getAnchorSize.__RunWithoutDraw(self,self.clusterCenters)
            else:
                pass
            print("Iteration done. Final number of iterations: {}\n".format(iterationNum))
            print("{} different sizes of anchors as below:\n".format(self.k))
            # ?????????????????????k??????????????????
            anchorSquare=[]
            anchorFile=open(self.__anchorPath,'w')
            for index in range(self.k):
                anchorSquare.append(self.clusterCenters[index][0]*self.clusterCenters[index][1])
            anchorSerialIndex=np.argsort(anchorSquare,axis=0)
            for index in anchorSerialIndex:
                anchorFile.write('{},{}\n'.format(self.clusterCenters[index][0],self.clusterCenters[index][1]))
            anchorFile.close()
            for i in range(self.k):
                print("anchor: number {0} , width= {1}   height= {2}\n".format(i+1,self.clusterCenters[i][0],self.clusterCenters[i][1]))
            if os.path.exists(self.__programLogPath):
                logFile=open(self.__programLogPath,'a')
            else:
                logFile=open(self.__programLogPath,'w')
            (year,month,day,clock,minute,second)=time.localtime()[0:6]
            logFile.write('>>> {0}-{1}-{2} {3}:{4}:{5} :Running check success.\n'.format(year,month,day,clock,minute,second))
            for warnings in self.warningList:
                logFile.write(warnings)
                print(warnings)
            for logs in self.programLogList:
                logFile.write(logs)
                print(logs)
            logFile.close()
        else:
            print("Program exited with {0} errors and {1} warnings.Refer to program log in {2}".format(len(self.errorList),len(self.warningList),self.__programLogPath))
            if os.path.exists(self.__programLogPath):
                logFile=open(self.__programLogPath,'a')
            else:
                logFile=open(self.__programLogPath,'w')
            (year,month,day,clock,minute,second)=time.localtime()[0:6]
            logFile.write('>>> {0}-{1}-{2} {3}:{4}:{5} :Running check failed.\n'.format(year,month,day,clock,minute,second))
            for errors in self.errorList:
                logFile.write(errors)
            for warnings in self.warningList:
                logFile.write(warnings)
            for logs in self.programLogList:
                logFile.write(logs)
            logFile.close()
        return