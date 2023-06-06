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