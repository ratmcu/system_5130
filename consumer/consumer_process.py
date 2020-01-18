import multiprocessing as mp
import time
import sys
sys.path.append('..')
from codes.bin_finder import binIndex, denoiseRadar
from codes.kinect_utility import getChestDistanceFromRadars, activityDetection
from codes.algorithm_utility import getAlgoList
import numpy as np
from codes.radar_conversion import radarToNp, framesToNp, toRawRadarFrame

class ConsumerMP(mp.Process):
    def __init__(self):
        mp.Process.__init__(self)  
        self.chunkQ = mp.Queue()
        self.stopEvent = mp.Event()
        self.algo_list = getAlgoList()
    def run(self):
        while not self.stopEvent.is_set():
            if not self.chunkQ.empty():
                chunk = self.chunkQ.get()
                # print(chunk.keys())
                print(f"started at {time.strftime('%X')}")
                # create data into two lists based on person id
                try:
                    kinect_data = chunk['kinects']
                except:
                    raise BaseException('chunk doesn\'t contain \'kinect\' data' )
                
                try:
                    radar_data = chunk['radars']
                except:
                    raise BaseException('chunk doesn\'t contain \'radar\' data' )
                
                skeleton_data = {}
                # print(f"kinect_data: {kinect_data}")  
                for kinect in kinect_data.keys():
                    # print(kinect_data[kinect])
                    for skeleton_list in kinect_data[kinect]:
                        # print(skeleton_list)
                        for skeleton in skeleton_list[1]:
                            if 'person{0}'.format(skeleton[0]) in skeleton_data:
                                skeleton_data['person{0}'.format(skeleton[0])].append(skeleton[1:])
                            else:
                                skeleton_data['person{0}'.format(skeleton[0])] = [skeleton[1:]]
                # print(f"skeleton_data: {skeleton_data}")                
                # get chest position coordinates 
                if skeleton_data:
                    chest_positions = {}
                    for person in skeleton_data.keys():
                        chest_positions[person] = getChestDistanceFromRadars(np.asarray(skeleton_data[person][0])/1000)
                    # print(f"chest_positions: {chest_positions}")
                    
                    # denoise the radar signals first
                    denoised_radar_data = {}
                    np_radar_data = {}
                    for radar in radar_data.keys():
                        np_data = framesToNp(radar_data[radar])
                        np_radar_data[radar] = np_data
                        denoised_radar_data[radar] = denoiseRadar(np_data, 17)
                    # print(denoised_radar_data.keys())            
                # if 1 == 2:
                    # send to the bin finder and get the bin
                    # 6 bins
                    bin_index_dict = {} # each bin is for person number and will contain bin for each radar
                    for person in chest_positions.keys():
                        bins = {}
                        for radar, position in enumerate(chest_positions[person]):
                            if 'radar{0}'.format(radar+1) in denoised_radar_data.keys():
                                bins['radar{0}'.format(radar+1)] = binIndex(position, denoised_radar_data['radar{0}'.format(radar+1)])
                        bin_index_dict[person] = bins
                    # calculate the breathing rate now
                    # for each algorithm there will be an entry
                    # print(f"bin_index_dict: {bin_index_dict}")
                
                    breathing_rate_dict = {}
                    for person in bin_index_dict.keys():
                        breathing_rate_for_radar = {}
                        for radar in bin_index_dict[person].keys():
                            column_index = bin_index_dict[person][radar]
                            # target_bin = radar_data[radar[:,column_index:column_index+1]]
                            br_dict = {} # algo name and the rate realavant to 
                            for algo in self.algo_list:
                                # br_dict[algo['name']] = algo['function'](target_bin, radar_data[radar])
                                br_dict[algo['name']] = algo['function'](np.unwrap(np.angle(np_radar_data[radar][:,column_index])))
                            breathing_rate_for_radar[radar] = br_dict
                        breathing_rate_dict[person] = breathing_rate_for_radar

                    print(breathing_rate_dict)
                    # print(denoised_radar_data['radar1'][0])
                    print(f"finished at {time.strftime('%X')}")

                else:
                    print("zero people detected by kinect!")
                

                # run the breathing rate detection
        print('consumer process stopped')
 
    def shutdown(self):
        print ("Shutdown of radar process initiated")
        self.stopEvent.set()
    
