from server import Server
from settings import *

if __name__ == "__main__":
    # Create and start the server
    hostname = socket.gethostname()
    server_ip = socket.gethostbyname(hostname)
    print(f"Tell clients to connect to this address {server_ip}")

    server = Server("0.0.0.0", 8888)
    print("Starting server...")
    server.start()
    server_is_on = True
    try:
        while server_is_on:
            msg = input("Server: ")
            if msg.lower() == 'exit':
                server_is_on = False
    except KeyboardInterrupt:
        print("\nShutting down server...")
