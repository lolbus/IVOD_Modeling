import zmq
import json

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import matplotlib.animation as animation
from sklearn.cluster import DBSCAN
import time
from threading import Thread

topicfilter = "radar_data"
context = zmq.Context()
subSocket = context.socket(zmq.SUB)
subSocket.connect ("tcp://192.168.90.5:11002")
subSocket.setsockopt_string(zmq.SUBSCRIBE, topicfilter)

gdata = []

global x, y
coordinates_1 = [[],[]]
coordinates_2 = [[],[]]

count_frames  = 0
number_frames = 50
previous_time = 0

aniFrames = 2
interval = 5
xlim = (-4, 4)
ylim = (0, 5)
xlabel = "X"
ylabel = "Y"

fig = plt.figure(figsize=(110, 90))
ax = fig.add_subplot (121)

def Radar_DataCollection():
    print(f"Start receiving data")

    while True:
        #recieve data
        topic, message = subSocket.recv_string ().split (" ", 1)
        data = json.loads (message)

        #Extract data from Radar 1
        if data["name"] == "radar1":
            for i in data["packets"]:
                if (i["tlvType"] == 6):  # pointcloud
                    for n in i["data"]:
                        coordinates_1[0].append (n["x"])
                        coordinates_1[1].append (n["y"])
        elif data["name"] == "radar2":
            for i in data["packets"]:
                if (i["tlvType"] == 6):  # pointcloud
                    for n in i["data"]:
                        coordinates_2[0].append (n["x"])
                        coordinates_2[1].append (n["y"])
def clearArr(arr):
    for i in range(len(arr)):
        arr[i].clear()

def getDBScan(data):
    db = DBSCAN(eps=0.5, min_samples=20).fit(data)
    core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
    core_samples_mask[db.core_sample_indices_] = True
    labels = db.labels_
    n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise_ = list(labels).count(-1)
    unique_labels = set(labels)
    colors = [plt.cm.Spectral(each) for each in np.linspace(0, 1, len(unique_labels))]
    return unique_labels, colors, labels, core_samples_mask, n_clusters_

def updateGraphMerged(i):
    global coordinates
    if i == 0:
        clearArr (coordinates_1)
        clearArr (coordinates_2)
        ax.clear()
    try:
        data1 = np.column_stack ((coordinates_1[0], coordinates_1[1]))
        data2 = np.column_stack ((coordinates_2[0], coordinates_2[1]))
        stack = np.append (data1, data2, axis=0)
        print(stack)
        unique_labels, colors, labels, core_samples_mask, n_clusters_ = getDBScan (stack)
        for k, col in zip (unique_labels, colors):
            if k == -1:
                # Black used for noise.
                col = [0, 0, 0, 1]

            class_member_mask = labels == k

            xy = stack[class_member_mask & core_samples_mask]
            ax.scatter (xy[:, 0], xy[:, 1], marker=".", s=25, color=tuple (col))

            # xy = data3[class_member_mask & ~core_samples_mask]
            # ax.scatter(xy[:, 0], xy[:, 1], marker="o", s=6, color=tuple(col))
            ax.set (xlim=xlim, xlabel=xlabel)
            ax.set (ylim=ylim, ylabel=ylabel)
            ax.set_title ("Estimated number of clusters: %d" % n_clusters_)
    except:
        pass

thread = Thread(target = Radar_DataCollection)
thread.start()

ani = animation.FuncAnimation(fig, updateGraphMerged, aniFrames, interval=interval)
plt.show()
