#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 13:08:59 2020

@author: rnd
"""
def person_list(x): #input row of the kinect csv file 
    personlist = []
    if x[1]=='Body ID: 1':
        x1=x.iloc[2]
        y1=x.iloc[3]
        z1=x.iloc[4]
        Position_1 = [1,x1,y1,z1]
        #
        x2=x.iloc[12]
        y2=x.iloc[13]
        z2=x.iloc[14]
        Position_2 = [2,x2,y2,z2]
        personlist=[Position_1,Position_2]
        #print(personlist)
    else:
        x1=x.iloc[12]
        y1=x.iloc[13]
        z1=x.iloc[14]
        Position_1 = [1,x1,y1,z1]
        #
        x2=x.iloc[2]
        y2=x.iloc[3]
        z2=x.iloc[4]
        Position_2 = [2,x2,y2,z2]
        personlist=[Position_1,Position_2]
        
        
    return(personlist)
        
        
        