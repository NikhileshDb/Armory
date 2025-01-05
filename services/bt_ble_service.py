# # bless, bleak
# from typing import Any
# from bless import BlessServer, BlessGATTCharacteristic, GATTCharacteristicProperties, GATTAttributePermissions
# import logging
# from constants import BTBLEConstants

# logging.basicConfig(level=logging.INFO)

# class BluetoothServer:
#     def __init__(self):
#         self.received_chunks = []
#         self.image_characteristic_uuid = BTBLEConstants.CHARACTERISTIC_UUID
#         self.service_uuid = BTBLEConstants.SERVICE_UUID
#         self.server = None

#     async def start(self):
#         # Initialize BLESS server
#         self.server = BlessServer("Armory BT")
#         self.server.read_request_func = self.read_request
#         self.server.write_request_func = self.write_request

#         await self.server.add_new_service(self.service_uuid)

#         properties = (
#                 GATTCharacteristicProperties.read |
#                 GATTCharacteristicProperties.write
#                 )

#         value = None

#         permissions = (
#             GATTAttributePermissions.readable |
#             GATTAttributePermissions.writeable
#         )

#         # Add characteristic with properties, value, and permissions
#         await self.server.add_new_characteristic(
#             self.service_uuid,  # Service UUID
#             self.image_characteristic_uuid,  # Characteristic UUID
#             properties,  # Properties
#             value,       # Initial value
#             permissions,  # Permissions
#         )

#         await self.server.start()

#         logging.info(f"Is advertising: {await self.server.is_advertising()}")
#         logging.info("BT Server started")

#     async def stop(self):
#         if self.server:
#             await self.server.stop()
#             logging.info("BT Server stopped")

#     def read_request(characteristic: BlessGATTCharacteristic, **kwargs) -> bytearray:
#         logging.debug(f"Reading {characteristic.value}")
#         return characteristic.value

#     def write_request(characteristic: BlessGATTCharacteristic, value: Any, **kwargs):
#         characteristic.value = value
#         logging.debug(f"Char value set to {characteristic.value}")
#         if characteristic.value == b"\x0f":
#             logging.debug("NICE")

# class ImageCharacteristic(BlessGATTCharacteristic):
#     def __init__(self):
#         super().__init__(
#             uuid= BTBLEConstants.CHARACTERISTIC_UUID,
#             properties=GATTCharacteristicProperties.write | GATTCharacteristicProperties.read,
#             permissions=GATTAttributePermissions.readable | GATTAttributePermissions.writeable,
#             value=None
#         )
#         self.received_chunks = []

#     async def on_write_request(self, data: bytes) -> bool:
#         try:
#             self.received_chunks.append(data)
#             logging.info(f"Received chunk of size: {len(data)} bytes")

#             # Check if transfer is complete
#             if self.is_transfer_complete(data):
#                 await self.stitch_image()

#             return True
#         except Exception as e:
#             logging.error(f"Error processing write request: {e}")
#             return False

#     async def stitch_image(self):
#         try:
#             # complete_data = b''.join(self.received_chunks)
#             # image = Image.open(io.BytesIO(complete_data))
#             # image.save("received_image.jpg")
#             # logging.info("Image successfully saved")
#             self.received_chunks = []  # Reset for next transfer
#         except Exception as e:
#             logging.error(f"Error processing complete image: {e}")

#     def is_transfer_complete(self, data: bytes) -> bool:
#         return len(data) < 20  # Example: last packet might be smaller than MTU
