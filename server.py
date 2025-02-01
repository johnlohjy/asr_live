# https://websockets.readthedocs.io/en/stable/reference/sync/server.html
# check what's the diff between the threading library and asyncio library

from websockets.sync.server import serve

class Server:

    def handle_new_connection(self,websocket):
        '''
        Get client connection info
        Initialise the client manager
        '''
        pass

    def recv_audio(self,websocket):
        pass

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

        The handler receives the ServerConnection instance, which you can use to send and receive messages.

        Once the handler completes, either normally or with an exception, the server performs the closing 
        handshake and closes the connection.

        Treat as context manager. Call serve_forever() to serve requests
        '''
        with serve(handler=self.recv_audio, host=host, port=port) as server:
            server.serve_forever()

        