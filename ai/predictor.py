
from fastapi import logger
from ultralytics import YOLO
import cv2
import os
import base64
from constants import AIConstants
from services.db_service import get_category_attribute_data_by_name
from services.helper_log import logger


def predict(sample):
    """
    Perform prediction on the provided image sample using a YOLOv8 model.

    Args:
        sample (dict): A dictionary containing details of the image sample:
            {
                "name": "image_2.jpg",
                "path": "data/temp/image_2.jpg",
                "upload_date": "2025-01-05T10:30:00",
                "is_deleted": false
            }

    Returns:
        tuple: A list of predictions and the base64-encoded annotated image.
    """
    try:
        logger.info(sample)
        # Define the model path
        model_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'data',
            'ai',
            'output',
            'weights',
            'best.pt'
        )

        # Load the YOLOv8 model
        model = YOLO(model_path)

        # Get the path to the test image from the sample
        test_image_path = sample["path"]
        logger.info(test_image_path)

        if not os.path.exists(test_image_path):
            raise FileNotFoundError(
                f"Image file not found at path: {test_image_path}")

        # Perform prediction
        results = model(test_image_path)

        predictions = []
        for result in results:
            boxes = result.boxes
            for box in boxes:
                class_id = int(box.cls)
                class_name = AIConstants.CLASS_NAMES[class_id]
                predictions.append({
                    "class_id": class_id,
                    "class_name": class_name,
                    "attributes": get_category_attribute_data_by_name(class_name),
                    "confidence": float(box.conf),
                    "bbox": box.xyxy.tolist()  # Bounding box coordinates
                })

        # Generate an annotated image
        annotated_image = results[0].plot()

        # Encode the annotated image to base64
        _, img_encoded = cv2.imencode('.jpg', annotated_image)
        img_base64 = base64.b64encode(img_encoded).decode('utf-8')

        return predictions, img_base64

    except FileNotFoundError as e:
        logger.error(f"FileNotFoundError: {e}")
        return {"error": str(e)}, None
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return {"error": "An error occurred during prediction. Check logs for details."}, None
