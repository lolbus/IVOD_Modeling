import zmq
import json
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import matplotlib.animation as animation
from sklearn.cluster import DBSCAN
import time
from threading import Thread
from sklearn.neighbors import NearestNeighbors

topicfilter = "radar_data"
context = zmq.Context()
subSocket = context.socket(zmq.SUB)
subSocket.connect ("tcp://192.168.70.120:11002")
subSocket.setsockopt_string(zmq.SUBSCRIBE, topicfilter)

fig = plt.figure(figsize=(110, 90))
#ax = fig.add_subplot (1, 3, 1)
#ax2 = fig.add_subplot (1, 3, 2)
#ax3 = fig.add_subplot (1, 3, 3)
ax = fig.add_subplot(projection="3d")

centroids = []

def readFiles(pathName, main, constant, lower_limit, upper_limit):
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
        if data :
            for d in data:
                if d["snr"] > 10 and d["snr"] < 50: 
                    if d[main] > lower_limit and d[main] < upper_limit:   
                        dataPoints = []
                        dataPoints.append(d[main])
                        dataPoints.append(d[constant])
                        tmp.append(dataPoints)
    return tmp

def DBSCAN_(X): # Machine Learning
    if X.size > 0:
        db = DBSCAN (eps=0.2, min_samples=15).fit (X)
        core_samples_mask = np.zeros_like (db.labels_, dtype=bool)
        core_samples_mask[db.core_sample_indices_] = True
        labels = db.labels_

        n_clusters_ = len (set (labels)) - (1 if -1 in labels else 0)
        n_noise_ = list (labels).count (-1)

    #  print ("Estimated number of clusters: %d" % n_clusters_)
    #  print ("Estimated number of noise points: %d" % n_noise_)

        unique_labels = set (labels)
        colors = [plt.cm.Spectral (each) for each in np.linspace (0, 1, len (unique_labels))]
        centroid_of_cluster = [[], []]
        
        for k, col in zip (unique_labels, colors):
            if k == -1:
                continue
            points_of_cluster = X[labels == k, :]
            centroids = np.mean(points_of_cluster, axis=0)
            centroid_of_cluster[0].append(centroids[0])
            centroid_of_cluster[1].append(centroids[1])

            class_member_mask = labels == k

            xy = X[class_member_mask & core_samples_mask]
            #ax.plot (
            #    xy[:, 0],
            #    xy[:, 1],
            #    ".",
            #    markerfacecolor=tuple (col),
            #    markeredgecolor="k",
            #    markersize=10,
            #)

            xy = X[class_member_mask & ~core_samples_mask]
            #ax.plot (
            #    xy[:, 0],
            #    xy[:, 1],
            #    ".",
            #    markerfacecolor=tuple (col),
            #    markeredgecolor="k",
            #    markersize=3,
            #)
    #   fig.tight_layout ()
        #ax.set_xlim ([-5, 5])
        #ax.set_ylim ([0, 5])
        #print("Estimated number of clusters: %d | " % n_clusters_, centroid_of_cluster)

        #ax2.scatter (c1,c2, marker=".", s=25, color=tuple (col))
        #ax2.set (xlim=xlim, xlabel=xlabel)
        #ax2.set (ylim=ylim, ylabel=ylabel)
        #ax2.set_title ("Cluster Centroids")
        return n_clusters_

# lower_limit, upper_limit
#xy_1 = np.array(readFiles(path, "x", "y", 0.25, 0.75))
#xy_2 = np.array(readFiles(path, "x", "y", -0.25,0.25))
#xy_3 = np.array(readFiles(path, "x", "y", -0.75,-0.25))

fileNo = 1
correct = 0

while fileNo < 1000:

    path ="//192.168.70.120/debug/data/PassengerNo_2/" + str(fileNo) + "/Both Radar.txt"
    xy_1 = np.array(readFiles(path, "x", "y", 0.2, 0.4))
    xy_2 = np.array(readFiles(path, "x", "y", 0,0.2))
    xy_3 = np.array(readFiles(path, "x", "y", -0.2,0))

    zx_1 = np.array(readFiles(path, "z", "x", -0.2,-0.1))
    zx_2 = np.array(readFiles(path, "z", "x", -0.3,-0.2))
    zx_3 = np.array(readFiles(path, "z", "x", -0.4,-0.3))

    if xy_1.size > 0 :
        clusters =  DBSCAN_(xy_1) + DBSCAN_(xy_2) + DBSCAN_(xy_3) + DBSCAN_(zx_1) + DBSCAN_(zx_2) + DBSCAN_(zx_3)
    #DBSCAN_(xy_1)  
    #DBSCAN_(xy_2)
    #DBSCAN_(xy_3) 
    #DBSCAN_(zx_1)  
    #DBSCAN_(zx_2) 
    #DBSCAN_(zx_3)

    if clusters == 12:
        #print("1 Passenger")
        correct += 1
    print(clusters)
    fileNo += 1
else: 
    score = correct / 1000 * 100
    print(f"Accuracy: {score} %")


#print("Clusters: ", clusters)
#wrong, plotting array not the dbscan cluster

#ax.scatter(xy_1[:,0], xy_1[:,1], c="red")
#ax.scatter(xy_2[:,0], xy_2[:,1], c="green")
#ax.scatter(xy_3[:,0], xy_3[:,1], c="blue")
#ax.set_xlabel('Azimuth')
#ax.set_ylabel('Range')
#ax.set_title('Section x and y')
#plt.show()

#ax2.scatter(xy_2[:,0], xy_2[:,1])
#ax2.set_xlabel('Azimuth')
#ax2.set_ylabel('Range')

#ax3.scatter(xy_3[:,0], xy_3[:,1])
#ax3.set_xlabel('Azimuth')
#ax3.set_ylabel('Range')
#plt.show()

#thread = Thread (target=DBSCAN_)
#thread.start ()

#ani = animation.FuncAnimation(fig, updateGraphMerged, aniFrames, interval=interval)
#plt.show()

