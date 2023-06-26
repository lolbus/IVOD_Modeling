import torch

class DatasetMeta(object):
    """metadata class which store all prefix meta values related to the dataset"""
    def __init__(self):
        # Data collection configs:
        # self.HOME_DIR = "C:/debug/data/"
        self.HOME_DIR = "C:/Users/WayneGuangWayTENGSof/Desktop/22June_DataCollection/"
        # self.SAVE_DATA_DIR = self.HOME_DIR + "PassengerNo_3 (D+FP+LB)(C)"
        self.SAVE_DATA_DIR = self.HOME_DIR + "PassengerNo_0 (Empty)2"


        # Training Preprocess configs:
        self.data_class_distribution = [0, 3333, 3333, 3334,
                                        0, 0, 10000]  # How much samples to draw for training data preprocessing
        self.augmentation_rate = [2, 0, 0, 0, 0, 0] # How much to augment replicate each instance drawn
        # DROP UNDERSIZED FRAME CANNOT BE USED DURING INFERENCE
        # "Available: DUPLICATE RANDOM FRAMES / DROP IF INSUFFICIENT FRAMES / PAD ZEROS AT TAIL"
        self.INPUT_PADDER_CONFIG = {"Min Frame Handler": "PAD ZEROS AT TAIL"}

        # Inference configs:
        self.modelDir = "C:/Users/WayneGuangWayTENGSof/Desktop/IVOD_Models/"  # Directory of saved weights checkpoint

        # Static variables ( Change only if you have done the homework )
        self.RGB_MAX_VALUES = (5.39238717, 7.44210686, 2.46697083)
        self.RGB_MIN_VALUES = (-5.53902304, -3.51760874, -2.50915695)
        self.RGB_MEAN_VALUES = (131.36865153/255.,  97.51712626/255., 124.85315563/255.)
        self.RGB_STD_VALUES = (130.43618906/255.,  81.93117782/255., 128.05481866/255.)
        self.FRAME_LENGTH = 149
        self.FRAME_SIZE = 180
        self.STR_TO_ONEHOT_LABELS = {"PassengerNo_0 (Empty)": str([0, 0, 0]),
                                     "PassengerNo_1 (D)": str([1, 0, 0]),
                                     "PassengerNo_2 (D+FP)": str([1, 1, 0]),
                                     "PassengerNo_2 (D+LB)": str([1, 0, 1]),
                                     "PassengerNo_3 (D+FP+LB)": str([1, 1, 1]),
                                     "PassengerNo_0 (Empty)2": str([0, 0, 0]),
                                     "PassengerNo_3 (D+FP+LB)(C)": str([1, 1, 1])
                                     }
        self.STR_TO_CLASS_LABELS = {"PassengerNo_0 (Empty)": 0,
                                    "PassengerNo_1 (D)": 1,
                                    "PassengerNo_2 (D+FP)": 2,
                                    "PassengerNo_2 (D+LB)": 3,
                                    "PassengerNo_3 (D+FP+LB)": 4,
                                    "PassengerNo_0 (Empty)2": 0,
                                    "PassengerNo_3 (D+FP+LB)(C)": 4,
                                    "Inferencing an Unknown": -1
                                    }
        self.ONEHOT_TO_STR_LABELS = {str([0, 0, 0]): "PassengerNo_0 (Empty)",
                                     str([0, 0, 0]): "PassengerNo_0 (Empty)2",
                                     str([1, 0, 0]): "PassengerNo_1 (D)",
                                     str([1, 1, 0]): "PassengerNo_2 (D+FP)",
                                     str([1, 0, 1]): "PassengerNo_2 (D+LB)",
                                     str([1, 1, 1]): "PassengerNo_3 (D+FP+LB)",
                                     str([1, 1, 1]): "PassengerNo_3 (D+FP+LB)(C)"
                                     }
        self.STR_LABELS_LIST = list(self.STR_TO_ONEHOT_LABELS.keys())
        self.EXTRA_DATA = [0, 34, 5, 10, 0, 0]
        self.RGB_NORM_STAND_MEAN_CONSTANTS = [((0. - self.RGB_MIN_VALUES[0])/(self.RGB_MAX_VALUES[0]-self.RGB_MIN_VALUES[0]) - self.RGB_MEAN_VALUES[0])/self.RGB_STD_VALUES[0],
         ((0. - self.RGB_MIN_VALUES[1])/(self.RGB_MAX_VALUES[1]-self.RGB_MIN_VALUES[1]) - self.RGB_MEAN_VALUES[1])/self.RGB_STD_VALUES[1],
          ((0. - self.RGB_MIN_VALUES[2])/(self.RGB_MAX_VALUES[2]-self.RGB_MIN_VALUES[2]) - self.RGB_MEAN_VALUES[2])/self.RGB_STD_VALUES[2]
         ]
        self.MIN_X = -2.0
        self.MAX_X = 2.0
        self.MIN_Y = 1.0
        self.MAX_Y = 2.65
        self.MIN_Z = -0.5
        self.MAX_Z = 0.5


