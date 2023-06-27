import cv2
import os
import time
from metadata import DatasetMeta
metadata = DatasetMeta()
# Define the path to the video stream (replace with your actual RTSP URL)
rtsp_url = 'rtsp://root:pass@192.168.31.2/axis-media/media.amp?videocodec=h264&resolution=640x360'

# Define the directory where to save the images
output_dir = metadata.SAVE_VID_DATA_DIR
os.makedirs(output_dir, exist_ok=True)

# Use OpenCV to read the video stream
cap = cv2.VideoCapture(rtsp_url)

# Define a counter for the image filenames
counter = 0


try:
    while True:
        start_time = time.time()

        # Capture two frames per second
        for _ in range(2):
            ret, frame = cap.read()
            if ret:
                # Define the filename of the image
                img_filename = os.path.join(output_dir, f'image_{str(counter).zfill(5)}.png')

                # Save the image
                cv2.imwrite(img_filename, frame)
                counter += 1

        # Calculate remaining time to sleep to maintain 2 frames per second
        elapsed_time = time.time() - start_time
        if elapsed_time < 1:
            time.sleep(1 - elapsed_time)
except KeyboardInterrupt:
    # Release the video capture object
    cap.release()

print(f'Extracted {counter} frames from the video and saved them into {output_dir}.')