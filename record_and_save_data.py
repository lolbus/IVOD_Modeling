import model as m
import zmq
import json
import time
from threading import Thread
from metadata import DatasetMeta
import os


class status_handler(object):
    def __init__(self):
        self.updated = False


statushandler = status_handler()

context = zmq.Context()
# publish output target
pubSocket = context.socket(zmq.PUB)
pubSocket.connect("tcp://192.168.70.120:11332")
topic = "ivod_demo_inf"
model_name = "IVOD DATA COLLECTOR"

subSocket = context.socket(zmq.SUB)
subSocket.connect("tcp://192.168.70.120:11002")
subSocket.setsockopt_string(zmq.SUBSCRIBE, "radar_data")


# publish topic,  ivod_demo_inf
# Update function


def collect_data(duration_requested: int):
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
            # if "{\"topic\": " not in message: # fix the stimulatator bug
            # message = "{\"topic\": " + message

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
model = m.modelloader(modelname=model_name)
print("Completed Model Loading")


def collect_and_save_data_static_loop():
    global unpacked_radar_stream_1, unpacked_radar_stream_2
    unpacked_radar_stream_1 = []
    unpacked_radar_stream_2 = []
    while True:
        start = time.time()
        if len(unpacked_radar_stream_1) >= model.metadata.FRAME_SIZE + 5:
            unpacked_radar_stream_1 = unpacked_radar_stream_1[
                                      len(unpacked_radar_stream_1) - model.metadata.FRAME_SIZE - 5:]
        if len(unpacked_radar_stream_2) >= model.metadata.FRAME_SIZE + 5:
            unpacked_radar_stream_2 = unpacked_radar_stream_2[
                                      len(unpacked_radar_stream_2) - model.metadata.FRAME_SIZE - 5:]
        # ml_data_array1 = []
        # ml_data_array2 = []
        # frame_len = 0
        # while frame_len < 10:
        recv = subSocket.recv_string()
        topic, message = recv.split(" ", 1)
        # print("msg", message)
        if "{\"topic\": " not in message:  # fix the stimulatator bug
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
                    tmp = [int(round(p.get("x") * 100)), int(round(p.get("y") * 100)), int(round(p.get("z") * 100)),
                           int(round(p.get("doppler") * 1000))]
                    if name == "radar1":
                        this_frame_pts_1.append(tmp)
                    elif name == "radar2":
                        this_frame_pts_2.append(tmp)
            if name == "radar1":
                # ml_data_array1.append(this_frame_pts_1)
                unpacked_radar_stream_1.append(this_frame_pts_1)
            elif name == "radar2":
                # ml_data_array2.append(this_frame_pts_2)
                unpacked_radar_stream_2.append(this_frame_pts_2)
            statushandler.updated = True


# Stream a sample local saved capture
'''with open("samplecapture.txt", 'r') as f:
    x = f.read()
x = eval(x)'''


def unpack_data(r1, r2):
    unpacked_r1 = [frame for s in r1 for frame in s]
    unpacked_r2 = [frame for s in r2 for frame in s]
    return unpacked_r1, unpacked_r2



metadata = DatasetMeta()
directory = metadata.SAVE_DATA_DIR


def write(data: list, to: str):
    with open(to, "w") as file:
        file.write(str(data))
        print("Finished writing: ", to)


def inference_and_save():
    # initialize by collecting 10s worth of data first
    while len(unpacked_radar_stream_1) < 1 or len(unpacked_radar_stream_2) < 1 or not statushandler.updated:
        print("Updated status", statushandler.updated)
        time.sleep(0.5)
    else:
        print("Okay to infer sec of data available for r1 and r2", len(unpacked_radar_stream_1),
              len(unpacked_radar_stream_2))
        print("Update status", statushandler.updated)
    print("Initialize loading of first 10s completed")
    start_loop = time.time()

    # Run for num seconds
    run_time = 128800
    for i in range(run_time):
        if statushandler.updated and len(unpacked_radar_stream_1) >= model.metadata.FRAME_SIZE:
            # Inference Preprocess
            print("Saving data of length:", len(unpacked_radar_stream_1), len(unpacked_radar_stream_2))
            d = [unpacked_radar_stream_1[0:model.metadata.FRAME_SIZE],
                 unpacked_radar_stream_2[0:model.metadata.FRAME_SIZE]]

            file_count = str(len(os.listdir(directory)))
            filename = metadata.SAVE_DATA_DIR + "/" + file_count + ".txt"
            write(data=d, to=filename)
            statushandler.updated = False
        time.sleep(1)
    end_loop = time.time() - start_loop
    print(f"Completed 100 predicts in {end_loop}")


update_data_static = Thread(target=collect_and_save_data_static_loop)
update_data_static.start()

collection = Thread(target=inference_and_save)
collection.start()
