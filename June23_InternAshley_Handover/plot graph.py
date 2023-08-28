import json
import numpy as np
from matplotlib import pyplot as plt

def readFiles(pathName):
    splitVar = "{\"DateTime"
    tmp = []
    
    file = open(pathName, "r")
    values = file.read()
    msg = values.split(splitVar)
    msg.pop(0)

    for r in range(len(msg)):
        msg[r] = splitVar + msg[r]
        package = json.loads(msg[r])
        data = package["data"]
        if data != 'No data received':
            for d in data:
                #if len(tmp) < 2048 and d["y"]<2 and d["x"] > -0.8:        
                #if d["y"]<2 and d["snr"] < 100 and d["snr"] > 20:  
                
                #if d["x"] > -0.8 and d["y"] > 1.7 and d["y"] < 3.2:
                if d["x"] > -0.7: 
                    dataPoints = []
                    dataPoints.append(d["x"])
                    dataPoints.append(d["y"])
                    dataPoints.append(d["z"])
                    tmp.append(dataPoints)

    return tmp

DATA_DIR ="//192.168.70.120/debug/data/PassengerNo_2 (Front Passenger)/1/Both Radar.txt"
#DATA_DIR ="//192.168.70.120/debug/data/extra/PassengerNo_1 (Front View No E Flip)/100/Both Radar.txt"

samplePoints = readFiles(DATA_DIR)
samplePoints = np.array(samplePoints)
#print(type(samplePoints))
print(len(samplePoints))
#C:\debug\testing keras\1 Passenger keras\train\1

fig = plt.figure(figsize=(5, 5))
ax = fig.add_subplot(projection="3d")
ax.scatter(samplePoints[:, 0], samplePoints[:, 1], samplePoints[:, 2])
ax.set_xlabel('Azimuth')
ax.set_ylabel('Range')
#ax.set(xlim=(2, -2), ylim=(0, 4), zlim=(-0.8, 0.2))

ax.set_zlabel('Elevation')
ax.set_title("Front Two Passenger")
ax.view_init (90, 0)

plt.show()