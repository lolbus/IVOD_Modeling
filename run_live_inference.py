import model as m
import torch
import InferenceEngineHandler as ieh
import zmq
import json
import time
context = zmq.Context()
subSocket = context.socket(zmq.SUB)
subSocket.connect("tcp://192.168.70.120:11002")
subSocket.setsockopt_string(zmq.SUBSCRIBE, "radar_data")

def collect_data():
    ml_data_array1 = []
    ml_data_array2 = []
    start = time.time()
    time_take = 0.0
    while time_take < 10.0:
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
    return ml_data_array1, ml_data_array2


modelA = m.IVODResnet34()
modelB = m.IVODResnet34()
modelsDir = 'C:/Users/WayneGuangWayTENGSof/Desktop/IVOD_Models/'
modelA.load_state_dict(torch.load(modelsDir + '/FP_Predictor/050623-FP-0992-10SEC-200MAXFRAME.pt', map_location=torch.device('cpu')))
modelB.load_state_dict(torch.load(modelsDir + '/LB_Predictor/050623-LB-0997-10SEC-200MAXFRAME.pt', map_location=torch.device('cpu')))
device = torch.device("cpu")
modelA.eval()
modelB.eval()
print("Completed code")

# Change this to read from zmq on 7 June 23
with open("samplecapture.txt", 'r') as f:
    x = f.read()
x = eval(x)

input1, time_take = ieh.live_inference_preprocess(x[0][0:200], x[1][0:200])

with torch.no_grad():
    input1 = input1.to(device)
    outputs_FP = modelA(input1)
    outputs_LB = modelB(input1)
    preds_FP = (torch.sigmoid(outputs_FP) > 0.5).long().item()
    preds_LB = (torch.sigmoid(outputs_LB) > 0.5).long().item()

print(f"Prediction: D:1 FP:{preds_FP} LB:{preds_LB} Time Taken for Preprocess: {time_take}")






