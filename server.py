# https://websockets.readthedocs.io/en/stable/reference/sync/server.html
# check what's the diff between the threading library and asyncio library
from websockets.sync.server import serve
import json
import numpy as np




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
        client = "test_client"
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
        frames_np = self.get_audio_from_websocket(websocket)
        print('"Received" audio chunk')

        # Send a dummy transcription
        websocket.send(
            json.dumps({
                "test": "test response",
            })
        )




    def recv_audio(self,websocket):
        """
        First handle the new connection

        Continously process audio frames
        """

        # Try to handle the new connection
        if not self.handle_new_connection(websocket):
            return
        
        self.process_audio_frames(websocket)
        



    def run(self,host,port):
        """
        Function to run the transcription server.

        Args:
            host (str): The host address to bind the server.
            port (int): The port number to bind the server.
        """
        
        '''
        Create a WebSocket Server (threading) that listens on host and port

        Whenever a client connects, the server creates a ServerConnection, performs the opening handshake, 
        and delegates to the handler

        The handler receives the ServerConnection instance, which we can use to send and receive messages.
        Once the handler completes, either normally or with an exception, the server performs the closing 
        handshake and closes the connection.

        Treat as context manager. Call serve_forever() to serve requests
        '''

        with serve(handler=self.recv_audio, host=host, port=port) as server:
            server.serve_forever()

        