import zmq
import json
import numpy as np
from matplotlib import pyplot as plt
from sklearn.cluster import DBSCAN
from threading import Thread
from sklearn.neighbors import NearestNeighbors
import time

topicfilter = "radar_data"
context = zmq.Context()
subSocket = context.socket(zmq.SUB)
subSocket.connect ("tcp://192.168.70.120:11002")
subSocket.setsockopt_string(zmq.SUBSCRIBE, topicfilter)


xlim = (-0.2, 1.2)
ylim = (1, 3)
xlabel = "X"
ylabel = "Y"

all_Data = []

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
                if 1 < d["y"] < 2.6: 
                    if d[main] > lower_limit and d[main] < upper_limit: 
                        if main == "z":
                            tmp.append([d[constant], d[main], d["y"]])
                        else:
                            tmp.append([d[main], d[constant]])
    return tmp

def DBSCAN_(X, name): # Machine Learning      
    centroid_of_cluster = []
    centroids = []
    y = []
    if X.size > 0:
        if name == "clustering":
            sample = 5
            eps = 0.3
        elif name == "centroids":   
            sample = 4
            eps = 0.3
        db_X = np.column_stack((X[:, 0], X[:, 1]))

        db = DBSCAN (eps, min_samples=sample).fit (db_X)
        core_samples_mask = np.zeros_like (db.labels_, dtype=bool)
        core_samples_mask[db.core_sample_indices_] = True
        labels = db.labels_

        n_clusters_ = len (set (labels)) - (1 if -1 in labels else 0)
        unique_labels = set (labels)
        
        for k in unique_labels:
            if k == -1:
                continue
            points_of_cluster = db_X[labels == k, :]
            centroids = np.mean(points_of_cluster, axis=0)    

            if len(X[0]) == 3:
                for p in points_of_cluster:
                    for r in X:
                        if p[0] == r[0]:
                            y.append(r[2])
                            break
                cluster_y = np.mean(y)                    
                centroid_of_cluster.append([centroids[0], cluster_y])
            else:
                centroid_of_cluster.append(centroids.tolist())
        return centroid_of_cluster

fileNo = 1
correct = 0
numberofFiles = 2600
A_interval = np.linspace(1, -0.2, 10)
Z_interval = np.linspace(0.1, -0.4, 7)

while fileNo < numberofFiles:
    start_time = time.time()
    cluster_tmp = []
    totalCluster = []
    path ="//192.168.70.120/debug/data/PassengerNo_2 (Front Passenger)/" + str(fileNo) + "/Both Radar.txt"
    #X: 1 to -0.2
    for r in range(len(A_interval)-1):
        xy = np.array(readFiles(path, "x", "y", A_interval[r+1], A_interval[r]))
        totalCluster.append(DBSCAN_(xy, "clustering"))
    
    
    for r in range(len(Z_interval)-1):
        zx = np.array(readFiles(path, "z", "x", Z_interval[r+1], Z_interval[r]))
        totalCluster.append(DBSCAN_(zx, "clustering"))

    for t in totalCluster:
        if t:
            for t1 in t:
                cluster_tmp.append(t1)
    cluster_tmp = np.array(cluster_tmp)

    final_centriods = np.array(DBSCAN_(cluster_tmp, "centroids"))

    fig = plt.figure(figsize=(110, 90))
    ax = fig.add_subplot (1, 2, 1, projection ="3d")
    ax2 = fig.add_subplot (1, 2, 2)

    ax.scatter(cluster_tmp[: ,0], cluster_tmp[:, 1], 0, color="red")
    #ax.scatter(finalCluster[: ,0], finalCluster[:, 1],finalCluster[:, 2])
    ax.set (xlim=xlim, xlabel=xlabel)
    ax.set (ylim=ylim, ylabel=ylabel)
    ax.set_zlabel('Elevation')
    ax.set_title("Centroids")
    ax.view_init (90,0)

    ax2.scatter(final_centriods[: ,1], final_centriods[:, 0], color="red")
    ax2.set (xlim=ylim, xlabel=ylabel)
    ax2.set (ylim=(1.2,-0.2), ylabel=xlabel)
    #ax2.set_zlabel('Elevation')
    ax2.set_title(f"Cluster Number: {2}")
    plt.show()

       #print("fileNo: ", fileNo)
    if len(DBSCAN_(cluster_tmp, "centroids")) == 2:
        correct += 1
    fileNo += 1
    score = correct / fileNo * 100

    print("Centroids: ",len(final_centriods))
    print(f"Accuracy: {score} %")
    print("Time: ",  time.time() - start_time)
    print("File No: ", fileNo)
else: 
    score = correct / numberofFiles * 100
    print("correct: ", correct)
    print(f"Final Accuracy: {score} %")

    

#range 1-2.6, 0.4
#azimuth -1 to 0.25 0.25
#elevation -0.6 to 0.2 0.2