import serial
import os
import logging
import time
from PIL import Image
import io
from datetime import datetime
import shutil
import asyncio

from services.db_service import insert_sample

# Set up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


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
            logger.info(f"Connected to {self.port} at {
                        self.baudrate} baudrate.")
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

            logger.info(f"Image saved to {temp_path}.")
        except Exception as e:
            logger.exception("Error saving image to file", exc_info=e)

        self.file_counter += 1

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
                    self.save_image_to_file(data)
                    # Send image to WebSocket clients
                    await self.socket_manager.broadcast_image(data)
                    self.send_acknowledgment()

                    data.clear()  # Clear buffer for next image
                    time.sleep(1)  # Optional delay

            except serial.SerialException as e:
                logger.error(f"Serial error: {e}")
                self.disconnect()
            except Exception as e:
                logger.error(f"Error during image processing: {e}")
                data.clear()

    async def run(self):
        """Run the serial port manager."""
        if not self.serial_connection or not self.serial_connection.is_open:
            logger.error(
                "Serial connection is not open. Call connect() first.")
            return

        logger.info("Starting to read images from serial port...")
        await self.read_images()
