from settings import *


class ServerSocket(threading.Thread):
    def __init__(self, sc, sock_name, server):
        super().__init__()
        self.sc = sc  # socket object
        self.sock_name = sock_name  # address of client
        self.server = server  # reference to the server
        self.running = True
        self.user_name = None  # Will be set after authentication
        self.user_id = None  # Will be set after authentication

    def run(self):
        """Handle client communication."""
        try:
            self.server.broadcast_connection_count()

            while self.running:
                # Wait for message from client
                message = self.sc.recv(1024).decode('utf-8')
                if message:
                    # Process the received message
                    # Expected format: name:message:color:timestamp
                    try:
                        parts = message.split(':', 3)
                        if len(parts) == 4:
                            name, content, color, timestamp = parts

                            # If the username is "System", this is a system message (like user joining/leaving)
                            if name == "System":
                                # Broadcast system messages without modification
                                formatted_message = f"System: {content}"
                                print(f"[{self.sock_name}] {formatted_message}")
                                self.server.broadcast(formatted_message, self.sock_name)

                                # If this is a disconnect message, close the connection
                                if "logged out" in content or "disconnected" in content:
                                    # Extract username if possible
                                    words = content.split()
                                    if len(words) > 0:
                                        self.user_name = words[0]

                                    print(f"Client {self.sock_name} ({self.user_name or 'Unknown'}) logged out")
                                    self.running = False
                                    self.server.remove_connection(self)

                            else:
                                # Set the user_name from the first message received
                                if self.user_name is None:
                                    self.user_name = name
                                    # Broadcast a join message
                                    join_msg = f"System: {name} has joined the chat."
                                    self.server.broadcast(join_msg, self.sock_name)
                                    print(f"User {name} identified on connection {self.sock_name}")

                                # Format regular chat message for display
                                formatted_message = f"{name} ({timestamp}): {content}"
                                # Color the message using ANSI codes
                                if color in COLORS:
                                    formatted_message = f"{COLORS[color]}{formatted_message}{COLORS['reset']}"

                                print(f"[{self.sock_name}] {formatted_message}")

                                # Broadcast the formatted message
                                self.server.broadcast(formatted_message, self.sock_name)
                        else:
                            # Fall back to broadcasting the raw message
                            print(f"[{self.sock_name}] {message}")
                            self.server.broadcast(message, self.sock_name)
                    except Exception as e:
                        print(f"Error processing message: {e}")
                        self.server.broadcast(message, self.sock_name)
                else:
                    # Empty message means client disconnected
                    if self.user_name:
                        disconnect_msg = f"System: {self.user_name} has disconnected from the chat."
                        self.server.broadcast(disconnect_msg, self.sock_name)

                    print(f"Client {self.sock_name} has disconnected")
                    self.running = False
                    self.server.remove_connection(self)

        except ConnectionResetError:
            # Handle unexpected client disconnect
            if self.user_name:
                disconnect_msg = f"System: {self.user_name} has disconnected from the chat."
                self.server.broadcast(disconnect_msg, self.sock_name)

            print(f"Client {self.sock_name} forcibly disconnected")
            self.running = False
            self.server.remove_connection(self)
        finally:
            self.sc.close()

    def send(self, message):
        """Send a message to the client."""
        try:
            self.sc.sendall(message.encode('utf-8'))
        except (ConnectionResetError, BrokenPipeError):
            # Handle send to disconnected client
            print(f"Failed to send to {self.sock_name}")
            self.running = False
            self.server.remove_connection(self)
