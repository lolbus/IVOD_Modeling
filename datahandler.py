import json
import torch
from torchvision import transforms
from metadata import DatasetMeta

metadata = DatasetMeta()
from PIL import Image
import os


def save_image(i: Image, dir):
    directory = os.path.dirname(dir)
    if not os.path.exists(directory):
        os.makedirs(directory)
    i.save(dir)


def data_framesize_padder_handler(data_list: list, max_len: int, mode='zero_padding'):
    '''
    Pad or trim list so that data can be converted into a torch tensor object of desired size as model input.
    Currently only support 0 padding, will support advanced padding interporlated values in the future.
    Input: list of data points / multiple [x, y, z] lists
    Output: list of data points / multiple [x, y, z] lists with padded [0, 0, 0] lists such that len(output) matches max_len
    '''
    required_paddings = max_len - len(data_list)
    for i in range(required_paddings):
        data_list.append([0., 0., 0.])

    if not len(data_list) == max_len:
        print("WARNING! It seems like max len isnt enough to utilize the data efficiently", len(data_list))
        data_list = data_list[:max_len]
        print("After correcting..", len(data_list))
        return data_list
    else:
        return data_list


def generate_frames_list(json_list_file, max_len=149):
    '''
    Input json file usually named as BothRadar.txt
    Output processed radar frames as lists (many list of xyz points within 1 frame) in list (list of frames) for radar1 and radar2
    '''
    with open(json_list_file, 'r') as f:
        this_data_radar1_frames_list = []
        this_data_radar2_frames_list = []
        for i, line in enumerate(f):
            try:
                json_dict = json.loads(line)
            except Exception as e:
                print(e)
                print("ERROR check data format! Cannot convert line to JSON", i)
                print("the line trying to read", line)
            d = json_dict['data']
            this_frame_points_list = []
            try:
                for points in d:
                    '''if points['x'] < metadata.MIN_X or points['x'] > metadata.MAX_X:
                        continue
                    if points['y'] < metadata.MIN_Y or points['y'] > metadata.MAX_Y:
                        continue
                    if points['z'] < metadata.MIN_Z or points['z'] > metadata.MAX_Z:
                        continue'''
                    point_list = [points['x'], points['y'], points['z']]
                    this_frame_points_list.append(point_list)
                # Pad width with zeros
                this_frame_points_list = data_framesize_padder_handler(this_frame_points_list, max_len)
            except Exception as e:
                print("Check data format:", i, e)
                print(d)
            if len(this_frame_points_list) == max_len:  # Pad successfully!
                this_data_radar1_frames_list.append(this_frame_points_list) if json_dict[
                                                                                   'name'] == 'radar1' else this_data_radar2_frames_list.append(
                    this_frame_points_list)
            else:
                print(
                    f"Skipping json object of line {i}. Unusual circumstance. json object size {len(this_frame_points_list)} values: {this_frame_points_list}")
                continue
    return this_data_radar1_frames_list, this_data_radar2_frames_list


def generate_frames_list_from_txt(txt_list_file, max_len=149):
    '''
    Input txt file of new data format [Radar1_Frames_List, Radar2_Frames_List] where RadarX_Frames_List = [RadarX_Frame1, RadarX_Frame2... RadarX_Frame180]
    Output processed radar frames as lists (many list of xyz points within 1 frame) in list (list of frames) for radar1 and radar2
    '''
    with open(txt_list_file, 'r') as f:
        this_data_radar1_frames_list = []
        this_data_radar2_frames_list = []
        for i, line in enumerate(f):
            data = eval(line)
            this_data_radar1_frames_list = data[0][-metadata.FRAME_SIZE:]
            this_data_radar2_frames_list = data[1][-metadata.FRAME_SIZE:]

            this_data_radar1_frames_list = [(0.01 * torch.tensor(frame)[:, :-1]).tolist() for frame in
                                            this_data_radar1_frames_list if len(frame) > 0]
            this_data_radar2_frames_list = [(0.01 * torch.tensor(frame)[:, :-1]).tolist() for frame in
                                            this_data_radar2_frames_list if len(frame) > 0]

            try:

                this_data_radar1_frames_list = [data_framesize_padder_handler(this_frame_points_list, max_len) for
                                                this_frame_points_list in this_data_radar1_frames_list]
                this_data_radar2_frames_list = [data_framesize_padder_handler(this_frame_points_list, max_len) for
                                                this_frame_points_list in this_data_radar2_frames_list]
            except Exception as e:
                print("Check data format:", txt_list_file, e)

    return this_data_radar1_frames_list, this_data_radar2_frames_list


