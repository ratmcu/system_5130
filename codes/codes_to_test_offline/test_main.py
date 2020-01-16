#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 15:17:23 2020

@author: rnd
"""
import numpy as np
from scipy.spatial import distance
from PyEMD import EMD
from scipy import signal
from scipy.signal import medfilt
from scipy.signal import find_peaks
from numpy import linalg as LA
from numpy import genfromtxt
import pandas as pd


from bin_finder import binIndex, denoiseRadar,svdDenoised
from varun import coord_conv,activity_det
from EMD_br_rate import emd_br_rate
from welch_br import welch_br_rate
from min_max_breath_rate import rescale1, minmax_br_rate
from Kinect_data import person_list

import time

from radar_conversion import radarToNp, framesToNp, toRawRadarFrame
# Define variables
fs=17
Breathing_segment=15
Segment_length = Breathing_segment*fs
radarResolution = 0.0522
radarStartIndex = 17*fs
num_fast_chan=180
Segment_overlap=0.5
# load the kinect data
kin_data = pd.read_csv("exp1_kin_1118_1.csv")
# load the input data from radar
rd1_data = genfromtxt('exp1_rd1_1118.csv', dtype=complex,delimiter=',')
rd1_data = rd1_data[radarStartIndex:,1:]
#rd1_data=np.absolute(rd1_data)
#
rd2_data = genfromtxt('exp1_rd2_1118.csv', dtype=complex,delimiter=',')
rd2_data = rd2_data[radarStartIndex:,1:]
#rd2_data=np.absolute(rd2_data)
#
rd3_data = genfromtxt('exp1_rd3_1118.csv', dtype=complex,delimiter=',')
# print(rd3_data)
rd3_data = rd3_data[radarStartIndex:,1:]
# print(rd3_data)
#rd3_data=np.absolute(rd3_data)
# load the br_belt data
br_belt1 = genfromtxt('exp1_varun_1118.csv', delimiter=',')
br_belt2 = genfromtxt('exp1_shan_1118.csv', delimiter=',')

segment_num=2


#check the distance of the chest using kinect
per_data = kin_data.iloc[1,:]
per_list = person_list(per_data)

per1 = False
per2 = False
dist_to_rad_per_1 = []
dist_to_rad_per_2 = []
for entry in per_list:
    # since we get the first ever coordinate for chsest distance
    if entry[0] == 1 and not per1:
       print(entry[1:])
       temp,dist_to_rad_per_1 = coord_conv(np.asarray(entry[1:])/1000)
    if entry[0] == 2 and not per2:
        temp,dist_to_rad_per_2 = coord_conv(np.asarray(entry[1:])/1000)
    if per1 and per2:
        break


# for row in rd1_data:

r1data = rd1_data[1:256,:]
r2data = rd2_data[1:256,:]
r3data = rd3_data[1:256,:]      

den_r1data = denoiseRadar(r1data, fs)
den_r2data = denoiseRadar(r2data, fs)
den_r3data = denoiseRadar(r3data, fs)

    # Find the binindex
#Person-1
br1_index1 = binIndex(dist_to_rad_per_1[0], den_r1data)
br1_index2 = binIndex(dist_to_rad_per_1[1], den_r2data)
br1_index3 = binIndex(dist_to_rad_per_1[2], den_r3data)
#Person-2
br2_index1 = binIndex(dist_to_rad_per_2[0], den_r1data)
br2_index2 = binIndex(dist_to_rad_per_2[1], den_r2data)
br2_index3 = binIndex(dist_to_rad_per_2[2], den_r3data)

    # Calculate breathing rate
#Person-1
signal_bin11 = np.unwrap(np.angle(r1data[:,br1_index1]))
brate1_r1 = emd_br_rate(signal_bin11)

signal_bin12 = np.unwrap(np.angle(r2data[:,br1_index2]))
brate1_r2 = emd_br_rate(signal_bin12)

signal_bin13 = np.unwrap(np.angle(r3data[:,br1_index3]))
brate1_r3 = emd_br_rate(signal_bin13)

#Person-2
signal_bin21 = np.unwrap(np.angle(r1data[:,br2_index1]))
brate2_r1 = emd_br_rate(signal_bin21)

signal_bin22 = np.unwrap(np.angle(r2data[:,br2_index2]))
brate2_r2 = emd_br_rate(signal_bin22)

signal_bin23 = np.unwrap(np.angle(r3data[:,br2_index3]))
brate2_r3 = emd_br_rate(signal_bin23)
brate2_r3w = welch_br_rate(signal_bin23)
print(brate1_r1, brate1_r2, brate1_r3, brate2_r3w)





rd3_data = genfromtxt('C:\\Users\\rajitha\\Documents\\mbolic\\5130\\system\\codes\\codes_to_test_offline\\exp1_rd3_1118.csv', dtype=complex, delimiter=',')
raw = toRawRadarFrame(rd3_data)
r3data_sim = framesToNp(raw)
r3data = r3data_sim[radarStartIndex:,1:]
r3data = r3data[1:256,:]
den_r3data = denoiseRadar(r3data, fs)
signal_bin23 = np.unwrap(np.angle(r3data[:,br2_index3]))
br2_index3 = binIndex(dist_to_rad_per_2[2], den_r3data)
brate2_r3 = emd_br_rate(signal_bin23)
brate2_r3w = welch_br_rate(signal_bin23)
print(brate1_r1, brate1_r2, brate1_r3, brate2_r3w)



