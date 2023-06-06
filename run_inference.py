# Main file
from model import MyModel
import torch
import InferenceEngineHandler as handler
import argparse

def parse_args():
    parser=argparse.ArgumentParser(description="python code to run inference")
    parser.add_argument("--bothradar_txt", default='./0_1.txt', help='location of both_radar.txt default is ./0_1.txt')
    parser.add_argument("--model_weights", default='./model.pth', help='location of model weight. default is ./model.pth')
    args=parser.parse_args()
    return args


if __name__ == "__main__":
    inputs = parse_args()
    model, loadmodel_time_take = handler.load_inference_model(inputs.model_weights)
    inf_data, inference_preprocess_time_take = handler.inference_preprocess(inputs.bothradar_txt)
    predict, inference_time_take = handler.inference(model, inf_data)
    class_predict = handler.postprocess(predict)
    print(f'Predicted Class: {class_predict}. Predicted Value: {predict}. Model loading Time taken:{loadmodel_time_take}. Inference Preprocess Time Taken:{inference_preprocess_time_take}. Inference Time Taken:{inference_time_take}.')