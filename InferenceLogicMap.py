MVP_Model3_Logic_Map = {
    "0 Pax Predictor": [("CCTV Person Counter", False), (0, True)],
    "CCTV Person Counter": [("D+LB vs D Predictor", False), ("D+FP+LB vs D+FP Predictor", False)],
    "D+LB vs D Predictor": [(1, True), (2, True)],
    "D+FP+LB vs D+FP Predictor": [(2, True), (3, True)]
}

MVP_Model4_Logic_Map = {
    "0 Pax Predictor": [("D+FP Predictor", False), (0, True)],
    "D+FP Predictor": [("D+LB vs D Predictor", False), ("D+FP+LB vs D+FP Predictor", False)],
    "D+LB vs D Predictor": [(1, True), (2, True)],
    "D+FP+LB vs D+FP Predictor": [(2, True), (3, True)]}

MVP_Model5_Logic_Map = {
    "0 Pax Predictor": [("D+FP Predictor", False), (0, True)],
    "D+FP Predictor": [("D+LB vs D Predictor", False), ("CCTV Person Counter", False)],
    "D+LB vs D Predictor": [(1, True), (2, True)],
    "CCTV Person Counter": [(2, True), (3, True)]}

# Keys: All nodes, Values: model corresponding to the node name
ModelMapper = {
    "0 Pax Predictor": "ZERO_PAX_PREDICTOR",
    "CCTV Person Counter": "CCTV_MP_PERSON_PREDICTOR",
    "D+LB vs D Predictor": "D+LB vs D Predictor (V14)",
    "D+FP+LB vs D+FP Predictor": "D+FP+LB vs D+FP Predictor (V16)",
    "D+FP Predictor": "D+FP Predictor (V18)"
}
