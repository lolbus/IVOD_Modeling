# Training Data Preprocessing

from torchvision import transforms
import json
import torch
import datahandler as dh
import os
from PIL import Image
import torchvision.transforms as transforms
from metadata import DatasetMeta
import time
import numpy as np
import pandas as pd

metadata = DatasetMeta()
instances_each_class_desired = metadata.data_class_distribution

def osdir_handler(training_json_path_directory='./', bad_data_folders=[]):
    '''
    Input path to directory containing, 1.PassengerNo_1 (D), 2.PassengerNo_2 (D+FP), 3.PassengerNo_2 (D+LB), 4.PassengerNo_3 (D+FP+LB)
    Output list of [data_id_identity, strlabel, str specifying location path of all both_radar.txt] for all data instance
    '''
    start = time.time()
    training_files = []

    # loop over all D, D+FP and D+FP+LB folders, load all the related files into list object
    for i, c in enumerate(metadata.STR_LABELS_LIST):
        instances_to_processed = instances_each_class_desired[i]
        print(f"preparing {instances_to_processed} instances for class {c}")
        extra_data = metadata.EXTRA_DATA  # There are extra data instances (more than 10k) for some of the classes, for e.g (D) class has 34 extra instance
        '''start_id_for_this_class = i * 10000 + extra_data[
            i - 1] if i != 0 else 0  # 0-10033 for (D), 10034-20038 for (D+FP) 20039-30049 for (D+LB) 30050-40049(D+FP+LB)'''
        start_id_for_this_class = 0
        new_method_count = 0
        for count, (root, dirs, files) in enumerate(
                os.walk(f"{training_json_path_directory}/{c}/")):  # ROOT_DIR/CLASS_FOLDER/
            # check if 'Both Radar.txt' exists in the list of files
            if count >= instances_to_processed or new_method_count >= instances_to_processed:
                print(f"Finished processing {count} data instances. Current len {len(training_files)}")
                break

            # Handles the new txt files containing 185 frames of Radar1/2
            if root == f"{training_json_path_directory}/{c}/":
                new_method_count = 0
                for file in files:
                    if file.split(".")[0].isdigit():
                        id_identity = int(file.split(".")[0])
                        data_id = start_id_for_this_class + id_identity
                        if data_id in bad_data_folders:  # Skip folders that are in the blacklist
                            continue
                        datainstance = [data_id, c, f"{root}/{file}", id_identity]
                        training_files.append(datainstance)
                        new_method_count += 1
                        if new_method_count > instances_to_processed:
                            break

            else:
                # Handles the old txt files containing list of JSON
                if root.split("/")[-1].isdigit():
                    id_identity = int(root.split("/")[-1])
                    data_id = start_id_for_this_class + id_identity
                    if data_id in bad_data_folders:  # Skip folders that are in the blacklist
                        continue
                if 'Both Radar.txt' in files:
                    datainstance = [data_id, c, f"{root}/Both Radar.txt", id_identity] # Each instance metadata is its data_id, the true label associated, its origin location and the original id identity when it was raw format
                    # print(f"Add data {datainstance}")
                    training_files.append(datainstance)
                elif root.split("/")[-1].isdigit() and not 'Both Radar.txt' in files:
                    bad_datainstance = [data_id, c, root]
                    print(f"Bad data detected!!!{bad_datainstance}. count {count} foldername {id_identity}")



            
        print(f"completed loading for class {c} {metadata.STR_TO_ONEHOT_LABELS[c]}. Total instances {len(training_files)}")

    time_take = time.time() - start
    return training_files, time_take