def pad_frames_list(radar1list: list, radar2list: list):
    '''
    Input radar 1 list radar 2 list
    Output padded radar 1 converted to tensor object of desired width
    '''
    # Pad width
    correct_radar1list = []
    correct_radar2list = []
    for frame in radar1list:
        f = data_framesize_padder_handler(frame, metadata.FRAME_LENGTH)
        if not len(f) == metadata.FRAME_LENGTH:
            print("ops something wrong with the padder", len(f))
        else:
            correct_radar1list.append(f)
    for frame in radar2list:
        f = data_framesize_padder_handler(frame, metadata.FRAME_LENGTH)
        if not len(f) == metadata.FRAME_LENGTH:
            print("ops something wrong with the padder", len(f))
        else:
            correct_radar2list.append(f)

    # torch_tensor_radar1 = data_frames_padder_handler(radar1list, metadata.FRAME_LENGTH, metadata.FRAME_SIZE)
    # torch_tensor_radar2 = data_frames_padder_handler(radar2list, metadata.FRAME_LENGTH, metadata.FRAME_SIZE)
    return correct_radar1list, correct_radar2list


def data_frames_padder_handler(data_list: list, frames_size, max_len, dtype="torch.float32"):
    '''
    Tensorize the data then, pad the height of the data to make sure the coverage frames matches the required.
    Only support 0 padding at the end of the data.
    This method will work optimally if BothRadar.txt produces 150-180 frames per BothRadar.txt input during site testing.
    May support trimming in future for inputs greater than 200 frames.
    Input: list of frame points
    Output: tensor with correct size
    '''
    # print('error size',len(data_list))
    try:
        d = torch.tensor(data_list, dtype=eval(dtype))
    except Exception as e:
        print(e)
        print("failed to process datalist",d)
        for i, frame in enumerate(d):
            print(f"len for frame {i}, has len {d}")
            #correction
            if not len(frame) == max_len:
                print("weird frame detected need correction", frame)
                d[i] = frame[:max_len]
        d = torch.tensor(data_list, dtype=eval(dtype))

    if len(data_list) < frames_size:
        required_rows = frames_size - len(data_list)
        print(f"padding required rows: {required_rows}")
        if metadata.INPUT_PADDER_CONFIG["Min Frame Handler"] == "PAD ZEROS AT TAIL":
            padding_zeros = torch.zeros((required_rows, max_len, 3), dtype=eval(dtype))
            d = torch.cat((d, padding_zeros))
        elif metadata.INPUT_PADDER_CONFIG["Min Frame Handler"] == "DUPLICATE RANDOM FRAMES":
            indices = torch.randperm(d.shape[0])[
                      :required_rows]  # randomly select rows and duplicate without replacement
            rows_to_add = d[indices]
            d = torch.cat((d, rows_to_add), dim=0)
        elif metadata.INPUT_PADDER_CONFIG["Min Frame Handler"] == "DROP IF INSUFFICIENT FRAMES":
            return torch.tensor([], dtype=eval(dtype)), False

    elif len(data_list) > frames_size:
        d = d[:frames_size]
    return d, True


def check_size_list(class_label: int, torch_tensor_radar1, torch_tensor_radar2, dataid: int):
    # Check if List len is acceptable, if unaccepted return reason, and the folder name
    if torch_tensor_radar1.shape[0] != metadata.FRAME_SIZE or torch_tensor_radar2.shape[0] != metadata.FRAME_SIZE:
        bad_data_discovered = dataid - (
                class_label * 10000 + (0 if class_label == 0 else metadata.EXTRA_DATA[class_label - 1]))
        reason = f"Class label {class_label}. Frame length do not match! Len of Radar1 points: {torch_tensor_radar1.shape[0]} Len of Radar2 points: {torch_tensor_radar2.shape[0]}. Required {metadata.FRAME_SIZE} "
        return True, reason, bad_data_discovered
    else:
        return False, "", None


