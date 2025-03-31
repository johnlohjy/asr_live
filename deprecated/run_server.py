from server import Server

server = Server()
host = "localhost"
port = 9090
try:
    server.run(host=host,port=port)
except KeyboardInterrupt:
    print("Keyboard Interrupt")