def load_bad_data(dir={
    'file_path1': './folder1_bad_data.txt',
    'file_path2': './folder2_bad_data.txt',
    'file_path3': './folder3_bad_data.txt',
    'file_path4': './folder4_bad_data.txt',
    'file_path_devtest': './devtest.txt'
}):
    '''
    Load data to me omitted from preprocessing.
    Input dictionary object with above default format
    Output a list of data id that shall be omitted from data preprocessing
    '''
    start = time.time()

    file_path1 = dir['file_path1']
    file_path2 = dir['file_path2']
    file_path3 = dir['file_path3']
    file_path4 = dir['file_path4']
    file_path_devtest = dir['file_path_devtest']  # Omit adding data instance from the devtest set

    # Load bad data of D+FP+lB
    with open(file_path4, 'r') as file:
        list_string = file.read()
        f4_bad_dirs = (np.array(eval(list_string)) + 30000 + metadata.EXTRA_DATA[2]).tolist()
        loaded_list = f4_bad_dirs

        # Load bad data of D+lB
    with open(file_path3, 'r') as file:
        list_string = file.read()
        f3_bad_dirs = (np.array(eval(list_string)) + 20000 + metadata.EXTRA_DATA[1]).tolist()
        loaded_list += f3_bad_dirs

    # Load bad data of D+FP
    with open(file_path2, 'r') as file:
        list_string = file.read()
        f2_bad_dirs = (np.array(eval(list_string)) + 10000 + metadata.EXTRA_DATA[0]).tolist()
        loaded_list += f2_bad_dirs

    # Load bad data of D
    with open(file_path1, 'r') as file:
        list_string = file.read()
        f1_bad_dirs = (np.array(eval(list_string))).tolist()
        loaded_list += f1_bad_dirs

    # Load devtest data to omit
    with open(file_path_devtest, 'r') as file:
        list_string = file.read()
        devtest_bad_dirs = np.array(eval(list_string)).tolist()
        loaded_list += devtest_bad_dirs
    loaded_list.sort()

    print("List object loaded successfully. Total blacklisted folders:", len(loaded_list))
    print("Loaded List:", loaded_list)
    time_take = time.time() - start
    return np.array(loaded_list), time_take


def training_preprocess(dataid, strclass, txt_file, augmentation=False, whitenoise_scale=0.01,
                        dtype='torch.float32', BothRadarTxt=True):
    '''
    Must be replicable by inference engine preprocessing.
    Perform data preprocess for training data as input for ML Model.
    1. Take in a BothRadar.txt,
    2, Load all json objects.
    3. Process all frames, do necessary padding/trimming
    4. Perform normalization and standization
    5. Perform data augmentation (White Noise, X offset, Y offset, X Gap offset)
    convert all frames into one input tensor
    Input: path and filename of BothRadar.txt file containing list of JSON objects
    Output: Torch Tensor data
    '''
    start = time.time()
    dataidentity = (dataid, strclass)
    augmentation_factor = metadata.augmentation_rate[metadata.STR_TO_CLASS_LABELS[strclass]]

    # Essential preprocess of BothRadar.txt file
    if BothRadarTxt:
        this_data_radar1_frames_list, this_data_radar2_frames_list = dh.generate_frames_list(txt_file,
                                                                                             metadata.FRAME_LENGTH)
    else:
        # print(f"new format processing {txt_file}")
        this_data_radar1_frames_list, this_data_radar2_frames_list = dh.generate_frames_list_from_txt(txt_file,
                                                                                             metadata.FRAME_LENGTH)

    # Tensorize the frames list, Pad data tensor height, 2 Methods, pad zeros or interpolate and duplicating neighbouring pixel values and concatenate them
    torch_tensor = dh.tensorize_list(this_data_radar1_frames_list, this_data_radar2_frames_list, metadata.FRAME_SIZE,
                                     metadata.FRAME_LENGTH, dataidentity)

    if torch_tensor.shape[0] != metadata.FRAME_SIZE:  # Failed to tensorize will return a int
        print("returning int instance as this instance is undersized and has to be dropped")
        return dataid, strclass, None, None, None, None

    # Data Normalize
    torch_tensor = dh.normalize_tensor(torch_tensor, max_values=metadata.RGB_MAX_VALUES,
                                       min_values=metadata.RGB_MIN_VALUES)

    # Save as png image using PIL
    image_array = np.uint8(torch_tensor.numpy() * 255)
    im_bef_stand = Image.fromarray(image_array)

    # Data Standardize
    torch_tensor = dh.standardize_tensor(torch_tensor, rgbmean=metadata.RGB_MEAN_VALUES, rgbstd=metadata.RGB_STD_VALUES)
    im_bef_aug = None

    if augmentation:
        im_bef_aug = transforms.ToPILImage()(torch_tensor[0])
        # Return result with augmentation noise (Unlike inference which skip this steps)
        replicate_data = []
        for replicate in range(augmentation_factor):
            replicate_data.append(dh.augmentation_handler(torch_tensor, whitenoise_scale=whitenoise_scale))
        replicate_data_tensor = torch.tensor(replicate_data)
        torch_tensor = torch.cat( (torch_tensor, replicate_data_tensor), dim=0)


    im = transforms.ToPILImage()(torch_tensor[-1])

    # Save the true label
    strlabel = strclass
    onehotlabel = metadata.STR_TO_ONEHOT_LABELS[strlabel]

    time_take = time.time() - start

    return torch_tensor, onehotlabel, im, im_bef_stand, im_bef_aug, time_take

