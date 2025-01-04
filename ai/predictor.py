from ultralytics import YOLO
import cv2
import os
import base64
from constants import AIConstants
from services.db_service import get_category_attribute_data_by_name

def predict():

    model_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'ai', 'output', 'weights','best.pt')

    # Load the YOLOv8 model
    model = YOLO(model_path) 

    # Path to the test image
    test_image_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'ai', 'input', 'test', 'images', 'bisleri-mineral-water-bottle.jpg')

    # Perform prediction
    results = model(test_image_path)
    
    predictions = []
    for result in results:
        
        boxes = result.boxes 
        for box in boxes:
            classId = int(box.cls)
            className = AIConstants.CLASS_NAMES[classId]
            predictions.append({
                "class_id": classId, 
                "class_name": className, 
                "attributes" : get_category_attribute_data_by_name(className), 
                "confidence": float(box.conf),  
                "bbox": box.xyxy.tolist()  
            })
        
        annotated_image = results[0].plot()  # I dont understand this but it seems like there can be only 1 annotated image

        _, img_encoded = cv2.imencode('.jpg', annotated_image)
        img_base64 = base64.b64encode(img_encoded).decode('utf-8')

        return predictions, img_base64  