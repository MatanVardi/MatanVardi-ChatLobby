from client_connection import ServerSocket
from settings import *

class Server(threading.Thread):
    def __init__(self, host, port):
        super().__init__()
        self.connections = []
        self.host = host
        self.port = port

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.host, self.port))

        sock.listen(1)
        print("Listening at", sock.getsockname())

        while True:
            sc, sock_name = sock.accept()
            print(f"Accepting a new connection from {sc.getpeername()} to {sc.getsockname()}")

            server_socket = ServerSocket(sc, sock_name, self)
            server_socket.start()

            self.connections.append(server_socket)
            print(f"Ready to receive messages from {sc.getpeername()}. Active connections: {len(self.connections)}")

            # Broadcast updated count after adding a connection
            self.broadcast_connection_count()

    def broadcast(self, message, source):
        """Send a message to all clients except the source."""
        for connection in self.connections:
            if connection.sock_name != source:
                connection.send(message)

    def broadcast_connection_count(self):
        """Broadcast the current number of connections to all clients"""
        count = len(self.connections)
        count_msg = f"COUNT:{count}"
        print(f"Broadcasting connection count: {count}")
        for connection in self.connections:
            try:
                connection.send(count_msg)
            except Exception as e:
                print(f"Error sending count to client: {e}")

    def remove_connection(self, connection):
        """Remove a connection and update all clients about the new count."""
        if connection in self.connections:
            self.connections.remove(connection)
            active_connections = len(self.connections)
            print(f"Connection removed. Active connections: {active_connections}")
            # Broadcast updated count immediately after removing a connection
            self.broadcast_connection_count()

    def get_active_connections_count(self):
        """Return the current number of active connections."""
        return len(self.connections)
