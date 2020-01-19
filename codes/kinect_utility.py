'''
created on Jan 10th 2020
@author: Rajitha Hathurusinghe 
'''
import numpy as np
from numpy import linalg as LA


def getChestDistanceFromRadars(joint_list): #TODO getting coordinates from a config
    rd1=np.array([0, -2.08, 0]) #Radar-1 coordinate
    rd1=np.transpose(rd1)
    rd1=rd1.reshape(3,1)
    rd2=np.array([1.55, -2.08, 1.24])#Radar-2 coordinate
    rd2=np.transpose(rd2)
    rd2=rd2.reshape(3,1)
    rd3=np.array([0, -1.74, 3.41]) #radar-3 coordinate
    rd3=np.transpose(rd3)
    rd3=rd3.reshape(3,1)
    alpha=-np.pi/6
    Rotx=np.array([ [1,0,0],
                    [0,np.cos(alpha),-np.sin(alpha)],
                    [0,np.sin(alpha),np.cos(alpha)] ])
    x_rot=np.matmul(Rotx,joint_list)
    x_rot=x_rot.reshape(3,1)
    conv_cord=np.subtract(x_rot,np.array([ [0], [2.11], [0] ])) #Shifting to new origin
    #Calculate the distance  from each radar
    rd1_dist=LA.norm(np.subtract(rd1,conv_cord),2)
    rd2_dist=LA.norm(np.subtract(rd2,conv_cord),2)
    rd3_dist=LA.norm(np.subtract(rd3,conv_cord),2)
    # rd_dist=np.array([rd1_dist,rd2_dist,rd3_dist])
    return([rd1_dist,rd2_dist,rd3_dist])
    # return [1.809, 1.809, 1.809]


#15 sec block of kinect shoulder joint data    
def activityDetection(input_bloc):
    blc_std=np.std(input_bloc*1/1000, axis=0,dtype=np.float64,ddof=1)
    blc_std=blc_std.reshape(3,1)
    th = 0.65
    if blc_std[0][0]<th and blc_std[1][0]<th and blc_std[2][0]<th:
        det_activity=1
    else:
        det_activity=0
    
    return(det_activity)