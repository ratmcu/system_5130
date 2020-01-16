import socket
import sys
import multiprocessing as mp
import time
from numpy import genfromtxt
import pandas as pd
import numpy as np
"""
Created on Tue Jan 14 13:08:59 2020

@author: rnd
"""
def personList(x): #input row of the kinect csv file 
    person_list = []
    if x[1]=='Body ID: 1':
        x1=x.iloc[2]
        y1=x.iloc[3]
        z1=x.iloc[4]
        Position_1 = [0,x1,y1,z1]
        #
        x2=x.iloc[12]
        y2=x.iloc[13]
        z2=x.iloc[14]
        Position_2 = [1,x2,y2,z2]
        person_list=[Position_1,Position_2]
        #print(personlist)
    else:
        x1=x.iloc[12]
        y1=x.iloc[13]
        z1=x.iloc[14]
        Position_1 = [0,x1,y1,z1]
        #
        x2=x.iloc[2]
        y2=x.iloc[3]
        z2=x.iloc[4]
        Position_2 = [1,x2,y2,z2]
        person_list=[Position_1,Position_2]
    return([person_list])

class KinectBridge(mp.Process):  
    def __init__(self, number, port , frequency):
        mp.Process.__init__(self)
        self.dataQ = mp.Queue()
        self.stopEvent = mp.Event()
        self.port = port
        self.number = number
        self.fs = frequency
        s = None
        s = socket.socket(2, 2, 0)  # these values were taken from the c program, 
        s.bind(("127.0.0.1", port))
        print('opened socket')
        s.settimeout(3.0)
        data = s.recv(1024)
        # s.setblocking(True)
    def run(self):
        s = None
        connected = False
        while not self.stopEvent.is_set():
            s = socket.socket(2, 2, 0)
            s.bind(("127.0.0.1", self.port))
            print('opened socket')
            s.settimeout(3.0)
            while not connected:
                try:
                    data = s.recv(1024)
                    connected = True
                    break
                except:
                    print('timed out waiting for server')
                print('server alive and transmitting')

            s.settimeout(10.0) # if not we have to wait a forever to kill it
            
            try:
                data = s.recv(1024)
                # print('Received', str(data.decode("utf-8", errors='ignore')).split('\0')[0])                
            except:
                print('timed out waiting for server')
            try:
                coord_list = ast.literal_eval(data.decode("utf-8"))
                print(coord_list)
            except:
                print('malformed bytes receved {0}'.format(data.decode("utf-8")))
            self.dataQ.put(coord_list)   
        s.close()

    def shutdown(self):
        print ("Shutdown of radar process initiated")
        self.stopEvent.set()


class KinectBridgeDummy(mp.Process):
    def __init__(self, number, port, frequency, file = None):
        mp.Process.__init__(self)
        self.dataQ = mp.Queue()
        self.stopEvent = mp.Event()
        self.port = port
        self.number = number
        self.fs = frequency
        self.file = file
        # s = None
        # s = socket.socket(2, 2, 0)  # these values were taken from the c program, 
        # s.bind(("127.0.0.1", port))
        # print('opened socket')
        # s.settimeout(3.0)
        # data = s.recv(1024)
        # s.setblocking(True)
    def run(self):
        oldTime = time.time()
        currentTime = time.time()
        if self.file:
            kin_data = pd.read_csv(self.file)
            per_data = kin_data.iloc[1,:]
            per_list = personList(per_data)
            while not self.stopEvent.is_set():
                for entry in per_list:
                    while (currentTime - oldTime) < (1.0/self.fs): #TODO: find a better cpu hit, wait for termination
                        currentTime = time.time()
                    oldTime = time.time()
                    self.dataQ.put(entry) 
        else:
            while not self.stopEvent.is_set():
                if (currentTime - oldTime) > (1.0/self.fs):
                    oldTime = time.time()
                    currentTime = time.time()
                    coord_list = [[0, 100.0, 123.33, 23.45], [1, 100.0, 123.33, 23.45]]
                    self.dataQ.put(coord_list) 
                currentTime = time.time()

    def shutdown(self):
        print ("Shutdown of kinect dummy process initiated")
        self.stopEvent.set()
