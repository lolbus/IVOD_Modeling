import zmq
import json
import pandas as pd
from matplotlib import pyplot as plt
import warnings

import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn import cluster
import time

warnings.simplefilter(action='ignore', category=FutureWarning)

gdata = []

global x, y, z
coordinates = pd.DataFrame()
Training_data_df = pd.DataFrame()
radar_name = "radar2"

count_frames  = 0
number_frames = 50
counter = 0

fig = plt.figure (figsize=(110, 90))
ax = fig.add_subplot (121)
ax_DBSCAN = fig.subplots_adjust(hspace=.5, wspace=.2)

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
    redraw_figure()

def redraw_figure():
    plt.draw()
    plt.pause(0.0001)

# from https://stackoverflow.com/questions/40126176/fast-live-plotting-in-matplotlib-pyplot
eps = 225
min_samples = 20

def DBSCAN_(X): # Machine Learning

   # X = np.array(x,y)
#    X = StandardScaler ().fit_transform (X)

    db = DBSCAN (eps=0.3, min_samples=10).fit (X)
    core_samples_mask = np.zeros_like (db.labels_, dtype=bool)
    core_samples_mask[db.core_sample_indices_] = True
    labels = db.labels_

    # Number of clusters in labels, ignoring noise if present.
    n_clusters_ = len (set (labels)) - (1 if -1 in labels else 0)
    n_noise_ = list (labels).count (-1)

    print ("Estimated number of clusters: %d" % n_clusters_)
    print ("Estimated number of noise points: %d" % n_noise_)

    unique_labels = set (labels)
    colors = [plt.cm.Spectral (each) for each in np.linspace (0, 1, len (unique_labels))]
    for k, col in zip (unique_labels, colors):
        if k == -1:
            # Black used for noise.
            col = [0, 0, 0, 1]

        class_member_mask = labels == k

        xy = X[class_member_mask & core_samples_mask]
        plt.plot (
            xy[:, 0],
            xy[:, 1],
            "o",
            markerfacecolor=tuple (col),
            markeredgecolor="k",
            markersize=14,
        )

        xy = X[class_member_mask & ~core_samples_mask]
        plt.plot (
            xy[:, 0],
            xy[:, 1],
            "o",
            markerfacecolor=tuple (col),
            markeredgecolor="k",
            markersize=3,
        )
    fig.tight_layout ()

    plt.title ("Estimated number of clusters: %d" % n_clusters_)
    redraw_figure ()

def Radar_DataCollection():
    global count_frames , number_frames, coordinates, Training_data_df, counter
    try:

        minPointdetected = 1
        context = zmq.Context (1)
        # Socket facing clients
        sub_port = 11002
        submq = context.socket (zmq.SUB)
        connectstring = "tcp://192.168.70.120:{}".format (sub_port)
        submq.connect (connectstring)
        tpc = "radar_data"

        submq.setsockopt_string (zmq.SUBSCRIBE, "radar_data")
        print ("Start radar data streamming----topic :{}".format (tpc))
        while True:
            #recieve data
      #      counter += 1
      #      time.sleep (0.1)

            context = submq.recv ().decode ("utf-8")  # receive
            topic, message = context.split (" ", 1)
            jsndata = json.loads (message)
            # print(jsndata)
            if (not jsndata.get ("packets") is 'None'):
                datacnt = len (jsndata["packets"])
                # if(datacnt>minPointdetected ):
                #  print ("Received Packet Len {}".format(datacnt))

                #Extract data from Radar 1
                if jsndata["name"] == radar_name:
                    for i in jsndata["packets"]:
                        #  print(i)
                        datacnt = len (i["data"])
                        if (datacnt > minPointdetected and i["tlvType"] in [6, 7, 8]):
                            # gdata.extend(jsndata["data"])
                            #    print ("topic : {}  tnxid :{} name:{} data Length:{} datatype {} ".format(topic,jsndata["tnxid"],jsndata["name"],datacnt,i["tlvType"]))
                            if (i["tlvType"] == 6):  # pointcloud
                                for n in i["data"]:
                                    if count_frames == 0:
                                        coordinates = pd.DataFrame ({'x': n["x"], 'y': n["y"]}, index=[0])

                                    else:
                                        c = pd.DataFrame ({'x': n["x"], 'y': n["y"]}, index=[0])
                                        coordinates = coordinates.append (c)
                                    count_frames += 1  # used to count number of frames captured
                                    # everytime type 6 is detected, thats 1 frame
            #  elif (i["tlvType"] == 8):
                        #      tgt = []
                        #      for n in i["data"]:
                        #          if (n["targetIndex"] not in tgt):
                        #              tgt.append ((n["targetIndex"]))
                        # 7 TargetsPosition
                        # print(tgt)
                        # print (i)

            #split by frame
            #if (count_frames <= 20):
            #    count_frames += 1
            #    DBSCAN_ (coordinates['x'], coordinates['y'])
            ## live_update_demo (coordinates['x'], coordinates['y'])
            #else:
            #    # reset
            #    coordinates.empty
            #    plt.cla ()
            #    count_frames = 0

            if (count_frames <= 20):
                # live_update_demo (coordinates['x'], coordinates['y'])
                # print(a)
              # if not coordinates.empty:
              #      a = np.array ([coordinates['x'], coordinates['y']])
                DBSCAN_ (coordinates.to_numpy())
                count_frames += 1
                print (counter)
                # print (number_frames)
            else:  # reset
                # coordinates.empty
                plt.cla ()
                count_frames = 0
                counter = 0
            # split by time
        #   if (counter <= 10):
        #       # live_update_demo (coordinates['x'], coordinates['y'])
        #       #print(a)
        #       if not coordinates.empty:
        #           a = np.array ([coordinates['x'], coordinates['y']])
        #           DBSCAN_ (a)
        #       count_frames += 1
        #       print (counter)
        #       # print (number_frames)
        #   else:  # reset
        #       #coordinates.empty
        #       plt.cla ()
        #       count_frames = 0
        #       counter = 0
    except Exception as e:
        print (e)
        print ("bringing down zmq device")
    finally:
        pass


#if __name__ == "__main__":
#    x = threading.Thread (target=Radar_DataCollection, args=())
#    x.start ()
#    x.join ()


Radar_DataCollection()

