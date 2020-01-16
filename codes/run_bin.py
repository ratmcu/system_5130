# -*- coding: utf-8 -*-
"""
Created on Thu Jan  2 21:04:10 2020

@author: Zixiong Han
"""

import os
import csv
import numpy as np
import time

import sys
sys.path.append('..')
from bin_finder import binIndex, denoiseRadar

print(f"started at {time.strftime('%X')}")
fs = 17      # fs is radar sampling frequency
k_dist = 1.809   # k_dist indicates distance from kinect, which offer by Dr.Varun 
Folder_Path = r'C:\Users\rajitha\Documents\mbolic\5130\system\codes\data' 
os.chdir(Folder_Path)
    # Save all file names in that folder into a list
file_list = os.listdir()
csvFile = open('radar_back_normal_1.809m.csv', "r")
reader = csv.reader(csvFile)  
with open('1.csv', 'w+', newline='\n') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
    for i, row in enumerate(reader):
        spamwriter.writerow([val for val in row])
        if i == 2*fs*15-1:
            break
csvFile = open('1.csv', "r")
reader = csv.reader(csvFile) 
# Folder path of sample radar data, remember to change it  
# denoised_signal = File_Reader(Folder_Path, fs)
denoised_signal = denoiseRadar(reader, fs)
# print(f"started at {time.strftime('%X')}")
breath_ind = binIndex(k_dist, denoised_signal)
print("Breath index is %d" % breath_ind)
print(reader)
print(f"finished at {time.strftime('%X')}")
