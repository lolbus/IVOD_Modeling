import model as m
import zmq
import json
import time
from threading import Thread
from metadata import DatasetMeta
import os
import InferenceEngineHandler as ieh
from pynput import keyboard
# import record_and_save_cctv as CCTVHandler
import InferenceLogicMap
import Live_Visualize

metadata = DatasetMeta()


class status_handler(object):
    def __init__(self):
        self.updated = False
        self.start = False
        self.predict_memory = [0]
        self.data_radar_1 = []
        self.data_radar_2 = []
        self.data_radar_1_conv =[]
        self.data_radar_2_conv = []
        self.models_dict = {}
        for key in InferenceLogicMap.ModelMapper:
            value = InferenceLogicMap.ModelMapper[key]
            if value not in self.models_dict.keys():
                self.models_dict[value] = m.modelloader(value)
        self.str_true_label_of_interest = ""
        self.pax_count_of_interest = 0
        self.directory = ""
        self.save_incorrect_only = False
        self.prompting = False
        self.saved_data_count = 0
        self.not_collection = False

statushandler = status_handler()


def on_press(key):
    if key == keyboard.Key.f9:
        if not statushandler.start:
            prompt_settings()
        else:
            statushandler.start = False
            statushandler.prompting = True
            print("Stopped!")
            time.sleep(5)
            statushandler.prompting = False
        print(f'Enter button pressed. Started:{statushandler.start}')

context = zmq.Context()
# publish output target
pubSocket = context.socket(zmq.PUB)
pubSocket.connect("tcp://192.168.70.120:11332")
topic = "ivod_demo_inf"
model_name = "IVOD DATA COLLECTOR"

subSocket = context.socket(zmq.SUB)
subSocket.connect("tcp://192.168.70.120:11002")
subSocket.setsockopt_string(zmq.SUBSCRIBE, "radar_data")

#statushandler
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

def check_and_trim_data():
    if len(statushandler.data_radar_1) >= model.metadata.FRAME_SIZE + 5:
        statushandler.data_radar_1 = statushandler.data_radar_1[
                                     len(statushandler.data_radar_1) - model.metadata.FRAME_SIZE - 5:]
    if len(statushandler.data_radar_2) >= model.metadata.FRAME_SIZE + 5:
        unpacked_radar_stream_2 = statushandler.data_radar_2[
                                  len(statushandler.data_radar_2) - model.metadata.FRAME_SIZE - 5:]
    if len(statushandler.data_radar_1_conv) >= model.metadata.FRAME_SIZE + 5:
        statushandler.data_radar_1_conv = statushandler.data_radar_1_conv[
                                          len(statushandler.data_radar_1_conv) - model.metadata.FRAME_SIZE - 5:]
    if len(statushandler.data_radar_2_conv) >= model.metadata.FRAME_SIZE + 5:
        statushandler.data_radar_2_conv = statushandler.data_radar_2_conv[
                                          len(statushandler.data_radar_2_conv) - model.metadata.FRAME_SIZE - 5:]

def collect_and_save_data_static_loop():
    statushandler.data_radar_1 = []
    statushandler.data_radar_2 = []
    statushandler.data_radar_1_conv = []
    statushandler.data_radar_2_conv = []
    while True:
        start = time.time()

        # Trim the data to maintain the desirable size
        check_and_trim_data()

        recv = subSocket.recv_string()
        topic, message = recv.split(" ", 1)
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
            this_frame_pts_1_conventional = []
            this_frame_pts_2_conventional = []
            for p in packet:
                if p.get("x") is not None:
                    tmp = [int(round(p.get("x") * 100)), int(round(p.get("y") * 100)), int(round(p.get("z") * 100)),
                           int(round(p.get("doppler") * 1000))]
                    # tmp_conventional = [int(round(p.get("x") * 100)) * 0.01, int(round(p.get("y") * 100)) * 0.01, int(round(p.get("z") * 100)) * 0.01]
                    tmp_conventional = [p.get("x"), p.get("y"), p.get("z")]
                    if name == "radar1":
                        this_frame_pts_1.append(tmp)
                        this_frame_pts_1_conventional.append(tmp_conventional)
                    elif name == "radar2":
                        this_frame_pts_2.append(tmp)
                        this_frame_pts_2_conventional.append(tmp_conventional)
            if name == "radar1" and len(this_frame_pts_1) > 0:
                # ml_data_array1.append(this_frame_pts_1)
                statushandler.data_radar_1.append(this_frame_pts_1[:149])
                statushandler.data_radar_1_conv.append(this_frame_pts_1_conventional[:149])
                #print("add this_frame_pts_1_conventional[:149]", len(this_frame_pts_1_conventional[:149]))
            elif name == "radar2" and len(this_frame_pts_2) > 0:
                # ml_data_array2.append(this_frame_pts_2)
                statushandler.data_radar_2.append(this_frame_pts_2[:149])
                statushandler.data_radar_2_conv.append(this_frame_pts_2_conventional[:149])
                #print("add this_frame_pts_2_conventional[:149]", len(this_frame_pts_2_conventional[:149]))
            statushandler.updated = True


