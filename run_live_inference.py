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
            # print("msg", message)
            if "{\"topic\": " not in message: # fix the stimulatator bug
                message = "{\"topic\": " + message

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
        num_sec_data_1.append(ml_data_array1)
        num_sec_data_2.append(ml_data_array2)
    return num_sec_data_1, num_sec_data_2

# Load models
'''device = torch.device("cpu")
modelA = m.IVODResnet34()
modelB = m.IVODResnet34()
modelsDir = 'C:/Users/WayneGuangWayTENGSof/Desktop/IVOD_Models/'
modelA.load_state_dict(torch.load(modelsDir + '/FP_Predictor/050623-FP-0992-10SEC-200MAXFRAME.pt', map_location=device))
modelB.load_state_dict(torch.load(modelsDir + '/LB_Predictor/050623-LB-0997-10SEC-200MAXFRAME.pt', map_location=device))
modelA.eval()
modelB.eval()'''

model = m.modelloader(modelname="IVOD V3")
print("Completed Model Loading")

# Initial animation data
x_data, y_data = [], []
fig, ax = plt.subplots()
ax.set_xlim(0, 10)  # for example, 10 time steps
ax.set_ylim(0, 5)   # Y axis values from 0 to 3
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
    global unpacked_radar_stream_1, unpacked_radar_stream_2
    radar_stream_1, radar_stream_2 = [], []
    # radar_stream_1, radar_stream_2 = collect_data(duration_requested=10)
    unpacked_radar_stream_1, unpacked_radar_stream_2 = [], []
    radar_stream_1, radar_stream_2 = collect_data(duration_requested=15)
    unpacked_radar_stream_1, unpacked_radar_stream_2 = unpack_data(radar_stream_1, radar_stream_2)
    print("Collect 10s data completed")
    while(True):
        print("Updating data..")
        start_collect = time.time()
        # Sustain the window shift
        new_sec_radar_stream_1, new_sec_radar_stream_2 = collect_data(duration_requested=1)
        # Discard and replace 1second every loop
        radar_stream_1 = radar_stream_1[1:] + new_sec_radar_stream_1
        radar_stream_2 = radar_stream_2[1:] + new_sec_radar_stream_2
        unpacked_radar_stream_1, unpacked_radar_stream_2 = unpack_data(radar_stream_1, radar_stream_2)
        end_collect = time.time() - start_collect
        print("Time spent to collect 1s data", end_collect)

def unpack_data(r1, r2):
    unpacked_r1 = [frame for s in r1 for frame in s]
    unpacked_r2 = [frame for s in r2 for frame in s]
    return unpacked_r1, unpacked_r2

def inference():
    # initialize by collecting 10s worth of data first
    while len(unpacked_radar_stream_1) < 1 or len(unpacked_radar_stream_2) < 1:
        time.sleep(0.5)
    else:
        print("Okay to infer sec of data available for r1 and r2", len(unpacked_radar_stream_1), len(unpacked_radar_stream_2))
    print("Initialize loading of first 10s completed")
    start_loop = time.time()
    PAST_PREDICTS = []
    TIME_STEP = []
    # Run for num seconds
    run_time = 3600
    global x_data, y_data
    for i in range(run_time):
        # Inference Preprocess
        print("Inferring data of length:", len(unpacked_radar_stream_1), len(unpacked_radar_stream_2) )
        input, im, pprocess_time_take = ieh.live_inference_preprocess(unpacked_radar_stream_1[0:model.metadata.FRAME_SIZE], unpacked_radar_stream_2[0:model.metadata.FRAME_SIZE])
        # Calculations
        start_calc = time.time()
        FP_Predict, LB_Predict, FP_Score, LB_Score, passengerNo = model.calculate_output(input)
        print("FP Predict score", FP_Score)
        print("LB Predict score", LB_Score)
        FP_confidence_score = abs(np.log((1.0 - FP_Score + 1e-10))).long().item()
        LB_confidence_score = abs(np.log((1.0 - LB_Score + 1e-10))).long().item()

        end_calc = time.time() - start_calc
        # Total passengers predicted = Driver seat passenger (1) + all seats detected
        total_passengers = 1 + passengerNo

        print(f"Prediction: D:1 FP:{FP_Predict} FP Confidence: {FP_confidence_score} LB:{LB_Predict} LB Confidence: {LB_confidence_score} Time Taken for Preprocess: {pprocess_time_take}, for calculations {end_calc}")
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







