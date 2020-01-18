#!/usr/bin/env python3
# gives out the algorithm dictinary list
# and defines the functions executing the breathing algorithms



"""
Created on Fri Jan 10 14:40:28 2020

@author: rnd
"""
import numpy as np
from scipy import signal
from scipy.spatial import distance
from PyEMD import EMD
    
# Input is the 15 sec signal at the range bin
def welchBreathingRate(data):
    fs = 17    #sampling rate
    # print(data.shape)
    data = data.reshape(data.shape[0],1)
    data = np.transpose(data)
    # calculate psd with Blackman window
    f, Pxx_den = signal.welch(data, fs,'blackman',noverlap=100, nfft=2**16)
    # calculate the max and its index
    max_index=np.argmax(Pxx_den)
    # check the value at that point
    freq = f[max_index]
    #Breathing rate
    br_rate=freq*60
    return(br_rate)

def emdBreathingRate(data):    
    fs = 17    #sampling rate
    # print(data.shape)
    size = data.shape[0]
    data = data.reshape(size,1)
    data = np.transpose(data)
    data = data[0,1:size]
    #Calculate the EMD of the input signal
    IMF = EMD().emd(data)  # Format N X No_Points
    #Number of IMFs
    N=IMF.shape[0]
    No_points=IMF.shape[1]
    #Initialize variables
    Flt_imf=np.zeros((N,No_points))
    sq_imf=np.zeros((N,No_points))
    b=np.zeros((1,N))
    br_fq=np.zeros((1,N))
    dist=np.zeros((1,N))
        
    for k in range(N):
        mean_imf=np.mean(IMF[k,0:No_points])
        Flt_imf[k,0:No_points]=IMF[k,0:No_points]-mean_imf
        sq_imf[k,0:No_points]=np.multiply(Flt_imf[k,0:No_points],Flt_imf[k,0:No_points])
        b[0][k]=np.sum(sq_imf) #axis
        
    b=b/np.max(b)
    b=1-b
    
    for i in range(N):
        f, Pxx_den = signal.periodogram(IMF[i,0:No_points],fs,window='blackman', nfft=2**16)
        # calculate the max and its index
        max_index = np.argmax(Pxx_den)
        # check the value at that point
        freq = f[max_index]
        br_fq[0][i] = freq
        #Minkowski distance
        dist[0][i] = distance.minkowski(IMF[i,0:No_points],data)
        
    
    min_index = np.argmin(dist)
    br_rate = br_fq[0][min_index]*60
    
    if br_rate<8 or br_rate>30:
        dist[0][min_index]=10000
        min_index = np.argmin(dist)
        br_rate = br_fq[0][min_index]*60
        
        
    return(br_rate)    

def getAlgoList():
    algo_list = [{'name':'emd', 'function' : emdBreathingRate},
                 {'name': 'welch fft', 'function' : welchBreathingRate}  
                ]
    return algo_list
