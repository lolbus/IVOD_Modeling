# Save as model.py

import torch.nn as nn
import torch
import torchvision.models as models
import torch.nn.functional as F
from metadata import DatasetMeta
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import MediaPipeCallbacks as mpc
BaseOptions = mp.tasks.BaseOptions
ObjectDetector = mp.tasks.vision.ObjectDetector
ObjectDetectorOptions = mp.tasks.vision.ObjectDetectorOptions
VisionRunningMode = mp.tasks.vision.RunningMode

# Define the model architecture
class MyModel(nn.Module):
    def __init__(self):
        super(MyModel, self).__init__()
        self.conv1 = nn.Conv2d(3, 6, 3)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(6, 9, (2,3))
        self.conv3 = nn.Conv2d(9, 12, 2)

        self.fc1 = nn.Linear(12 * 24 * 36, 4)
        #self.fc2 = nn.Linear(240, 124)
        #self.fc3 = nn.Linear(124, 4)

        self.dropout = nn.Dropout(0.2) # 20% dropout

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x))) # output size is 6c by 198/2=99 by  296/2=148
        x = self.pool(F.relu(self.conv2(x))) # output size is 9c by 98/2=49 by 146/2=73
        x = self.dropout(x)
        x = self.pool(F.relu(self.conv3(x))) # output size is 12c by 48/2=24 by 72/2=36
        x = x.view(-1, 12 * 24 * 36)
        x = self.fc1(x)
        #x = F.relu(self.fc1(x))
        #x = self.dropout(x)
        #x = F.relu(self.fc2(x))
        #x = self.dropout(x)
        #x = self.fc3(x)
        return x

def IVODResnet34():
    # Define ResNet model
    import copy

    import torch
    from torch import nn
    from torchvision import models
    device = torch.device("cpu")

    modelA = models.resnet34()
    modelA.avgpool = nn.AdaptiveAvgPool2d((1, 1))

    # Add a dropout layer
    modelA.dropout = nn.Dropout(0.)

    num_features = modelA.fc.in_features
    modelA.fc = nn.Linear(num_features, 1)

    # Define Loss Function and Optimizer
    criterion = nn.BCEWithLogitsLoss()
    # optimizer = torch.optim.Adam(modelA.parameters(), lr=0.001)
    optimizer = None

    # Modify the forward method to include dropout
    def new_forward(self, x):
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.maxpool(x)

        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)

        x = self.avgpool(x)
        x = torch.flatten(x, 1)
        x = self.dropout(x)
        x = self.fc(x)

        return x

    # Replace the original forward method with your modified one
    modelA.forward = new_forward.__get__(modelA, models.ResNet)
    modelA = modelA.to(device)
    return modelA

class CCTV_modeler(object):
    def __init__(self, detector):
        self.detector = detector
        self.counter = 0

    def persondetector_evaluate_frame(self, input):
        self.counter += 1
        self.detector.detect_async(input, self.counter)
        result = mpc.persondetector_predictionHandler.predictions
        return result

