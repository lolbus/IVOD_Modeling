import zmq
import json

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import warnings
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler

warnings.simplefilter(action='ignore', category=FutureWarning)

gdata = []

global x, y, z
coordinates = pd.DataFrame()

count_frames  = 0
number_frames = 50

fig = plt.figure (figsize=(110, 90))
ax = fig.add_subplot (121)

def live_update_demo(X,Y):
    ax.scatter(X, Y,color='red', s=1)
    ax.set_xlabel('Azimuth', fontsize=10)
    ax.set_ylabel('Range', fontsize=10)
    #  ax.set_zlabel('Elevation', fontsize=10)
    ax.set_title('Radar 1', fontsize=10)
    #plt.title ("Graph", fontweight='bold', size=15)
    # ax.view_init (0, 90)

    ax.set_xlim ([-10, 10])
    ax.set_ylim ([0, 15])
    fig.tight_layout ()
    #  ax.autoscale (False)

    redraw_figure()

def redraw_figure():
    plt.draw()
    plt.pause(0.0001)

# from https://stackoverflow.com/questions/40126176/fast-live-plotting-in-matplotlib-pyplot

eps = 225
min_samples = 20

def DBSCAN_(X): # Machine Learning

    db = DBSCAN (eps=0.5, min_samples=15).fit (X)
    core_samples_mask = np.zeros_like (db.labels_, dtype=bool)
    core_samples_mask[db.core_sample_indices_] = True
    labels = db.labels_

    # Number of clusters in labels, ignoring noise if present.
    n_clusters_ = len (set (labels)) - (1 if -1 in labels else 0)
    n_noise_ = list (labels).count (-1)

  #  print ("Estimated number of clusters: %d" % n_clusters_)
  #  print ("Estimated number of noise points: %d" % n_noise_)

    unique_labels = set (labels)
    colors = [plt.cm.Spectral (each) for each in np.linspace (0, 1, len (unique_labels))]
    for k, col in zip (unique_labels, colors):
        if k == -1:
            # Black used for noise.
            col = [0, 0, 0, 1]

        class_member_mask = labels == k

        xy = X[class_member_mask & core_samples_mask]
        ax.plot (
            xy[:, 0],
            xy[:, 1],
            ".",
            markerfacecolor=tuple (col),
            markeredgecolor="k",
            markersize=10,
        )

        xy = X[class_member_mask & ~core_samples_mask]
        ax.plot (
            xy[:, 0],
            xy[:, 1],
            ".",
            markerfacecolor=tuple (col),
            markeredgecolor="k",
            markersize=3,
        )
 #   fig.tight_layout ()
    ax.set_xlim ([-5, 5])
    ax.set_ylim ([0, 5])
    plt.title ("Estimated number of clusters: %d" % n_clusters_)
    redraw_figure ()

def Radar_DataCollection():
    global count_frames , number_frames, coordinates, Training_data_df

    # try:
    minPointdetected = 1
    context = zmq.Context (1)
    # Socket facing clients
    sub_port = 11002
    submq = context.socket (zmq.SUB)
    connectstring = "tcp://192.168.90.5:{}".format (sub_port)
    submq.connect (connectstring)
    tpc = "radar_data"

    submq.setsockopt_string (zmq.SUBSCRIBE, "radar_data")
    print ("Start radar data streamming----topic :{}".format (tpc))
    while True:
        #recieve data
        context = submq.recv ().decode ("utf-8")  # receive
        topic, message = context.split (" ", 1)
        jsndata = json.loads (message)
        if (not jsndata.get ("packets") is 'None'):

            #Extract data from Radar 1
            if jsndata["name"] == "radar1":
                for i in jsndata["packets"]:
                    if (i["tlvType"] == 6):  # pointcloud
                        for n in i["data"]:
                            if count_frames  == 0:
                                coordinates = pd.DataFrame ({'x': n["x"], 'y': n["y"]}, index=[0])
                            else:
                                c = pd.DataFrame ({'x': n["x"], 'y': n["y"]}, index=[0])
                                coordinates = coordinates.append (c)
                        count_frames  +=1 # used to count number of frames captured
                        # everytime type 6 is detected, thats 1 frame
                #  elif (i["tlvType"] == 8):
                #      tgt = []
                #      for n in i["data"]:
                #          if (n["targetIndex"] not in tgt):
                #              tgt.append ((n["targetIndex"]))
                # 7 TargetsPosition

                # print(tgt)
                # print (i)
        if (count_frames <= 10):
            #live_update_demo (coordinates['x'], coordinates['y'])
            if not coordinates.empty:
                DBSCAN_ (coordinates.to_numpy ())
            count_frames += 1
        else:
            # reset
            coordinates.drop (coordinates.index, inplace=True)
            plt.cla ()
            count_frames = 0


# except Exception as e:
#     print (e)
#     print ("bringing down zmq device")
# finally:
#     pass


#if __name__ == "__main__":
#    x = threading.Thread (target=Radar_DataCollection, args=())
#    x.start ()
#    x.join ()


Radar_DataCollection()
