import serial
import os
import logging
import time
from PIL import Image
import io
from datetime import datetime
import shutil
import asyncio
from .helper_log import logger
from ai.predictor import predict
from services.db_service import get_sample_details_by_name, insert_sample, save_prediction_to_db
import json


def get_highest_confidence_predictions(predictions):
    if not predictions:
        return []

    # Find the highest confidence level
    highest_confidence = max(predictions, key=lambda x: x['confidence'])[
        'confidence']

    # Filter predictions that have the highest confidence level
    highest_confidence_predictions = [
        prediction for prediction in predictions if prediction['confidence'] == highest_confidence]

    # Return the predictions inside a list
    return highest_confidence_predictions


class SerialPortManager:
    def __init__(self, port, socket_manager, baudrate=9600, output_dir="received_images"):
        """
        Initialize the serial port manager.

        Args:
            port (str): Serial port to connect to.
            baudrate (int): Baud rate for the serial connection.
            output_dir (str): Directory to save the received images.
        """
        self.port = port
        self.baudrate = baudrate
        self.output_dir = output_dir
        self.file_counter = 1  # Counter to generate unique filenames
        self.serial_connection = None
        self.running = False
        self.socket_manager = socket_manager

        # Ensure the output directory exists
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def connect(self):
        """Establish a serial connection."""
        try:
            self.serial_connection = serial.Serial(
                self.port, self.baudrate, timeout=5
            )
            logger.info(f"Connected to {self.port} at {self.baudrate}.")
            self.running = True
        except serial.SerialException as e:
            logger.error(f"Failed to connect to serial port: {e}")
            self.running = False

    def disconnect(self):
        """Close the serial connection."""
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            logger.info("Serial connection closed.")
        self.running = False

    def save_image_to_file(self, data):
        """Save binary image data to a file."""
        try:
            temp_folder = 'data/temp/'
            if not os.path.exists(temp_folder):
                os.makedirs(temp_folder)

            temp_path = temp_folder + f"image_{self.file_counter}.jpg"
            with open(temp_path, "wb") as buffer:
                buffer.write(data)

            # Call a function to insert sample or log details into a database
            insert_sample(f"image_{self.file_counter}.jpg", temp_folder +
                          f"image_{self.file_counter}.jpg", datetime.now(), False)

            sample = get_sample_details_by_name(
                f"image_{self.file_counter}.jpg")
            # After updating the database get the prediction of the image and sent it to the client

            logger.info(f"Image saved to {temp_path}.")
            self.file_counter += 1
            return sample
        except Exception as e:
            logger.exception("Error saving image to file", exc_info=e)

    def display_image(self, data):
        """Display the image using PIL."""
        try:
            image = Image.open(io.BytesIO(data))
            image.show()
        except Exception as e:
            logger.error(f"Failed to display image: {e}")

    def send_acknowledgment(self):
        """Send an acknowledgment to the sender."""
        acknowledgment = b"IMAGE_RECEIVED"
        self.serial_connection.write(acknowledgment)
        logger.info("Acknowledgment sent: IMAGE_RECEIVED")

    async def read_images(self):
        """Continuously read images from the serial port."""
        data = bytearray()

        while self.running:
            try:
                if self.serial_connection.in_waiting > 0:
                    # Read available data
                    chunk = self.serial_connection.read(
                        self.serial_connection.in_waiting)
                    data.extend(chunk)
                    logger.info(f"Received {len(chunk)} bytes.")

                # Check for end of image data (JPEG EOF marker)
                if data.endswith(b"\xFF\xD9"):  # JPEG EOF marker
                    # Save the image to a file and get its metadata
                    sample = self.save_image_to_file(data)

                    if not sample:
                        logging.error("Failed to save the image.")
                        return

                    # Perform prediction on the saved image
                    predictions_array, annotated_image_base64 = predict(sample)
                    predictions = get_highest_confidence_predictions(
                        predictions_array)
                    # logger.info(annotated_image_base64)
                    if len(predictions) == 0:
                        # logging.error(f"Prediction error:{
                        #               predictions['error']}")
                        logger.info(
                            "*************PPP NO PREDICTION ****************")
                        logger.info(predictions)
                    logger.info("*************OKKKKKK****************")
                    logger.info(predictions)

                    save_prediction_to_db(
                        prediction=predictions, annotated_image=annotated_image_base64)

                    # modified_data = {
                    #     'class_id': predictions[0]['class_id'] if predictions and 'class_id' in predictions[0] else None,
                    #     'class_name': predictions[0]['class_name'] if predictions and 'class_name' in predictions[0] else None,
                    #     'attributes': predictions[0]['attributes'] if predictions and 'attributes' in predictions[0] else None,
                    #     'confidence': predictions[0]['confidence'] if predictions and 'confidence' in predictions[0] else None,
                    #     'bbox': predictions[0]['bbox'] if predictions and 'bbox' in predictions[0] else None,
                    #     'annotated_image': annotated_image_base64
                    # }
                    # modified_data = {
                    #     **predictionss,
                    #     "annotated_image": annotated_image_base64
                    # }

                    # logger.error(modified_data)
                    # logging.info(modified_data)

                    # message = json.dumps(modified_data)
                    # Use the socket manager's broadcast method to send the message
                    # logger.error("THE MESSAGE {message}".format(predictions))
                    logger.info(f"THE MESSAGE: YOO YOO")
                    await self.socket_manager.broadcast("Hello mr. how do you do.")
                    # await self.socket_manager.broadcast_image()

                    # Optionally send acknowledgment back to the client
                    self.send_acknowledgment()

                    # Clear buffer and add optional delay
                    data.clear()  # Clear buffer for next image
                    time.sleep(1)

            except serial.SerialException as e:
                logger.error(f"Serial error: {e}")
                self.disconnect()
            except Exception as e:
                logger.error(f"Error during image processing: {e}")
                self.send_acknowledgment()
                data.clear()

    async def run(self):
        """Run the serial port manager."""
        if not self.serial_connection or not self.serial_connection.is_open:
            logger.error(
                "Serial connection is not open. Call connect() first.")
            return

        logger.info("Starting to read images from serial port...")
        await self.read_images()
