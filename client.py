import pyaudio
import websocket
import numpy as np
import threading
import time
import json

class Client:
    '''
    Client class handles 
    - websocket connections in a separate thread (send audio to server, receive data from server)
    - live audio recording and printing data in the main thread
    '''
    def __init__(self, host, port, record_seconds=10):
    
        # Audio Settings
        self.record_seconds = record_seconds
        self.chunk = 4096 # number of frames read per read
        self.format = pyaudio.paInt16  
        self.channels = 1                 
        self.rate = 16000 # number of frames per second
        self.p = pyaudio.PyAudio() # Set up PyAudio

        # Initialise WebSocketApp for long-lived connection
        # https://websocket-client.readthedocs.io/en/latest/examples.html
        # https://websocket-client.readthedocs.io/en/latest/app.html#websocket._app.WebSocketApp.__init__
        self.socket_url = f"ws://{host}:{port}"
        self.client_socket = websocket.WebSocketApp(
            self.socket_url, # websocket url
            on_open=self.on_open, # callback for opening websocket
            on_message=self.on_message, # callback for receiving data
            on_error=self.on_error, # callback for getting error
            on_close=self.on_close, # callback for closing connection
        )

        # Start Websocket client in a separate thread 
        # Multithreading is good for use-cases with a lot of I/O (implied waiting time)
        # - seamless thread switching during wait times when necessary
        self.ws_thread = threading.Thread(target=self.client_socket.run_forever)
        self.ws_thread.setDaemon(True)




    '''
    Websocket callbacks
    '''
    def on_open(self, ws):
        print("Opened connection")
        ws.send(
            json.dumps(
                {
                    "test": "open connection"
                }
            )
        )




    def on_message(self, ws, message):
        print("Received message from server:", message)




    def on_error(self, ws, error):
        print("WebSocket error:", error)




    def on_close(self, ws, close_status_code, close_msg):
        print("### closed ###")




    '''
    Websocket communication
    '''
    def send_packet_to_server(self, message):
        """
        Send an audio packet to the server using WebSocket.

        Args:
            message (bytes): The audio data packet in bytes to be sent to the server.
        """
        try:
            self.client_socket.send(message, opcode=websocket.ABNF.OPCODE_BINARY)
        except Exception as e:
            print("Error sending packet:", e)




    '''
    Helper function for recording audio
    '''
    def bytes_to_float_array(self, data):
        """
        Converts the given byte string to a NumPy float32 array.
        (Ensure the dtype matches your audio format.)
        """
        return np.frombuffer(data, dtype=np.float32)




    '''
    Start the client's operations
    '''
    def start(self):
        # Start websocket thread
        self.ws_thread.start()

        # Wait briefly to ensure connection is established
        time.sleep(1)

        # Open the audio stream for recording
        # https://people.csail.mit.edu/hubert/pyaudio/docs/#class-pyaudio
        try:
            self.stream = self.p.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk,
            )
        except Exception as e:
            print("Error opening audio stream:", e)
            return

        try:
            # Continuously records audio data from the input stream, sends it to the server via a WebSocket connection
            # Stops recording when the `RECORD_SECONDS` duration is reached 
            for _ in range(0, int(self.rate / self.chunk * self.record_seconds)):
                # Read samples from stream
                # https://people.csail.mit.edu/hubert/pyaudio/docs/#pyaudio.PyAudio.Stream
                data = self.stream.read(self.chunk, exception_on_overflow=False)

                audio_array = self.bytes_to_float_array(data)

                self.send_packet_to_server(audio_array.tobytes())

        except KeyboardInterrupt:
            print('Keyboard Interrupt: Stop recording.')

        # Stop recording
        self.stream.stop_stream() # stop stream
        self.stream.close() # close stream
        self.p.terminate() 
        self.client_socket.close() # close websocket connection
        print("Stopped recording and closed the connection.")




if __name__ == "__main__":
    host = "localhost" # use localhost since running client and server on same machine
    port = 9090
    client = Client(host, port, record_seconds=100)
    client.start()
