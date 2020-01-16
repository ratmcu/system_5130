#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 10 14:40:28 2020

@author: rnd
"""
import numpy as np
from scipy import signal
# Input is the 15 sec signal at the range bin
def welch_br_rate(data):
    fs = 17    #sampling rate
    data = data.reshape(255,1)
    data = np.transpose(data)
    # calculate psd with Blackman window
    f, Pxx_den = signal.welch(data, fs,'blackman',noverlap=170, nfft=2**16)
    # calculate the max and its index
    max_index=np.argmax(Pxx_den)
    # check the value at that point
    freq = f[max_index]
    #Breathing rate
    br_rate=freq*60
    return(br_rate)