'''
created on Jan 10th 2020
@author: Rajitha Hathurusinghe 
'''
import sys
import time
import os
import glob
import collections
import configparser
import multiprocessing as mp
import numpy as np
import pandas as pd

sys.path.append('..')
from radar.xethru_radar import XethruRadar, XethruRadarDummy
from kinect.kinect_bridge import KinectBridge, KinectBridgeDummy
from consumer.consumer_process import ConsumerMP
import atexit 

import logging
logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)
# logging.getLogger().setLevel(logging.INFO)
# logging.getLogger('system').debug('bah')

def exit_handler(exit_signals):
    print ('system is ending!')
    for i, event in enumerate(exit_signals):
        print ('signalling the device process {0} to exit'.format(i))
        event.set()
    
if __name__ == '__main__':
    configparser = configparser.ConfigParser()
    configparser.read('config.ini')
    print(configparser.sections())
    # print(configparser['kinect1']['port'])
    # print('done!!')
    # create runnable radars and the listner
    devices = {}
    radar_list = []    
    devices.update({'radars': radar_list})
    kinect_list = []    
    devices.update({'kinects': kinect_list})
    exit_signals = []   
    for section in configparser.sections(): 
        #TODO: seperation of config passing and device creation
        if section == 'system':
                chunk_size = configparser['system'].getint('chunk_size', 15) 
                sample_skip = configparser['system'].getint('sample_skip', 5) 
                offline = configparser['system'].getboolean('offline', False) 
                data_available = configparser['system'].getboolean('data', False) 
                print(chunk_size, sample_skip) 
        for i in range(4):           
            ## add the devices to the dictonary
            if section == 'radar{0}'.format(i):
                try:
                    port = configparser['radar{0}'.format(i)]['port']
                    fs = configparser['radar{0}'.format(i)].getfloat('fs', 17.0)
                except KeyError as e:
                    raise Exception('incomplete config.ini config file \
                                    missing key {0}'.format(e))
                print(section, port, fs) 
                if offline:
                    if data_available:
                        data_file = configparser['radar{0}'.format(i)]['file']
                    else:
                        data_file = None
                    radar = XethruRadarDummy(i, port, fs, data_file)
                else:
                    radar = XethruRadar(i, port, fs)
                plate = collections.deque(maxlen=int(chunk_size*fs))
                radar_entry = {'name': section, 'fs': fs, 'process': radar,
                            'queue': radar.dataQ, 'event': radar.stopEvent, 
                            'plate': plate} 
                exit_signals.append(radar.stopEvent)
                radar_list.append(radar_entry)

            if section == 'kinect{0}'.format(i):
                try:
                    port = configparser['kinect{0}'.format(i)].getint('port', 27012)
                    fs = configparser['kinect{0}'.format(i)].getfloat('fs', 1.0)
                except KeyError as e:
                    raise Exception('incomplete config.ini config file \
                                    missing key {0}'.format(e))
                print(section, port, fs)
                if offline:
                    if data_available:
                        data_file = configparser['kinect{0}'.format(i)]['file']
                    else:
                        data_file = None
                    kinect = KinectBridgeDummy(i, port, fs, data_file)
                else:
                    kinect = KinectBridge(i, port, fs)

                plate = collections.deque(maxlen=int(chunk_size*fs))
                kinect_entry = {'name': section, 'fs': fs, 'process': kinect,
                            'queue': kinect.dataQ, 'event': kinect.stopEvent, 
                            'plate': plate} 
                exit_signals.append(kinect.stopEvent)
                kinect_list.append(kinect_entry)
    
    
    chunk_queue = mp.Queue()

    ##starting all the devices
    for device_type in devices.keys():
        print(device_type)
        for entry in devices[device_type]:  # get from queue and add to the plate
            logging.getLogger('system').debug(f'starting device {entry["name"]}')
            entry['process'].start()
    # sys.exit(0)
    consumer = ConsumerMP()
    exit_signals.append(consumer.stopEvent)
    consumer.start()
    atexit.register(exit_handler, exit_signals)  
    
    
    split_time = time.time()
    while(1):  
        try:           
        # loop
            # pop from each queue and add to the current chunk(eg 15s long deque)  
            # probably with a label? then remove the gap of arbitarary old elemnts
            # we'll be adding the raw data for the queue now, 
            # it'd be the duty of the user process to do the conversions.
            # can assign to the processes that can save to the disk or process
            for device_type in devices.keys():
                for entry in devices[device_type]:  # get from queue and add to the plate
                    # logging.getLogger('system').debug(f'taking data from {entry["name"]}')
                    if not entry['queue'].empty():
                        entry['plate'].append(entry['queue'].get())
            if (time.time()-split_time) > chunk_size:
                split_time = time.time()
                chunk_dict = {}
                for device_type in devices.keys():
                    chunk_dict.update({device_type:{}})
                    for entry in devices[device_type]:  # get from plate and add to the chunk
                        chunk_dict[device_type].update({entry['name'] : entry['plate'].copy()}) # add a copy to the chunk 
                        entry['plate'].clear()                      # clear the whole plate,
                        # TODO: only the unwanted last frames has to be cleared 
                consumer.chunkQ.put(chunk_dict)
        except :
            sys.exit(1)