import asyncio
import logging
import threading
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks, WebSocketDisconnect, WebSocket
from contextlib import asynccontextmanager
from fastapi.responses import FileResponse, JSONResponse
from services.db_service import (
    create_table,
    get_all_predictions,
    get_all_samples,
    get_sample,
    insert_sample,
    get_all_assets,
    get_all_categories,
    insert_category,
    insert_asset,
    get_category_attributes,
    insert_category_attributes
)
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import os
import shutil
from datetime import datetime
from dtos.category_dto import add_category
from dtos.asset_dto import add_asset
# from services.bt_ble_service import BluetoothServer
from ai.predictor import predict
from ai.classifier import train
# from services.web_socket_service import ConnectionManager
from services.serialport_service import SerialPortManager


class SocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        # logger.info(f"New client connected. Total clients: {
        #             len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        # logger.info(f"Client disconnected. Total clients: {
        #             len(self.active_connections)}")

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error sending message to client: {e}")
                self.active_connections.remove(connection)

    async def broadcast_image(self, image_data: bytes):
        """
        Broadcasts the image data (binary) to all connected WebSocket clients.
        """
        for connection in self.active_connections:
            logger.debug("******************BROADCAST IMAGE******************")
            try:
                await connection.send_bytes(image_data)
            except Exception as e:
                logger.error(f"Error sending image to client: {e}")
                self.active_connections.remove(connection)


create_table()
# seed ?


socket_service = SocketManager()
serial_manager = SerialPortManager(
    port="COM3", socket_manager=socket_service, baudrate=9600, output_dir="received_images")


app = FastAPI()
logger = logging.getLogger(__name__)
logging.basicConfig(filename='armory.log',
                    encoding='utf-8', level=logging.DEBUG)
# bluetooth_server = BluetoothServer()

# a mobile app should not need CORS setup
origins = [
    "http://localhost:3000",
]
# Required to communicate with the ReactApp
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    # Establish the serial connection
    serial_manager.connect()

    # Start reading images in a separate thread
    threading.Thread(target=lambda: asyncio.run(
        serial_manager.run()), daemon=True).start()
    logging.info("Serial communication thread started.")


# FastAPI shutdown event
@app.on_event("shutdown")
def shutdown_event():
    # Gracefully close the serial connection
    serial_manager.disconnect()


@app.get("/samples")
def get_samples():
    data = get_all_samples()

    return data


@app.post("/samples/upload")
async def upload(files: List[UploadFile] = File(...)):
    for file in files:
        try:
            tempFolder = 'data/temp/'
            if not os.path.exists(tempFolder):
                os.makedirs(tempFolder)

            tempPath = tempFolder + file.filename
            with open(tempPath, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            insert_sample(file.filename, tempFolder +
                          file.filename, datetime.now(), False)

        except Exception as e:
            raise HTTPException(status_code=500, detail='Something went wrong')
        finally:
            await file.close()  # Use await for closing FastAPI UploadFile

    return {"message": f"Successfully uploaded samples {[file.filename for file in files]}"}


@app.post("/samples/{sampleId}/analyze")
async def analyze_sample(sampleId: int, backgroundTasks: BackgroundTasks):

    return {"message": "Accepted", "sampleId": sampleId}


@app.get("/assets")
def get_assets():
    return get_all_assets()


@app.post("/assets")
async def add_asset(addAssetObj: add_asset):

    added_date = datetime.now().timestamp()
    insert_asset(addAssetObj.name, addAssetObj.description,
                 added_date, addAssetObj.category_id, addAssetObj.is_active)

    return {"message": "Successfully added asset"}


@app.get("/categories")
def get_categories():
    return get_all_categories()


@app.post("/categories")
async def add_category(addCategoryObj: add_category):

    added_date = datetime.now().timestamp()
    insert_category(addCategoryObj.name, addCategoryObj.description,
                    added_date, addCategoryObj.is_active)

    return {"message": "Successfully added category"}


@app.get("/categories/{categoryId}/attributes")
def get_attributes(categoryId: int):
    return get_category_attributes(categoryId)


@app.post("/categories/{categoryId}/attributes")
async def add_attributes(categoryId: int, addAttributesObj: dict):

    insert_category_attributes(categoryId, addAttributesObj)

    return {"message": "Successfully added category attributes"}


@app.post("/ai/train")
async def train_model():
    train()


@app.post("/ai/predict")
async def predict_image():
    predictions, img_base64 = predict()

    return JSONResponse(content={
        "predictions": predictions,
        "annotated_image_base64": img_base64
    })


@app.post("/bt/start")
async def start_bt_server():
    # await bluetooth_server.start()
    return {"message": "Bt server started"}


@app.post("/bt/stop")
async def stop_bt_server():
    # await bluetooth_server.stop()
    return {"message": "Bt server stopped"}


# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await socket_service.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Broadcast message to all clients
            await socket_service.broadcast(f"Client said: {data}")
    except WebSocketDisconnect:
        socket_service.disconnect(websocket)  # Disconnect WebSocket client
        await socket_service.broadcast("A client disconnected.")


@app.get("/samples/{sampleId}/image")
async def get_image(sampleId):
    sample = get_sample(sampleId)
    print(sample)

    if sample is None:
        return {"error": "No sample was found"}

    image_path = os.path.join(sample["path"])

    # Check if the file exists
    if os.path.exists(image_path):
        try:
            print(image_path)
            return FileResponse(image_path, media_type="image/png")
        except Exception as e:
            return {"error": f"Failed to read the image: {str(e)}"}
    else:
        return {"error": "Image not found"}


@app.get("/predictions")
async def get_all_predictions_api():
    try:
        predictions = get_all_predictions()
        return JSONResponse(content={"predictions": predictions})
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"message": f"An error occurred: {str(e)}"}
        )


@app.get("/prediction/{prediction_id}")
def get_prediction_by_id(prediction_id: int):
    prediction = get_prediction_by_id(prediction_id)
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")

        # Convert the prediction to a dictionary (row_factory handles this)
    result = dict(prediction)

    return result
