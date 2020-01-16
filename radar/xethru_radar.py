import time
import threading
import multiprocessing as mp
from numpy import genfromtxt
import pandas as pd
import numpy as np

# from radar.radarHandlerMP import CollectionThreadX4MP

# def getConfig(configparser):
#         configparser = configparser.ConfigParser()
#         configparser.read('config.ini')
#         config = configparser[configparser['DEFAULT']['config_to_use']]
#         radar_fs = config.getfloat('radar_fs', 17.0)
#         createRadarSettingsDict('x4')

# def createRadarSettingsDict(moduleName):
#     radarSettings = {}
#     if moduleName == 'x2':
#         radarSettings['PGSelect'] = 6
#         radarSettings['FrameStitch'] = 3
#         radarSettings['SampleDelayToReference'] = 2.9e-9
#         radarSettings['Iterations'] = 50
#         radarSettings['DACStep'] = 4
#         radarSettings['DACMin'] = 0
#         radarSettings['DACMax'] = 8191
#         radarSettings['PulsesPerStep'] = 16
#         radarSettings['Resolution'] = 3.90625 / 1000  # X2
#         radarSettings['RadarType'] = 'X2'
#     elif moduleName == 'x4':
#         radarSettings['Iterations'] = 16
#         radarSettings['DACMin'] = 949
#         radarSettings['DACMax'] = 1100
#         radarSettings['PulsesPerStep'] = 26
#         radarSettings['FrameStart'] = 0
#         radarSettings['FrameStop'] = 9.75
#         radarSettings['DACStep'] = 1  
#         radarSettings['Resolution'] = 51.8617 / 1000  # X4
#         radarSettings['RadarType'] = 'X4'
#     return radarSettings

class XethruRadar():  
    def __init__(self, number, port, frequency):
        self.radar_fs = frequency
        self.createRadarSettingsDict('x4')        
        self.dataQ = mp.Queue()
        self.stopEvent = mp.Event()
        self.radarThread = CollectionThreadX4MP('radarThreadX4_{0}'.format(number), self.radarStopEventMP, self.radarSettings, 
                                                baseband=True, fs = self.radar_fs, dataQueue=self.dataQ, radarPort=port)

    def createRadarSettingsDict(self, moduleName):
        self.radarSettings = {}
        if moduleName == 'x2':
            self.radarSettings['PGSelect'] = 6
            self.radarSettings['FrameStitch'] = 3
            self.radarSettings['SampleDelayToReference'] = 2.9e-9
            self.radarSettings['Iterations'] = 50
            self.radarSettings['DACStep'] = 4
            self.radarSettings['DACMin'] = 0
            self.radarSettings['DACMax'] = 8191
            self.radarSettings['PulsesPerStep'] = 16
            self.radarSettings['RADAR_RESOLUTION'] = 3.90625 / 1000  # X2
            self.radarSettings['RadarType'] = 'X2'
        elif moduleName == 'x4':
            self.radarSettings['Iterations'] = 16
            self.radarSettings['DACMin'] = 949
            self.radarSettings['DACMax'] = 1100
            self.radarSettings['PulsesPerStep'] = 26
            self.radarSettings['FrameStart'] = 0
            self.radarSettings['FrameStop'] = 9.75
            self.radarSettings['DACStep'] = 1  # This value is NOT USED. Just put here for the normalization
            self.radarSettings['RADAR_RESOLUTION'] = 51.8617 / 1000  # X4
            self.radarSettings['RadarType'] = 'X4'

class XethruRadarDummy(mp.Process):
    def __init__(self, number, port, frequency , file = None):
        mp.Process.__init__(self)  
        self.fs = frequency
        self.radarDataQ = mp.Queue()
        self.stopEvent = mp.Event()
        self.number = number
        self.file = file
    def run(self):
        print ('Initializing dummy radar {0}'.format(self.number))
        print ('Started radar data collection')
        oldTime = time.time()
        currentTime = time.time()
        if self.file: 
            csv_np =  genfromtxt(self.file, dtype=complex, delimiter=',')                
            while not self.stopEvent.is_set():
                for row in csv_np:
                    while (currentTime - oldTime) < (1.0/self.fs): #TODO: find a better
                        currentTime = time.time()
                    oldTime = time.time()
                        # currentTime = time.time()
                    time_stamp = row[0]
                    real = []
                    imag = []
                    for col in row[1:]:
                        real.append(col.real)
                        imag.append(col.imag)
                    # print(real)
                    real.extend(imag)
                    self.radarDataQ.put([currentTime, real])
                # oldTime = time.time()
                    
        else:
            while not self.stopEvent.is_set():
                if (currentTime - oldTime) > (1.0/self.fs):
                    oldTime = time.time()
                    currentTime = time.time()
                    radarFrame = [ complex(i, i) for i in range(180) ] 
                    self.radarDataQ.put([currentTime, radarFrame])
                currentTime = time.time()
                # else:            
        print('radar stopped')
 
    def shutdown(self):
        print ("Shutdown of radar process initiated")
        self.stopEvent.set()