def tensorize_list(this_data_radar1_frames_list, this_data_radar2_frames_list, frame_size, max_len,
                   dataidentity=[-1, "Inferencing an Unknown"]):
    '''
    Convert list/np.darray object into torch tensor
    input radar1 list of list or numpy object and radar2 list of list or numpy object
    output torch tensor of training/inference shape for model input
    '''
    dataid = dataidentity[0]
    strclass = dataidentity[1]
    torch_tensor_radar1, radar1_pad_success = data_frames_padder_handler(this_data_radar1_frames_list, frame_size,
                                                                         max_len)
    torch_tensor_radar2, radar2_pad_success = data_frames_padder_handler(this_data_radar2_frames_list, frame_size,
                                                                         max_len)

    # Check if List len is acceptable
    '''check_size_list_result = check_size_list(metadata.STR_TO_CLASS_LABELS[strclass], torch_tensor_radar1,
                                             torch_tensor_radar2, dataidentity[0])
    if check_size_list_result[0]:
        return (
        check_size_list_result[2], check_size_list_result[1])  # return bad data id, followed by reason as a tuple
    else:'''
    if radar1_pad_success and radar2_pad_success:
        # print('sizes', torch_tensor_radar1.size(), torch_tensor_radar2.size())
        torch_tensor = torch.cat((torch_tensor_radar1, torch_tensor_radar2), dim=1)
        return torch_tensor
    else:
        return torch.tensor([])


# Preprocessing - normalize the images
def normalize_tensor(torch_tensor: torch.tensor, max_values: list, min_values: list):
    '''
    Min Max normalization with the provided rgb min max
    Input tensor to be normalize, rgb max: max_values rgb min: min_values
    Output: Normalized tensor for model input
    '''
    torch_tensor[:, :, 0] = torch_tensor[:, :, 0].clamp(min=min_values[0], max=max_values[0])
    torch_tensor[:, :, 0] -= min_values[0]
    torch_tensor[:, :, 0] /= max_values[0] - min_values[0]

    torch_tensor[:, :, 1] = torch_tensor[:, :, 1].clamp(min=min_values[1], max=max_values[1])
    torch_tensor[:, :, 1] -= min_values[1]
    torch_tensor[:, :, 1] /= max_values[1] - min_values[1]

    torch_tensor[:, :, 2] = torch_tensor[:, :, 2].clamp(min=min_values[2], max=max_values[2])
    torch_tensor[:, :, 2] -= min_values[2]
    torch_tensor[:, :, 2] /= max_values[2] - min_values[2]
    return torch_tensor


def standardize_tensor(torch_tensor: torch.tensor,
                       rgbmean=(131.36865153 / 255., 97.51712626 / 255., 124.85315563 / 255.),
                       rgbstd=(130.43618906 / 255., 81.93117782 / 255., 128.05481866 / 255.)):
    '''
    Standardize by z-norm.
    Input tensor to be normalize, rgb mean: rgbmean, rgb standard deviations: rgbstd
    Output: Normalized tensor for model input
    '''
    transform = transforms.Compose([transforms.Normalize(rgbmean, rgbstd)])
    torch_tensor = torch.tensor([torch_tensor.tolist()]).permute(0, 3, 1, 2).contiguous()
    return transform(torch_tensor)


def augmentation_handler(t: torch.tensor, whitenoise_scale=0.0):
    '''
    Perform random augmentation. List of augmentation methods:
    1. Adding random White Noise (mean 0 std provided as whitenoise_scale)
    more methods ... in future updates
    Input: Input Training tensor to be augmentated
    Output: Augmentated data
    '''
    # add noise to output array
    mask_red = (t[:, 0, ::] - metadata.RGB_NORM_STAND_MEAN_CONSTANTS[0]).abs() > 0.00001
    mask_green = (t[:, 1, ::] - metadata.RGB_NORM_STAND_MEAN_CONSTANTS[1]).abs() > 0.00001
    mask_blue = (t[:, 2, ::] - metadata.RGB_NORM_STAND_MEAN_CONSTANTS[2]).abs() > 0.00001

    # print("before cat! mask red", mask_red.shape)
    mask = torch.cat((mask_red, mask_green, mask_blue), 0)
    # print("mask shape ",mask.shape)
    # print("tensor shape after apply mask",t[:,mask].shape)
    noise = torch.normal(mean=torch.zeros(t[:, mask].size()),
                         std=whitenoise_scale * torch.ones(t[:, mask].size())).float()
    # print("before add", t)
    t[:, mask] += noise
    # print("after add", t)
    return t
