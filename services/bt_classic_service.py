# import bluetooth
# import logging

# # Set up logging
# logging.basicConfig(level=logging.DEBUG)

# class BluetoothServer2:
#     def __init__(self):
#         self.server_socket = None

#     async def start(self):
   
#             logging.debug("Initializing Bluetooth server...")
            
#             # Create the Bluetooth socket for RFCOMM communication
#             logging.debug("Creating RFCOMM Bluetooth socket...")
#             self.server_socket = bluetooth.BluetoothSocket()
            
#             local_address = bluetooth.lookup_name()
            
#             # Bind the server socket to a local Bluetooth address and port (RFCOMM channel 1)
#             self.server_socket.bind(local_address, 1)  # Bind to RFCOMM channel 1
#             logging.debug("Binding to RFCOMM channel 1...")
            
#             # Start listening for incoming connections
#             self.server_socket.listen(1)
#             logging.info("Bluetooth server started and listening on RFCOMM channel 1.")
            
#             # Accept an incoming connection
#             self.client_socket, client_address = self.server_socket.accept()
#             logging.info(f"Accepted connection from {client_address}")
            
#             # Handle communication with the client
#             await self.handle_communication()
            
        
    
#     async def handle_communication(self):
#         try:
#             while True:
#                 data = self.client_socket.recv(1024)  # Receive up to 1024 bytes
#                 if not data:
#                     break  # If no data, break the loop (client disconnected)
#                 logging.info(f"Received: {data.decode('utf-8')}")
                
#                 # Send a response to the client
#                 self.client_socket.send("Message received.".encode('utf-8'))
#         except Exception as e:
#             logging.error(f"Error during communication: {str(e)}")
#         finally:
#             self.client_socket.close()
#             logging.info("Client connection closed.")

#     def stop_server(self):
#         if self.server_socket:
#             self.server_socket.close()
#             logging.info("Bluetooth server stopped.")
#         else:
#             logging.warning("Server socket was not initialized.")
