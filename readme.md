# List of important files in the IVOD Project   
1. Toppan_LF_Project_closure_report_Oct_2022_final.pdf - Report prepared by Ngee Ann Poly Lecturers on the uRad's hardware configuration and setup, as well as feasibility test result done by the school staff
2. Radar Environmet Setup Documentation (Deprecated from 28Aug23).pdf - The old environment setup guide used from Jan 2023 to Aug 23. Has serious non static issues. Deprecated from Aug23 as a perm structure was built by Uncle Quek  
3. record_and_save.py - (MLOps Related) The main code that perform live inference and data collection at the same time using the MLOps systems Wayne developed when he onboards Toppan.  
4. InferenceLogicMap.py - (MLOps Related) The dictionary that maps the logic flows of the inference engine. The inference engine uses a sequence of models to do predictions  
5. run_live_inference.py - (MLOps Related) Stand alone inference engine without ablity to do data collection, updating stops since Aug 23.  
6. metadata.py - (MLOps Related) Contains all the config information required to process data collection or to read model for inference engine deployment
7. June23_InternAshley_Handover/ - Contains all the files that are related to Ashley's contribution. Here are information of each of the files:  
![image](https://github.com/lolbus/IVOD_Modeling/assets/1837762/cd2608d1-4074-451e-a796-f567a9f7f80f)
8. notebooks/Data_Preprocessing_newPipeline.ipynb - (MLOps Related) Data preprocessing source code. Convert point cloud data into relevant heatmaps  
9. notebooks/IVOD_Deeplearning_Trainer.ipynb - (MLOps Related) The first version of trainer, developed in June 23,  by Wayne  
10. notebooks/IVOD_Deeplearning_Trainer_V2.ipynb - (MLOps Related) Second version of model trained, developed in Early July 23  
11. notebooks/Data_Deeplearning_Trainer_CompiledTensor_V3.ipynb - (MLOps Related) The third version of model trained, the final non-static setup uses this trainer. Developed in mid July 23  
12. IVOD_SplitDBSCAN/IVOD_SplitDBSCAN/bin/Debug/net7.0/IVOD_SplitDBSCAN.exe - (MLOps Related) This is an app essential to run the DBScan live inference done by Nicholas during his departure. run record_and_save.py followed by this executable file to visualize the prediction and raw plot points on a matplotlib diagram.  
