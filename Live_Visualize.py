# Single thread collection
# Completed

import json
from collections import Counter
import numpy as np
import matplotlib.animation as animation
from matplotlib import pyplot as plt
import time
from threading import Thread
import zmq
import warnings
from time import sleep

#Pre-requisite
from svgpathtools import svg2paths
from svgpath2mpl import parse_path

start_time = time.time()
warnings.simplefilter(action='ignore', category=FutureWarning)




# zmq
topicfilter = "ivod_demo_dbscan"
context = zmq.Context()
subSocket = context.socket(zmq.SUB)
subSocket.connect("tcp://192.168.70.120:11002")
subSocket.setsockopt_string(zmq.SUBSCRIBE, topicfilter)
subSocket.setsockopt_string(zmq.SUBSCRIBE, "radar_data")

# matplotlib marker design
man_path, attributes = svg2paths('user.svg')
man_marker = parse_path(attributes[0]['d'])
man_marker.vertices -= man_marker.vertices.mean(axis=0)

sleep(1)
aniFrames = 2
time_limit = 500 * aniFrames
arr = []
data = []

lowerRange = 0
upperRange = 3.6
lowerAzimuth = -2
upperAzimuth = 2
lowerElevation = -0.8
upperElevation = 0.2

rangeSlice = np.linspace(lowerRange, upperRange, 13)
azimuthSlice = np.linspace(lowerAzimuth, upperAzimuth, 17)
elevationSlice = np.linspace(lowerElevation, upperElevation, 5)

numClust = []
tmp = []
rawArr = []
secondsLimit = 5
peopleCluster = []
centroidPoints = []
people = 0

#plt plot define
fig = plt.figure(figsize=(15, 15))
ax2 = fig.add_subplot(131, projection='3d')
ax2.view_init(90,-90)
ax = fig.add_subplot(132, projection='3d')
ax.view_init(90,-90)
ax3 = fig.add_subplot(133)


def collect_data():
    start_time = time.time()
    seconds = 0
    while True:
        global rawArr, secondsLimit, centroidPoints, tmp, peopleCluster
        recv = subSocket.recv_string()
        try:
            if recv == "ivod_demo_dbscan":
                recv1 = subSocket.recv_string()
                msg = json.loads(recv1)
                if (msg["dataName"] == "Centroids"):
                    package = msg["package"]
                    centroidPoints = []
                    for p in package:
                        centroidPoints.append([p.get("x"), p.get("y"), p.get("z")])
                if (msg["dataName"] == "People"):
                    package = msg["package"]
                    peopleCluster = []
                    for p in package:
                        peopleCluster.append([p.get("x"), p.get("y")])
            else:
                splitArr = recv.split(" ", 1)
                if splitArr[0] == "radar_data":
                    message = splitArr[1]
                else:
                    message = recv
                msg = json.loads(message)
                packet = msg["packets"]
                packet = packet[0]
                packet = packet["data"]
                for p in packet:
                    if p.get("x") is not None:
                        tmp.append([p.get("x"), p.get("y"), p.get("z")])

                if time.time() - start_time >= 0.5:
                    rawArr.append(tmp)
                    tmp = []
                    start_time = time.time()
                    if seconds < secondsLimit:
                        seconds += 0.5
                    else:
                        rawArr.pop(0)
        except:
            pass

def graphing(i):        
    global rawArr, man_marker, centroidPoints, people, peopleList

    ax.clear()
    ax2.clear()
    ax3.clear()
    
    working = rawArr
    npData = []
    if working:
        for w in working:
            npData += w

    ax.set(xlim=(-2, 2), xlabel="Azimuth", ylim=(0, 3.6), ylabel="Range", zlim=(-0.8, 0.2), zlabel="Elevation", title="Simplified Data")
    ax2.set(xlim=(-2, 2), xlabel="Azimuth", ylim=(0, 3.6), ylabel="Range", zlim=(-0.8, 0.2), zlabel="Elevation", title="Raw Data")
    ax3.set(xlim=(-2, 2), xlabel="Azimuth", ylim=(0, 3.6), ylabel="Range", title=f'People predicted: {people}')

    if npData:
        tmpPlot = np.array(npData)
        ax2.scatter(tmpPlot[:, 0], tmpPlot[:, 1], tmpPlot[:, 2], color="green")

    try:
        centroidPlot = np.array(centroidPoints)
        ax.scatter(centroidPlot[:, 0], centroidPlot[:, 1], centroidPlot[:, 2], color="red")
    except:
        pass

    try:
        npCluster = np.array(peopleCluster)
        people = len(peopleCluster)
        ax3.scatter(npCluster[:, 0], npCluster[:, 1], marker=man_marker, s=1000, color='black')
    except:
        pass

def visualization_main():
    print("Started visualization successfully")
    ani = animation.FuncAnimation(fig, graphing, aniFrames, interval=time_limit)
    plt.show()

collection = Thread(target=collect_data)
collection.start()

'''collection = Thread(target=visualization_main)
collection.start()
'''
if __name__ == "__main__":
    print("Started visualization successfully")
    ani = animation.FuncAnimation(fig, graphing, aniFrames, interval=time_limit)
    plt.show()
