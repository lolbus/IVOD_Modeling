# Save as model.py

import torch.nn as nn
import torch
import torchvision.models as models
import torch.nn.functional as F
from metadata import DatasetMeta

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

class modelloader(object):
    def __init__(self, modelname="IVOD V1"):
        self.metadata = DatasetMeta()
        device = torch.device("cpu")
        models_dir = self.metadata.modelDir
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
                torch.load(models_dir + '/EC_Predictor/260623-V9-EC180_best_model.pt',
                           map_location=device))
            self.ECPredictor.eval()
            self.metadata.FRAME_SIZE = 180


        self.fp_positive_thresold = 0.90
        self.lb_positive_thresold = 0.99
        self.ec_positive_thresold = 0.5

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


