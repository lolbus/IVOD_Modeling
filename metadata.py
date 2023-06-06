import torch

class DatasetMeta(object):
    """metadata class which store all prefix meta values related to the dataset"""
    def __init__(self):
        self.RGB_MAX_VALUES = (5.39238717, 7.44210686, 2.46697083)
        self.RGB_MIN_VALUES = (-5.53902304, -3.51760874, -2.50915695)
        self.RGB_MEAN_VALUES = (131.36865153/255.,  97.51712626/255., 124.85315563/255.)
        self.RGB_STD_VALUES = (130.43618906/255.,  81.93117782/255., 128.05481866/255.)
        self.FRAME_LENGTH = 149
        self.FRAME_SIZE = 200
        self.STR_TO_ONEHOT_LABELS = {"PassengerNo_1 (D)": str([1, 0, 0]),
                                     "PassengerNo_2 (D+FP)": str([1, 1, 0]),
                                     "PassengerNo_2 (D+LB)": str([1, 0, 1]),
                                     "PassengerNo_3 (D+FP+LB)": str([1, 1, 1])
                                     }
        self.STR_TO_CLASS_LABELS = {"PassengerNo_1 (D)": 0,
                                     "PassengerNo_2 (D+FP)": 1,
                                     "PassengerNo_2 (D+LB)": 2,
                                     "PassengerNo_3 (D+FP+LB)": 3,
                                     "Inferencing an Unknown": -1
                                     }
        self.ONEHOT_TO_STR_LABELS = {str([1, 0, 0]): "PassengerNo_1 (D)",
                                     str([1, 1, 0]): "PassengerNo_2 (D+FP)",
                                     str([1, 0, 1]): "PassengerNo_2 (D+LB)",
                                     str([1, 1, 1]): "PassengerNo_3 (D+FP+LB)"
                                     }
        self.STR_LABELS_LIST = list(self.STR_TO_ONEHOT_LABELS.keys())
        self.EXTRA_DATA = [34, 5, 10, 0]
        self.RGB_NORM_STAND_MEAN_CONSTANTS = [((0. - self.RGB_MIN_VALUES[0])/(self.RGB_MAX_VALUES[0]-self.RGB_MIN_VALUES[0]) - self.RGB_MEAN_VALUES[0])/self.RGB_STD_VALUES[0],
         ((0. - self.RGB_MIN_VALUES[1])/(self.RGB_MAX_VALUES[1]-self.RGB_MIN_VALUES[1]) - self.RGB_MEAN_VALUES[1])/self.RGB_STD_VALUES[1],
          ((0. - self.RGB_MIN_VALUES[2])/(self.RGB_MAX_VALUES[2]-self.RGB_MIN_VALUES[2]) - self.RGB_MEAN_VALUES[2])/self.RGB_STD_VALUES[2]
         ]
