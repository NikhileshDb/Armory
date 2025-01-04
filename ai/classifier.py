from ultralytics import YOLO
import os

def train():

    model_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'ai', 'yolov8n.pt')

    base_model = YOLO(model_path)

    file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'ai', 'data.yaml')

    base_model.train(
        data=file_path,                    # YAML file with dataset paths
        epochs=120,                        # Number of epochs
        imgsz=640,                         # Image size
        batch=32,                          # Batch size
        name="classification"
    )

    base_model.export(format="onnx")