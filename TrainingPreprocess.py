# Training Data Preprocessing 

from torchvision import transforms
import json
import torch
import datahandler as dh
from metadata import DatasetMeta
    

def training_preprocess(json_list_file, dtype='torch.float32'):
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
    metadata = DatasetMeta()
    # Essential preprocess of BothRadar.txt file
    this_data_radar1_frames_list, this_data_radar2_frames_list = dh.generate_frames_list(json_list_file, metadata.FRAME_LENGTH)

    # Tensorize the frames list, Pad data tensor height, 2 Methods, pad zeros or interpolate and duplicating neighbouring pixel values and concatenate them
    torch_tensor = dh.tensorize_list(this_data_radar1_frames_list, this_data_radar2_frames_list, metadata.FRAME_SIZE, metadata.FRAME_LENGTH)

    # Data Normalize
    torch_tensor = dh.normalize_tensor(torch_tensor, metadata.RGB_MIN_VALUES, metadata.RGB_MAX_VALUES)

    # Data Standardize
    torch_tensor = dh.standardize_tensor(torch_tensor, mean_values=metadata.RGB_MEAN_VALUES, std_values=metadata.RGB_STD_VALUES)

    # Return result with augmentation noise (Unlike inference which skip this steps)
    torch_tensor = dh.augmentation_handler(torch_tensor, whitenoise_scale=0.1)

    return torch_tensor
