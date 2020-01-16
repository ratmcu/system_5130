# -*- coding: utf-8 -*-
"""
Created on Thu Jan  2 21:04:10 2020

@author: Zixiong Han
"""

import os
import csv
import numpy as np
import time

def denoiseRadar(data, fs):
    # Modify the current working directory
    rawData = []
    for row in data:
        rawData.append(row)
        # print(row)
        rawData = [x for x in rawData if x != []]
        data_num = len(rawData)
        bin_num = len(rawData[0])
        float_data = np.zeros([data_num, bin_num])
    
    for i in range(data_num):
        for j in range(bin_num):
            # float_data[i][j] = abs(complex(rawData[i][j+1]))
            float_data[i][j] = abs(rawData[i][j])
    # print(float_data.shape)
    file_duration = int(len(float_data)/fs)
    denoised_signal = svdDenoised(file_duration, fs, float_data)
    return denoised_signal

# k_dist indicates distance from kinect, which offer by Dr.Varun
# denoised_signal is a Numpy array,make sure that a Numpy array is input if you don't use File_Reader function 
def binIndex(k_dist, denoised_signal = []):
    # Calculate variance
    k_index = int(k_dist/0.05)
    low_thresh = k_index-5
    high_thresh = k_index+5
    
    target_bin = denoised_signal[:,low_thresh:high_thresh]
    bin_num = len(target_bin[0])
    
    var_bin = np.zeros(bin_num)
    for j in range(bin_num):
        var_bin[j] = np.var(target_bin[:,j])
        
    # Find out the breath_ind through max(variance)
    var_bin = var_bin.tolist()
    breath_ind = var_bin.index(max(var_bin))
    
    breath_ind = breath_ind + low_thresh
    
    return breath_ind

def svdDenoised(k, fs, float_data = []):
    bin_num = len(float_data[0])
    # SVD decomposition denoise
    seg_len = k*fs
    data_seg = np.zeros([seg_len,bin_num])
    data_seg = float_data
    U,s,V = np.linalg.svd(data_seg)
    S = np.zeros([len(data_seg),len(data_seg[0])])
    for k in range(len(s)):
        S[k][k] = s[k]
    
    tmp = np.dot(U,S)
    R = np.dot(tmp,V)
    # data_seg is denoised data
    denoised_signal = R
    
    return denoised_signal
