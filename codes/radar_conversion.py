'''
created on Jan 10th 2020
@author: Rajitha Hathurusinghe 
'''
import numpy as np

def radarToNp(frame):
    frame = np.array(frame)
    n = len(frame)
    # print type(n // 2)
    return frame[:n // 2] + 1j * frame[n // 2:]
        
                 
def framesToNp( radar_list):
    times = [row[0] for row in radar_list]
    frames = [radarToNp(row[1]) for row in radar_list]
    times = np.asarray(times)
    frames = np.column_stack((times, frames))
    return frames

def toRawRadarFrame(csv_np):
    raw  = []
    for row in csv_np:
        time = row[0]
        real = []
        imag = []
        for col in row[1:]:
            real.append(col.real)
            imag.append(col.imag)
        # print(real)
        real.extend(imag)
        raw.append([time, real])
    return raw