def training_set_preprocess(dataset:list, augmentation=False):
    """
    Preprocess the list of dataset
    Input lists of data ID and locations
    Output dataframe containing structured info
    """
    # Create new data df
    df = pd.DataFrame(columns=["Data ID", "(D)", "(FP)", "(LB)", "strLabel", "classLabel"])
    train_tensor = torch.empty(size=(0, 3, metadata.FRAME_SIZE, metadata.FRAME_LENGTH * 2), dtype=torch.float32)
    train_label_tensor = torch.empty(size=(0, 4), dtype=torch.float32)
    bad_data_discovered = []
    for i, data in enumerate(dataset):
        data_id = data[0] # The id given in this processed dataset
        strlabel = data[1] # strlabel
        data_file_origin = data[2] # The origin of the data
        original_data_identity = data[3] # original data identity when it was raw

        if data_file_origin.split("/")[-1] == "Both Radar.txt":
            # preprocess data
            x_final, y_onehot_str, final_heatmap, before_stand_heatmap, before_aug_heatmap, preprocess_time_take = training_preprocess(dataid=data_id,
                                                                                                                                       strclass=strlabel,
                                                                                                                                       txt_file=data_file_origin,
                                                                                                                                       augmentation = False)
        else:
            x_final, y_onehot_str, final_heatmap, before_stand_heatmap, before_aug_heatmap, preprocess_time_take = training_preprocess(
                dataid=data_id,
                strclass=strlabel,
                txt_file=data_file_origin,
                augmentation=False,
                BothRadarTxt= False)


        if type(x_final) == int:
            s = (str(x_final), y_onehot_str)
            print("Bad data discovered! ", s)
            bad_data_discovered.append(s)
            continue


        # save heat maps for visual inspection
        dh.save_image(before_stand_heatmap, dir=f"./before_stand_heatmap/{strlabel}_{original_data_identity}_{data_id}.png")
        dh.save_image(final_heatmap, dir=f"./final_heatmap/{strlabel}_{original_data_identity}_{data_id}.png")
        if augmentation:
            dh.save_image(before_aug_heatmap, dir=f"./before_aug_heatmap/{strlabel}_{original_data_identity}_{data_id}.png")


        # concat labels and other essential structured information into df
        y_onehot = eval(y_onehot_str)
        file_data_dict = {"Data ID": data_id, "(D)":y_onehot[0], "(FP)":y_onehot[1], "(LB)":y_onehot[2], "strLabel": strlabel, "classLabel": metadata.STR_TO_CLASS_LABELS[strlabel]}

        # save the y label tensor and its respective onehot
        y_final = torch.tensor(y_onehot + [data_id], dtype = torch.int)

        # Append the dictionary as a row in the DataFrame
        df = pd.concat([df, pd.DataFrame([file_data_dict])], ignore_index=True)

        # Append X tensor by concatenate method
        train_tensor = torch.cat((train_tensor, x_final), dim=0)
        train_label_tensor = torch.cat((train_label_tensor, y_final.unsqueeze(0)), dim=0)
        if i % 1000 == 0:
            print(f"Completed {i}/{len(dataset)}")
    print("Bad data detected ", bad_data_discovered)
    return df, train_tensor, train_label_tensor
