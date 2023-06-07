import model as m
import torch
import InferenceEngineHandler as ieh
import zmq
import json
import time
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from threading import Thread




context = zmq.Context()
# publish output target
pubSocket = context.socket(zmq.PUB)
pubSocket.connect("tcp://192.168.70.120:11332")
topic = "ivod_demo_inf"

subSocket = context.socket(zmq.SUB)
subSocket.connect("tcp://192.168.70.120:11002")
subSocket.setsockopt_string(zmq.SUBSCRIBE, "radar_data")

#publish topic,  ivod_demo_inf
# Update function
def update(frame):
    ax.set_xlim(x_data[0], x_data[-1])
    line.set_data(x_data, y_data)
    return line,

def collect_data(duration_requested:int):
    ml_data_array1 = []
    ml_data_array2 = []
    num_sec_data_1 = []
    num_sec_data_2 = []
    start = time.time()
    time_take = 0.0
    for sec_collected in range(duration_requested):
        while time_take < 1.0:
            recv = subSocket.recv_string()
            topic, message = recv.split(" ", 1)
            data = json.loads(message)
            name = data["name"]
            packet = data["packets"]
            if packet:
                packet = packet[0]
                packet = packet["data"]
                this_frame_pts_1 = []
                this_frame_pts_2 = []
                for p in packet:
                    if p.get("x") is not None:
                        tmp = [p.get("x"), p.get("y"), p.get("z")]
                        if name == "radar1":
                            this_frame_pts_1.append(tmp)
                        elif name == "radar2":
                            this_frame_pts_2.append(tmp)
                if name == "radar1":
                    ml_data_array1.append(this_frame_pts_1)
                elif name == "radar2":
                    ml_data_array2.append(this_frame_pts_2)
            time_take = time.time() - start
        num_sec_data_1 += ml_data_array1
        num_sec_data_2 += ml_data_array2
    return num_sec_data_1, num_sec_data_2

# Load models
device = torch.device("cpu")
modelA = m.IVODResnet34()
modelB = m.IVODResnet34()
modelsDir = 'C:/Users/WayneGuangWayTENGSof/Desktop/IVOD_Models/'
modelA.load_state_dict(torch.load(modelsDir + '/FP_Predictor/050623-FP-0992-10SEC-200MAXFRAME.pt', map_location=device))
modelB.load_state_dict(torch.load(modelsDir + '/LB_Predictor/050623-LB-0997-10SEC-200MAXFRAME.pt', map_location=device))
modelA.eval()
modelB.eval()
print("Completed Model Loading")

# Initial animation data
x_data, y_data = [], []
fig, ax = plt.subplots()
ax.set_xlim(0, 10)  # for example, 10 time steps
ax.set_ylim(0, 3)   # Y axis values from 0 to 3
line, = ax.plot(x_data, y_data)

# Stream a sample local saved capture
'''with open("samplecapture.txt", 'r') as f:
    x = f.read()
x = eval(x)'''

def updateGraph():
    # The FuncAnimation function
    ani = FuncAnimation(fig, update, frames=2)
    plt.show()

def collect_and_update_data():
    global radar_stream_1, radar_stream_2
    radar_stream_1, radar_stream_2 = [], []
    radar_stream_1, radar_stream_2 = collect_data(duration_requested=10)
    print("Collect 10s data completed")
    while(True):
        print("Updating data..")
        start_collect = time.time()
        # Sustain the window shift
        new_sec_radar_stream_1, new_sec_radar_stream_2 = collect_data(duration_requested=1)
        # Discard and replace 1second every loop
        radar_stream_1 = radar_stream_1[1:] + new_sec_radar_stream_1
        radar_stream_2 = radar_stream_2[1:] + new_sec_radar_stream_2
        end_collect = time.time() - start_collect
        print("Time spent to collect 1s data", end_collect)

def inference():
    # initialize by collecting 10s worth of data first
    while len(radar_stream_1) < 1 or len(radar_stream_2) < 1:
        time.sleep(0.5)
    print("Initialize loading of first 10s completed")
    start_loop = time.time()
    PAST_PREDICTS = []
    TIME_STEP = []
    # Run for num seconds
    run_time = 3600
    global x_data, y_data
    for i in range(run_time):
        # Inference Preprocess
        input, pprocess_time_take = ieh.live_inference_preprocess(radar_stream_1[0:200], radar_stream_2[0:200])
        # Calculations
        start_calc = time.time()
        with torch.no_grad():
            input1 = input.to(device)
            outputs_FP = modelA(input)
            outputs_LB = modelB(input)
            preds_FP = (torch.sigmoid(outputs_FP) > 0.5).long().item()
            preds_LB = (torch.sigmoid(outputs_LB) > 0.5).long().item()
        end_calc = time.time() - start_calc
        # Total passengers predicted = Driver seat passenger (1) + all seats detected
        total_passengers = 1 + preds_FP + preds_LB

        print(f"Prediction: D:1 FP:{preds_FP} LB:{preds_LB} Time Taken for Preprocess: {pprocess_time_take}, for calculations {end_calc}")
        # print(f"Total passengers predicts {total_passengers}. Total Inference duration {pprocess_time_take + end_calc}")
        TIME_STEP.append(i)
        PAST_PREDICTS.append(total_passengers)
        if len(TIME_STEP) > 10:
            TIME_STEP = TIME_STEP[1:]
        if len(PAST_PREDICTS) > 10:
            PAST_PREDICTS = PAST_PREDICTS[1:]
        line, = plt.plot(TIME_STEP, PAST_PREDICTS, 'r-')
        x_data = TIME_STEP
        y_data = PAST_PREDICTS
        pubSocket.send_string(topic + " " + str(y_data[-1]))
        # print(x_data)
        # print(y_data)
        time.sleep(1)

    end_loop = time.time() - start_loop
    print(f"Completed 100 predicts in {end_loop}")

updatedata = Thread(target=collect_and_update_data)
updatedata.start()

collection = Thread(target=inference)
collection.start()



while len(x_data) < 10:
    print("Not enough  data collected yet", len(x_data))
    time.sleep(10)
updateGraph()







