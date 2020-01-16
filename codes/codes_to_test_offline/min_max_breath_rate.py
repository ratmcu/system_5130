#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan  9 13:21:36 2020

@author: rnd
"""

import numpy as np
from scipy.signal import medfilt
from scipy.signal import find_peaks

def rescale1(x_in):
    x_min=np.min(x_in)
    x_max=np.max(x_in)
    N=np.size(x_in)
    x_out=np.zeros((N,1))
    x_out= (x_in-x_min)/(x_max-x_min)
    return(x_out)

def minmax_br_rate(data):  #Input is the 15 sec signal 
    fs=17
    data = data.reshape(255,1)
    data = np.transpose(data)
    mean_data=np.mean(data)
    filtered_signal=data-mean_data
    medfilt_signal_1 = medfilt(filtered_signal[0,0:255],kernel_size=5)
    medfilt_signal_2 = medfilt(-filtered_signal[0,0:255],kernel_size=5)
    norm_signal_1=rescale1(medfilt_signal_1)
    norm_signal_2=rescale1(medfilt_signal_2)
    peaks_1, _ = find_peaks(norm_signal_1, prominence=0.15, distance=25)
    peaks_2, _ = find_peaks(norm_signal_2, prominence=0.15, distance=25)
    
    len1=np.size(peaks_1)
    len2=np.size(peaks_2)
    
    if len1>1 and len2>1:
        num=60*fs
        den=np.mean(np.diff(peaks_1))+np.mean(np.diff(peaks_2))
        br_rate=2*(num/den)
    elif len1>1:
        num=60*fs
        den=np.mean(np.diff(peaks_1))
        br_rate=2*(num/den)
    elif len2>1:
        num=60*fs
        den=np.mean(np.diff(peaks_2))
        br_rate=2*(num/den)
    else:
        br_rate=0
    
    
    
    return(br_rate)