def write(data: list, to: str):
    with open(to, "w") as file:
        file.write(str(data))
        #print("Finished writing: ", to)

def save_data():
    # print("Saving data of length:", len(statushandler.data_radar_1), len(statushandler.data_radar_2))
    d = [statushandler.data_radar_1[0:model.metadata.FRAME_SIZE],
         statushandler.data_radar_2[0:model.metadata.FRAME_SIZE]]

    file_count = str(len(os.listdir(statushandler.directory)))
    filename = statushandler.directory + "/" + file_count + ".txt"
    if statushandler.saved_data_count % 10 == 0:
        print(f"Finished writing 10 files. Writing to..", filename)
    write(data=d, to=filename)
    statushandler.updated = False
    statushandler.saved_data_count += 1

def inference_and_save():
    check_ready()
    start_loop = time.time()
    # Run for num seconds
    run_time = 128800
    for i in range(run_time):
        if statushandler.updated and len(statushandler.data_radar_1) >= model.metadata.FRAME_SIZE:
            if not statushandler.start:
                # Inference Preprocess
                input, im, pprocess_time_take = ieh.live_inference_preprocess(
                    statushandler.data_radar_1_conv[0:model.metadata.FRAME_SIZE],
                    statushandler.data_radar_2_conv[0:model.metadata.FRAME_SIZE])

                # Calculations
                #EC_Predict, EC_Score, passengerNo = model.calculate_ec_output(input)
                #Test_Predict, Test_Score, Test_passengerNo = model.calculate_test_output(input)


                # Print predict result
                #print(f"The Car is Empty: {EC_Predict}, Score {EC_Score}  PassengerNo: {passengerNo}. Press space bar to start..")

                #print(f"Test Model: {Test_Predict}, +ve Score {Test_Score}  PassengerNo: {Test_passengerNo}. Press space bar to start..")
            else:
                # Saving
                if not statushandler.save_incorrect_only:
                    save_data()
                else:
                    if not statushandler.not_collection:
                        # trigger is not correct predict (target not equal predict)
                        trigger = not statushandler.pax_count_of_interest == statushandler.predict_memory[-1]

                    else:
                        # trigger is get an equal predict when collecting NOT instances of target
                        trigger = statushandler.pax_count_of_interest == statushandler.predict_memory[-1]
                    if trigger:
                        save_data()
                        #print("save an instance of in corect predict success")
                        #time.sleep(1)
                    else:
                         print("no trigger detected, not saving the current data")
                         time.sleep(0.5)
        time.sleep(1)
    end_loop = time.time() - start_loop
    print(f"Completed 100 predicts in {end_loop}")

def mvp_v4_inference():
    '''perform inference using the mvp_v3 logic map, input global data, output total passenger No'''

    logic_map = InferenceLogicMap.MVP_Model4_Logic_Map
    model_wrapper = InferenceLogicMap.ModelMapper
    result = -1
    current_status = "0 Pax Predictor"
    end = False
    LogicSequence = []
    while not end:
        model_name = model_wrapper[current_status]
        model = statushandler.models_dict[model_name]
        input, im, pprocess_time_take = ieh.live_inference_preprocess(
            statushandler.data_radar_1_conv[0:model.metadata.FRAME_SIZE], statushandler.data_radar_2_conv[0:model.metadata.FRAME_SIZE])
        #print("current status", current_status, model)
        if current_status == "CCTV Person Counter":
            #binary_output, score = max(CCTVHandler.statusHandler.pax_counter_list), 1.
            binary_output, score = 0, 0.0
        else:
            binary_output, score = model.calculate_modeler_binary_output(input)
        next_status, end = logic_map[current_status][int(binary_output)]
        this_step = current_status
        LogicSequence.append((this_step, round(score.item(), 5)))
        #if type(next_status) == int:
        if end:
            result = next_status
        current_status = next_status
    print("Finish predict! ", LogicSequence)
    return result

