# Inference Engine handler for Proof of Concept
import time
from model import MyModel
from metadata import DatasetMeta
import datahandler as dh
import torch
import torchvision.transforms as transforms
metadata = DatasetMeta()

def load_inference_model(model_weight_path, device='cpu'):
    '''
    Load a model from the saved state dict .pth/.pt file
    Input: path of .pth file
    Output: torch model for torch inference
    '''
    start = time.time()
    model = MyModel()
    model.load_state_dict(torch.load(model_weight_path, map_location=torch.device('cpu')), )
    model.eval()
    time_take = time.time() - start
    return model, time_take

def inference_preprocess(json_list_file, dtype='torch.float32'):
    '''
    Perform data preprocess for inference/serving data for ML Model. 
    1. Take in a BothRadar.txt, 
    2, Load all json objects. 
    3. Process all frames, do necessary padding/trimming 
    4. Perform normalization and standization
    5. Return attain desired shape of frame_size by max_len.
    convert all frames into one input tensor
    Input: path and filename of BothRadar.txt file containing list of JSON objects
    Output: Torch Tensor data 
    '''
    start = time.time()

    # Essential preprocess of BothRadar.txt file
    this_data_radar1_frames_list, this_data_radar2_frames_list = dh.generate_frames_list(json_list_file, metadata.FRAME_LENGTH)

    # Tensorize the frames list, Pad data tensor height, 2 Methods, pad zeros or interpolate and duplicating neighbouring pixel values and concatenate them
    torch_tensor = dh.tensorize_list(this_data_radar1_frames_list, this_data_radar2_frames_list, metadata.FRAME_SIZE, metadata.FRAME_LENGTH)

    # Data Normalize
    torch_tensor = dh.normalize_tensor(torch_tensor, metadata.RGB_MAX_VALUES, metadata.RGB_MIN_VALUES)

    # Data Standardize
    torch_tensor = dh.standardize_tensor(torch_tensor)

    time_take = time.time() - start
    return torch_tensor, time_take

def live_inference_preprocess(radar1list, radar2list, dtype='torch.float32'):
    '''
    Perform data preprocess for inference/serving data for ML Model.
    1. Take in a radar1list and radar2list
    2. Process all frames, pad width then height then tensorize
    3. Perform normalization and standization
    4. Return attain desired shape of frame_size by max_len.
    convert all frames into one input tensor
    Input: path and filename of BothRadar.txt file containing list of JSON objects
    Output: Torch Tensor data
    '''
    start = time.time()
    # Pad list width
    this_data_radar1_frames_list, this_data_radar2_frames_list = dh.pad_frames_list(radar1list, radar2list)

    # Tensorize the frames list, Pad data tensor height, 2 Methods, pad zeros or interpolate and duplicating neighbouring pixel values and concatenate them
    torch_tensor = dh.tensorize_list(this_data_radar1_frames_list, this_data_radar2_frames_list, metadata.FRAME_SIZE, metadata.FRAME_LENGTH)

    # Data Normalize
    torch_tensor = dh.normalize_tensor(torch_tensor, metadata.RGB_MAX_VALUES, metadata.RGB_MIN_VALUES)

    # Data Standardize
    torch_tensor = dh.standardize_tensor(torch_tensor)

    # Image format
    im = transforms.ToPILImage()(torch_tensor[0])

    time_take = time.time() - start
    return torch_tensor, im, time_take


def inference(model, inference_data, device='cpu'):
    '''
    Perform inference using inference data on model
    Input: Provided trained model
    Output: Predicted values 
    ''' 
    start = time.time()
    with torch.no_grad():
        input = inference_data.to(device)
        outputs = model(input)
        _, predicted = torch.max(outputs.data, 1)
    time_taken = time.time() - start
    return predicted, time_taken

def postprocess(predict_tensor:torch.tensor):
    '''
    Translate predict tensor value into high level info of prediction result
    Input: Tensor produced by model
    Output: 
    '''
    id_to_class_dict = {0:'class0_1000', 1:'class1_1100', 2:'class2_1010', 3:'class3_1110'}
    idx = predict_tensor.item()
    return id_to_class_dict[idx]