class modelloader(object):
    def __init__(self, modelname="IVOD V1"):
        self.metadata = DatasetMeta()
        self.metadata.INPUT_PADDER_CONFIG["Min Frame Handler"] = "PAD ZEROS AT TAIL"
        device = torch.device("cpu")
        models_dir = self.metadata.modelDir
        self.modelname = modelname
        if modelname == "IVOD V1":
            self.FPPredictor = IVODResnet34()
            self.LBPredictor = IVODResnet34()
            self.FPPredictor.load_state_dict(
                torch.load(models_dir + '/FP_Predictor/050623-FP-0992-10SEC-200MAXFRAME.pt', map_location=device))
            self.LBPredictor.load_state_dict(
                torch.load(models_dir + '/LB_Predictor/050623-LB-0997-10SEC-200MAXFRAME.pt', map_location=device))
            self.metadata.FRAME_SIZE = 182
            self.FPPredictor.eval()
            self.LBPredictor.eval()
        elif modelname == "IVOD V3":
            self.FPPredictor = IVODResnet34()
            self.LBPredictor = IVODResnet34()
            self.FPPredictor.load_state_dict(
                torch.load(models_dir + '/FP_Predictor/120623-FP-09985-FRAMESTEP-180MAXFRAME-V3_model_weight.pt', map_location=device))
            self.LBPredictor.load_state_dict(
                torch.load(models_dir + '/LB_Predictor/120623-LB-09995-FRAMESTEP-DUPLICATE-180MF_best_model.pt', map_location=device))
            self.metadata.FRAME_SIZE = 180
            self.FPPredictor.eval()
            self.LBPredictor.eval()
        elif modelname == "IVOD V4":
            self.FPPredictor = IVODResnet34()
            self.LBPredictor = IVODResnet34()
            self.FPPredictor.load_state_dict(
                torch.load(models_dir + '/FP_Predictor/120623-FP-09989-V4-FRAMESTEP-DROPFRAME-FP180_best_model.pt',
                           map_location=device))
            self.LBPredictor.load_state_dict(
                torch.load(models_dir + '/LB_Predictor/130623-LB-1000-A100-FRAMESTEP-DROPFRAMES-V4B-LP180_best_model.pt',
                           map_location=device))
            self.metadata.FRAME_SIZE = 180
            self.FPPredictor.eval()
            self.LBPredictor.eval()
        elif modelname == "IVOD V5":
            self.FPPredictor = IVODResnet34()
            self.LBPredictor = IVODResnet34()
            self.FPPredictor.load_state_dict(
                torch.load(models_dir + '/FP_Predictor/V5-FP-1000-FRAMESIZE-DROPPADDING-180_best_model.pt',
                           map_location=device))
            self.LBPredictor.load_state_dict(
                torch.load(models_dir + '/LB_Predictor/130623-LB-1000-A100-FRAMESTEP-DROPFRAMES-V4B-LP180_best_model.pt',
                           map_location=device))
            self.metadata.FRAME_SIZE = 180
            self.FPPredictor.eval()
            self.LBPredictor.eval()
        elif modelname == "IVOD V7":
            self.FPPredictor = IVODResnet34()
            self.LBPredictor = IVODResnet34()
            self.FPPredictor.load_state_dict(
                torch.load(models_dir + '/FP_Predictor/V7-FP-09942-40k-FRAMESIZE-DROPPADDING-180_best_model.pt',
                           map_location=device))
            self.LBPredictor.load_state_dict(
                torch.load(models_dir + '/LB_Predictor/150623-1000-V7-LB180_best_model.pt',
                           map_location=device))
            self.metadata.FRAME_SIZE = 180
            self.FPPredictor.eval()
            self.LBPredictor.eval()
        elif modelname == "IVOD DATA COLLECTOR":
            self.ECPredictor = IVODResnet34()
            self.ECPredictor.load_state_dict(
                torch.load(models_dir + '/EC_Predictor/260623-V9E-EC180_best_model.pt',
                           map_location=device))
            self.TestPredictor = IVODResnet34()
            self.TestPredictor.load_state_dict(
                torch.load(models_dir + '/Test_Predictor/270623-D+FP+LB_Predictor180_best_model.pt',
                           map_location=device))
            self.ECPredictor.eval()
            self.TestPredictor.eval()
            self.metadata.FRAME_SIZE = 180
        elif modelname == "CCTV_MP_PERSON_PREDICTOR":
            options = vision.ObjectDetectorOptions(
                base_options=BaseOptions(model_asset_path=models_dir + '/CCTVPredictor/efficientdet.tflite'),
                running_mode=VisionRunningMode.LIVE_STREAM,
                max_results=1,
                category_allowlist=["person"],
                result_callback=mpc.persondetector_print_result, score_threshold=0.2)
            self.detector = vision.ObjectDetector.create_from_options(options)
            self.CCTVHandler = CCTV_modeler(self.detector)
            self.modeler = self.CCTVHandler.persondetector_evaluate_frame
            self.modeler_positive_thresold = 0
        elif modelname == "ZERO_PAX_PREDICTOR":
            self.modeler = IVODResnet34()
            self.modeler.load_state_dict(
                torch.load(models_dir + '/EC_Predictor/260623-V9E-EC180_best_model.pt',
                           map_location=device))
            self.modeler.eval()
            self.metadata.FRAME_SIZE = 180
            self.modeler_positive_thresold = 1.05
        elif modelname == "D+LB vs D Predictor (V14)":
            self.modeler = IVODResnet34()
            self.modeler.load_state_dict(
                torch.load(models_dir + '/D+LB_vs_D_Predictor/290623_D+LBvsD_Predictor180_best_model_v14.pt',
                           map_location=device))
            self.modeler_positive_thresold = 0.2
            self.metadata.FRAME_SIZE = 180
            self.modeler.eval()
        elif modelname == "D+LB vs D Predictor (V22)":
            self.modeler = IVODResnet34()
            self.modeler.load_state_dict(
                torch.load(models_dir + '/D+LB_vs_D_Predictor/100723_D+LBvsD_Predictor180_best_model_v22.pt',
                           map_location=device))
            self.modeler_positive_thresold = 0.6
            self.metadata.FRAME_SIZE = 180
            self.modeler.eval()
        elif modelname == "D+FP+LB vs D+FP Predictor (V16)":
            self.modeler = IVODResnet34()
            self.modeler.load_state_dict(
                torch.load(models_dir + '/D+FP_vs_D+FP+LB_Predictor/300623_D+FPvsD+FP+LB_Predictor180_best_model.pt',
                           map_location=device))
            self.modeler_positive_thresold = 0.98
            self.metadata.FRAME_SIZE = 180
            self.modeler.eval()
        elif modelname == "D+FP+LB vs D+FP Predictor (V24)":
            self.modeler = IVODResnet34()
            self.modeler.load_state_dict(
                torch.load(models_dir + '/D+FP_vs_D+FP+LB_Predictor/120723_D+FP+LBvsD+FP_Predictor180_best_model_v24.pt',
                           map_location=device))
            self.modeler_positive_thresold = 0.5
            self.metadata.FRAME_SIZE = 180
            self.modeler.eval()
        elif modelname == "D+FP Predictor (V18)":
            self.modeler = IVODResnet34()
            self.modeler.load_state_dict(
                torch.load(models_dir + '/D+FP_Predictor/300623_D+FP_Predictor180_best_model.pt',
                           map_location=device))
            self.modeler_positive_thresold=0.2
            self.metadata.FRAME_SIZE = 180
            self.modeler.eval()
        elif modelname == "D+FP Predictor (V20)":
            self.modeler = IVODResnet34()
            self.modeler.load_state_dict(
                torch.load(models_dir + '/D+FP_Predictor/120723_D+FP_Predictor180_best_model_v20.pt',
                           map_location=device))
            self.modeler_positive_thresold = 0.5
            self.metadata.FRAME_SIZE = 180
            self.modeler.eval()
        elif modelname == "D+FP Predictor (V34)":
            self.modeler = IVODResnet34()
            self.modeler.load_state_dict(
                torch.load(models_dir + '/D+FP_Predictor/100823-D+FP_Predictor180_best_model_v34.pt',
                           map_location=device))
            self.modeler_positive_thresold = 0.5
            self.metadata.FRAME_SIZE = 180
            self.modeler.eval()
        elif modelname == "ZERO_PAX_PREDICTOR (V35)":
            self.modeler = IVODResnet34()
            self.modeler.load_state_dict(
                torch.load(models_dir + '/EC_Predictor/100823-EC180_best_model_V35.pt',
                           map_location=device))
            self.modeler.eval()
            self.metadata.FRAME_SIZE = 180
            self.modeler_positive_thresold = 0.5
        elif modelname == "D+LB vs D Predictor (V32)":
            self.modeler = IVODResnet34()
            self.modeler.load_state_dict(
                torch.load(models_dir + '/D+LB_vs_D_Predictor/100823-D+LBvsD_Predictor180_best_model_V32.pt',
                           map_location=device))
            self.modeler_positive_thresold = 0.5
            self.metadata.FRAME_SIZE = 180
            self.modeler.eval()
        self.fp_positive_thresold = 0.90
        self.lb_positive_thresold = 0.99
        self.ec_positive_thresold = 0.5

    def persondetector_evaluate_frame(self, input, counter):
        self.detector.detect_async(input, counter)
        result = mpc.persondetector_predictionHandler.predictions
        return result

    def calculate_output(self, input):
        with torch.no_grad():
            FP_Score = torch.sigmoid(self.FPPredictor(input))
            LB_Score = torch.sigmoid(self.LBPredictor(input))
            FP_Predict = (FP_Score > self.fp_positive_thresold).long().item()
            LB_Predict = (LB_Score > self.lb_positive_thresold).long().item()
            passengerNo = FP_Predict + LB_Predict
            return FP_Predict, LB_Predict, FP_Score, LB_Score, passengerNo

    def calculate_ec_output(self, input):
        with torch.no_grad():
            EC_Score = torch.sigmoid(self.ECPredictor(input))
            EC_Predict = (EC_Score > self.ec_positive_thresold).long().item()
            passengerNo = 0 if EC_Predict == 1 else -1
            return EC_Predict, EC_Score, passengerNo

    def calculate_test_output(self, input):
        with torch.no_grad():
            Score = torch.sigmoid(self.TestPredictor(input))
            Predict = (Score > 0.5).long().item()
            passengerNo = 3 if Predict == 1 else -1
            return Predict, Score, passengerNo

    def calculate_modeler_binary_output(self, input):
        modeler = self.modeler
        with torch.no_grad():
            score = torch.sigmoid(modeler(input))
            #print("score of predict", score)
            return 1. if score > self.modeler_positive_thresold else 0., score


