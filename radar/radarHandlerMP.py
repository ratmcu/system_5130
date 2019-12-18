'''
created on Mar 24, 2017
@author: isuru, modified by rajitha to expoit multiprocessing to avoid frame jitter 12/24/2018
'''
from pymoduleconnector import ModuleConnector
import time
import threading
import queue
import csv
import numpy as np
import sys
import threading
import queue
import copy
from io import open
import multiprocessing
 
# end of the threading based radar thread class

class CollectionThreadX4MP(multiprocessing.Process):
    def __init__(self, name, stopEvent, radarSettings, baseband = False, fs = 17, radarPort='/dev/ttyACM0', dataQueue=None):
        multiprocessing.Process.__init__(self)
        self.exit = multiprocessing.Event()
        self.name = name
        self.stopEvent = stopEvent
        self.radarDataQ = dataQueue
        self.radarPort = radarPort
        self.radarSettings = radarSettings
        self.fs = fs
        self.baseband = baseband
        print ('Collection thread initialized')

    def run(self):
        print ('Initializing radar')
        self.reset(self.radarPort)
        self.mc = ModuleConnector(self.radarPort)
        self.radarObject = self.mc.get_xep()
        while self.radarObject.peek_message_data_float():
            self.radarObject.read_message_data_float()
        # Set DAC range
        time.sleep(3)
        self.radarObject.x4driver_set_dac_min(self.radarSettings['DACMin'])
        self.radarObject.x4driver_set_dac_max(self.radarSettings['DACMax'])

        # Set integration
        self.radarObject.x4driver_set_iterations(self.radarSettings['Iterations'])
        self.radarObject.x4driver_set_pulses_per_step(self.radarSettings['PulsesPerStep'])
        self.radarObject.x4driver_set_frame_area(self.radarSettings['FrameStart'],self.radarSettings['FrameStop'])
        if self.baseband:
            self.radarObject.x4driver_set_downconversion(1)
        self.radarObject.x4driver_set_fps(self.fs)

        self.clearBuffer()
        startTime = time.time()
        print((self.radarObject.get_system_info(0x07)))

        print ('Started radar data collection')
        while not self.exit.is_set():
            currentTime = time.time()
            radarFrame = self.radarObject.read_message_data_float().get_copy()
            self.radarDataQ.put([currentTime, radarFrame])
        self.radarObject.x4driver_set_fps(0) # stop the radar
        print('radar stopped')
        
    def reset(self,device_name):
        mc = ModuleConnector(device_name)
        r = mc.get_xep()
        r.module_reset()
        mc.close()
        time.sleep(3)
    
    def readFrame(self):
        """Gets frame data from module"""
        d = self.radarObject.read_message_data_float()
        return d.get_copy()

    def clearBuffer(self):
        """Clears the frame buffer"""
        while self.radarObject.peek_message_data_float():
            _ = self.radarObject.read_message_data_float()
            
    def shutdown(self):
        print ("Shutdown of radar process initiated")
        
        #self.exit.set()
