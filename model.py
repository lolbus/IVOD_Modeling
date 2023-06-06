# Save as model.py

import torch.nn as nn
import torchvision.models as models
import torch.nn.functional as F

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
