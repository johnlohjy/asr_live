# https://websockets.readthedocs.io/en/stable/reference/sync/server.html
# check what's the diff between the threading library and asyncio library
from websockets.sync.server import serve
from websockets.exceptions import ConnectionClosed
import json
import numpy as np
import os
import wave

class Client:
    def __init__(self):
        self.frames_np = None

    def add_frames(self, frame_np):
        '''
        Add new audio chunks to frames buffer

        Check if need lock in the future
        '''
        if self.frames_np is None:
            # If the frames buffer is empty, initialise it with the new audio frames
            self.frames_np = frame_np.copy()
        else:
            # Append the new audio chunk to the existing frames buffer
            self.frames_np = np.concatenate((self.frames_np, frame_np), axis=0)

    def save_frames(self):
        '''
        Sample code to save the audio when client disconnects
        '''
        fp = os.path.join(os.getcwd(), "test_frames.wav")
        with wave.open(fp, "wb") as wavfile:
            wavfile: wave.Wave_write
            wavfile.setnchannels(1)
            wavfile.setsampwidth(2)
            wavfile.setframerate(16000)
            wavfile.writeframes(self.frames_np)





class ClientManager:
    '''
    Custom client manager class to handle clients connected over the 
    WebSocket server
    '''
    def __init__(self):
        self.clients = {}

    def add_client(self, websocket, client):
        '''
        Add a WebSocket server connection info and its associated client
        '''
        self.clients[websocket] = client

    def get_client(self, websocket):
        '''
        Retrieve a client associated with the WebSocket server connection info provided
        '''
        if websocket in self.clients:
            return self.clients[websocket]
        return False 




class Server:
    '''
    Server class handles
    - New client connections
    - Receiving and processing audio from client
    '''
    def __init__(self):
        self.client_manager = None




    def initialize_client(self, websocket):
        '''
        Initialize the new client and add it to the client manager
        '''
        client = Client()
        self.client_manager.add_client(websocket, client)




    def handle_new_connection(self,websocket):
        '''
        Get WebSocket server connection info when the client first connects
        Initialise the client manager
        Initialise the new client and add it to the client manager
        '''
        print('New client connected')

        # Get WebSocket server connection info when the client first connects
        # https://websockets.readthedocs.io/en/stable/reference/sync/server.html#websockets.sync.server.ServerConnection.recv
        serverConnectionInfo = websocket.recv()
        #serverConnectionInfo = json.loads(serverConnectionInfo)
        print(serverConnectionInfo)
        print('')

        # Initialise the client manager if not done
        if self.client_manager is None:
            self.client_manager = ClientManager()

        # Initialise the new client and add it to the client manager
        self.initialize_client(websocket)

        return True
    



    def get_audio_from_websocket(self, websocket):
        '''
        Receive audio chunks from the WebSocket and create a numpy array out of it
        '''
        # Subsequently, receive audio data (message) over the WebSocket server connection
        # https://websockets.readthedocs.io/en/stable/reference/sync/server.html#websockets.sync.server.ServerConnection.recv
        frame_data = websocket.recv()

        # Creates numpy array without copying it (more efficient)
        return np.frombuffer(frame_data, dtype=np.float32)




    def process_audio_frames(self, websocket):
        '''
        Get the audio chunk from the WebSocket as a numpy array

        Send a dummy transcription back to the client first
        '''
        # Get the audio chunk from the WebSocket as a numpy array
        frame_np = self.get_audio_from_websocket(websocket)
        print('"Received" audio chunk')
        # Get the client using its associated WebSocket
        client = self.client_manager.get_client(websocket)

        client.add_frames(frame_np)

        # Send a dummy transcription
        # https://websockets.readthedocs.io/en/stable/reference/sync/server.html#websockets.sync.server.ServerConnection.send
        # ServerConnection provides recv() and send() methods for receiving and sending messages.
        websocket.send(
            json.dumps({
                "test": "test response",
            })
        )

        return True




    def recv_audio(self,websocket):
        """
        First handle the new connection

        Continously process audio frames
        """

        # Try to handle the new connection
        if not self.handle_new_connection(websocket):
            return
        
        try:
            # Continously process audio frames
            while True: 
                if not self.process_audio_frames(websocket):
                    break
        except ConnectionClosed:
            print("Connection closed by client")
            client = self.client_manager.get_client(websocket)
            client.save_frames()
            print("Saved client frames")
        except Exception as e:
            print(f'Error: {e}')
        finally:
            websocket.close()
            del websocket




    def run(self,host,port):
        """
        Function to run the transcription server.

        Args:
            host (str): The host address to bind the server.
            port (int): The port number to bind the server.
        """
        
        '''
        Create a WebSocket Server (threading) that listens on host and port

        Whenever a client connects, the server creates a ServerConnection (threading implementation of a WebSocket server connection), performs the opening handshake, 
        and delegates to the handler

        The handler receives the ServerConnection instance, which we can use to send and receive messages.
        Once the handler completes, either normally or with an exception, the server performs the closing 
        handshake and closes the connection.

        Treat as context manager. Call serve_forever() to serve requests
        '''

        # https://websockets.readthedocs.io/en/stable/reference/sync/server.html
        with serve(handler=self.recv_audio, host=host, port=port) as server:
            print(f'Running Server on ws://{host}:{port}')
            server.serve_forever()

        