def check_ready():
    # initialize by collecting 10s worth of data first
    while len(statushandler.data_radar_1) < 1 or len(statushandler.data_radar_2) < 1 or not statushandler.updated:
        # print("Updated status", statushandler.updated)
        # print("CCTV predict:", max(CCTVHandler.statusHandler.pax_counter_list))
        time.sleep(1.0)
    else:
        print("Ready to infer sec of data available for r1 and r2", len(statushandler.data_radar_1),
              len(statushandler.data_radar_2))
        print("Update status", statushandler.updated)
    print("Initialize loading of first 10s completed")


def inference_monitoring():
    check_ready()
    start_loop = time.time()
    PAST_PREDICTS = []
    TIME_STEP = []
    # Run for num seconds
    run_time = 3600
    global x_data, y_data
    for i in range(run_time):
        if statushandler.updated and not statushandler.prompting:
            # Inference Preprocess
            TIME_STEP.append(i)
            total_passengers = mvp_v4_inference()
            PAST_PREDICTS.append(total_passengers)
            if len(TIME_STEP) > 10:
                TIME_STEP = TIME_STEP[1:]
            if len(PAST_PREDICTS) > 10:
                PAST_PREDICTS = PAST_PREDICTS[1:]
            x_data = TIME_STEP
            statushandler.predict_memory = PAST_PREDICTS
            statushandler.updated = False
            pubSocket.send_string(topic + " " + str(statushandler.predict_memory[-1]))
            print("Predicts memory: ", statushandler.predict_memory)
        # print(x_data)
        # print(y_data)
        if not statushandler.start:
            time.sleep(2)
        else:
            time.sleep(1.5)
    end_loop = time.time() - start_loop
    print(f"Completed 100 predicts in {end_loop}")


def prompt_settings():
    statushandler.prompting = True
    statushandler.str_true_label_of_interest = input("Enter the true label of interest (E.g \"NOT D\" or \"D+FP\")\n").upper()
    if "not" in statushandler.str_true_label_of_interest:
        statushandler.not_collection = True
        statushandler.str_true_label_of_interest= statushandler.str_true_label_of_interest.split(" ")[1]
    else:
        statushandler.str_true_label_of_interest = statushandler.str_true_label_of_interest.replace(" ", "")
    statushandler.pax_count_of_interest = len(statushandler.str_true_label_of_interest.split("+"))
    try:
        statushandler.directory = metadata.SAVE_DATA_DICT[statushandler.str_true_label_of_interest]
        statushandler.save_incorrect_only = True if input("Save incorrect predicts only? (y/n) \n").lower() == "y" else False
        print("Label", statushandler.str_true_label_of_interest)
        print("Not collection: ", statushandler.not_collection)
        print("directory to save", statushandler.directory)
        print("Save incorrect only", statushandler.save_incorrect_only)
        print("Pax count of interest", statushandler.pax_count_of_interest)
        time.sleep(5)
        statushandler.start = True

    except Exception as e:
        print(e)
        statushandler.start = False
        print(f"Failed to start! Key {statushandler.str_true_label_of_interest} does not exist in the label dict!")
    statushandler.prompting = False



if __name__ == "__main__":
    print("Started successfully")


# Start the Keyboard listener thread
listener = keyboard.Listener(on_press=on_press)
listener_thread = Thread(target=listener.start)
listener_thread.start()


# Collect and remember the data
update_data_static = Thread(target=collect_and_save_data_static_loop)
update_data_static.start()

# Perform saving of data
collection = Thread(target=inference_and_save)
collection.start()

# Perform live inference while model run
collection = Thread(target=inference_monitoring)
collection.start()

# Collect video feed stream data
# streaming_thread = Thread(target=CCTVHandler.stream)
# streaming_thread.start()

# Infer and update the predicts of CCTV model
'''infer_thread = Thread(target=CCTVHandler.infer_and_save)
infer_thread.start()'''

Live_Visualize.visualization_main()
