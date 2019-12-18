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
# from radar.radarHandlerMP import CollectionThreadX4MP
from radar.xethru_radar import XethruRadar, XethruRadarDummy
import atexit


# import logging
# logger1 = logging.getLogger()
# logger1.setLevel(logging.DEBUG)
# logger1.setLevel(0)

import logging
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
# logging.getLogger().setLevel(logging.INFO)
# logging.getLogger('system').debug('bah')

def exit_handler(radar_signals):
    print ('system is ending!')
    for i, event in enumerate(radar_signals):
        print ('signalling the radar process {0} to exit'.format(i))
        event.set()
    

if __name__ == '__main__':
    configparser = configparser.ConfigParser()
    configparser.read('config.ini')
    print(configparser.sections())
    print(configparser['radar1']['port'])
    print('done!!')
    # create runnable radars and the listner
    devices = {}
    radar_list = []
    radar_signals = []
    devices.update({'radars': radar_list})

    for i, section in enumerate(configparser.sections()): #TODO: seperation of config passing and device creation
        if section == 'system':
           chunk_size = configparser['system'].getint('chunk_size', 15) 
           sample_skip = configparser['system'].getint('sample_skip', 5) 
        if section == 'radar{0}'.format(i):
            try:
                port = configparser['radar{0}'.format(i)]['port']
                fs = configparser['radar{0}'.format(i)].getfloat('radar_fs', 17.0)
            except KeyError as e:
                raise Exception('incomplete config.ini config file missing key {0}'.format(e))
            print(section, port, fs) 
            # radar = XethruRadar(i, port, fs)
            radar = XethruRadarDummy(i, port, fs)
            plate = collections.deque(maxlen=int(chunk_size*fs))
            radar_entry = {'name': section, 'process': radar, 'queue': radar.radarDataQ, 'event': radar.radarStopEvent, 'plate':plate} 
            radar_signals.append(radar.radarStopEvent)
            radar_list.append(radar_entry)
            # radar.start()
    
    atexit.register(exit_handler, radar_signals)  
    split_time = time.time()
    while(1):             
    # loop
        # pop from each queue and add to the current chunk(eg 15s long deque)  probably with a label? then remove the gap of arbitarary old elemnts
        # we'll be adding the raw data for the queue now, it'd be the duty of the user process to do the conversions.
        # can assign to the processes that can save to the disk or process
        for device_type in devices.keys():
            for entry in devices[device_type]:  # get from queue and add to the plate
                logging.getLogger('system').debug(f'taking data from {entry["name"]}')
                entry['plate'].append(plate['queue'].get())        