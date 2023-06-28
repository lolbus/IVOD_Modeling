import cv2
import os
import time
import numpy as np
from metadata import DatasetMeta
import mediapipe as mp
from model import modelloader
from threading import Thread

metadata = DatasetMeta()
model = modelloader("CCTV_MP_PERSON_PREDICTOR")
# Define the path to the video stream (replace with your actual RTSP URL)
rtsp_url = 'rtsp://root:pass@192.168.70.2/axis-media/media.amp?videocodec=h264&resolution=640x360'

# Define the directory where to save the images
output_dir = metadata.SAVE_VID_DATA_DIR
os.makedirs(output_dir, exist_ok=True)

class statusHandler():
    def __init__(self):
        self.frame = None
        self.mp_image = None
        self.ret = False
        self.save = False
        self.processed_frame = None
        self.FirstLoop = True
statusHandler = statusHandler()

MARGIN = 10  # pixels
ROW_SIZE = 10  # pixels
FONT_SIZE = 1
FONT_THICKNESS = 1
TEXT_COLOR = (255, 0, 0)  # red


def visualize(
    image,
    detection_result
) -> np.ndarray:
  """Draws bounding boxes on the input image and return it.
  Args:
    image: The input RGB image.
    detection_result: The list of all "Detection" entities to be visualize.
  Returns:
    Image with bounding boxes.
  """
  for detection in detection_result.detections:
    # Draw bounding_box
    bbox = detection.bounding_box
    start_point = bbox.origin_x, bbox.origin_y
    end_point = bbox.origin_x + bbox.width, bbox.origin_y + bbox.height
    cv2.rectangle(image, start_point, end_point, TEXT_COLOR, 3)

    # Draw label and score
    category = detection.categories[0]
    category_name = category.category_name
    probability = round(category.score, 2)
    result_text = category_name + ' (' + str(probability) + ')'
    text_location = (MARGIN + bbox.origin_x,
                     MARGIN + ROW_SIZE + bbox.origin_y)
    cv2.putText(image, result_text, text_location, cv2.FONT_HERSHEY_PLAIN,
                FONT_SIZE, TEXT_COLOR, FONT_THICKNESS)

  return image

def count_people(pax_predictor_output):
    count = 0
    for o in pax_predictor_output.detections:
        category_name = o.categories[0].category_name
        if category_name == 'person':
            count += 1
    return count
def infer_and_save():
    counter = 0
    while True:
        if statusHandler.ret:
            counter += 1
            output = model.persondetector_evaluate_frame(statusHandler.mp_image, counter)
            print(f"Output: {output}")
            pax_count = count_people(output[-1])
            print("total pax", pax_count)
            statusHandler.processed_frame = visualize(statusHandler.frame, output[-1])
            # print("T", visualize_output)
            statusHandler.ret = False
            if statusHandler.FirstLoop:
                statusHandler.FirstLoop = False
            time.sleep(0.5)
        if statusHandler.save:
            # Define the filename of the image
            img_filename = os.path.join(output_dir, f'image_{str(counter).zfill(5)}.png')
            cv2.imwrite(img_filename, statusHandler.frame)



def stream():
    # Use OpenCV to read the video stream
    cap = cv2.VideoCapture(rtsp_url)

    # Create a named window for the display
    cv2.namedWindow("CCTV Stream", cv2.WINDOW_NORMAL)
    try:
        while True:
            start_time = time.time()

            # Capture two frames per second

            ret, frame = cap.read()
            statusHandler.ret = ret
            statusHandler.frame = frame
            statusHandler.mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)

            # Display the frame
            if not statusHandler.FirstLoop:
                cv2.imshow("CCTV Stream", statusHandler.processed_frame)

            # Break the loop if 'q' is pressed
            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        pass
    finally:
        # Release the video capture object and close the display window
        cap.release()
        cv2.destroyAllWindows()

    #print(f'Extracted {counter} frames from the video and saved them into {output_dir}.')

streaming_thread = Thread(target=stream)
streaming_thread.start()


streaming_thread = Thread(target=infer_and_save)
streaming_thread.start()

