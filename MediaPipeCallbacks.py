import mediapipe as mp
DetectionResult = mp.tasks.components.containers.DetectionResult
class predictionHandler():
    def __init__(self):
        self.predictions = [DetectionResult(detections=[]) for _ in range(5)]

persondetector_predictionHandler = predictionHandler()
def persondetector_print_result(result: DetectionResult, output_image: mp.Image, timestamp_ms: int):
    # print("output")
    # print('detection result: {}'.format(result))
    persondetector_predictionHandler.predictions = persondetector_predictionHandler.predictions[1:]
    persondetector_predictionHandler.predictions.append(result)

    '''for o in result.detections:
        bbox = o.bounding_box
        print(
            f"Bounding box: origin_x={bbox.origin_x}, origin_y={bbox.origin_y}, width={bbox.width}, height={bbox.height}")
        # Access categories.
        persondetector_predictionHandler.predictions = persondetector_predictionHandler.predictions[1:]
        persondetector_predictionHandler.predictions.append(o.categories)
        for category in persondetector_predictionHandler.predictions[-1]:
            # Extract category information.
            print(
                f"Category: index={category.index}, score={category.score}, display_name={category.display_name}, category_name={category.category_name}")

    print(f"shape of output image {output_image.numpy_view().shape}")
    print(f"ts: {timestamp_ms}")'''