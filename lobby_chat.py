from settings import *
import models


class LobbyChat:
    def __init__(self, auth_manager, console_interface):
        self.auth_manager = auth_manager
        self.console_interface = console_interface
        self.first_login = True
        self.running = True
        self.delay_between_messages = 6
        self.server_user_count = 0  # Initialize with 0
        self.last_message_time = 0  # Add this line to track the last message time

    def enter_chat_room(self):
        """Enter the chat room."""
        # Check if user is logged in - if not, return immediately
        if not self.auth_manager.current_user:
            return

        # Connect to server first
        server_ip = input("Enter the server's IP address: ")
        connected = self.connect_to_server(server_ip, 8888)
        if not connected:
            print("Could not connect to chat server. Please try again later.")
            return

        # Wait briefly to receive the initial COUNT message
        time.sleep(0.5)

        # Now show the chat room header
        print("\n===== CHAT ROOM =====")
        if self.first_login:
            print("TIP: Type '/menu' to see menu options.")
            self.first_login = False

        print("You are now in the chat room.")
        print(f"Current users in chat: {self.server_user_count}")
        self.show_message_history()  # Add this line here

        if self.server_user_count < 2:
            print("Waiting for more users to join before you can send messages...")
        else:
            print("There are enough users. You can send messages!")

        print("Type your messages below:")

        # Chat input loop
        while self.auth_manager.current_user and self.running:
            message = input("> ")

            if message.lower() == '/menu':
                # Delegate to console_interface to show menu
                self.console_interface.show_menu()
                # Check if user logged out from menu
                if not self.auth_manager.current_user:
                    # Send logout message to server
                    self.send_logout_message()
            elif message.lower() == '/status':
                # Add a status command to check current user count
                print(f"Current users in chat: {self.server_user_count}")
                if self.server_user_count < 2:
                    print("Waiting for more users to join before you can send messages...")
                else:
                    print("There are enough users. You can send messages.")

            elif message.lower().startswith('/history'):
                # Extract optional minutes parameter
                parts = message.split()
                minutes = 10  # Default
                if len(parts) > 1:
                    try:
                        minutes = int(parts[1])
                    except ValueError:
                        print("Invalid number of minutes. Using default 10 minutes.")

                self.display_recent_messages(minutes)

            else:
                self.handle_message(message)

    def load_banned_words(self, filename):
        try:
            with open(filename, 'r') as file:
                return [line.strip().lower() for line in file]
        except FileNotFoundError:
            print(f"Warning: Banned words file not found at {filename}")
            return []
        except Exception as e:
            print(f"Error loading banned words: {e}")
            return []

    def contains_banned_words(self, message, banned_words):
        message_lower = message.lower()
        for word in banned_words:
            if word in message_lower:
                return True
        return False

    def censor_message(self, message, banned_words):
        message_lower = message.lower()
        censored = message
        for word in banned_words:
            if word in message_lower:
                # Replace with asterisks
                censored = censored.replace(word, '*' * len(word))
        return censored

    def handle_message(self, message):
        # Skip empty messages
        if not message.strip():
            return False

        # Load banned words
        banned_words = self.load_banned_words("data/banned_words.txt")

        # Check if message contains banned words
        if self.contains_banned_words(message, banned_words):
            censored_message = self.censor_message(message, banned_words)
            print("Your message contains sensitive words and has been censored.")
            message = censored_message  # Use the censored version


        # Check if enough users are connected (with clear messaging)

        if self.server_user_count < 2:
            print(f"Cannot send message: Only {self.server_user_count} user connected. Wait for more users to join!")
            return False

        # Direct time check using time.time() (seconds since epoch)
        current_time = time.time()
        time_since_last = current_time - self.last_message_time

        if self.last_message_time > 0 and time_since_last < self.delay_between_messages:
            # Not enough time has passed
            remaining = self.delay_between_messages - time_since_last
            print(f"There is a time limit. Please wait {remaining:.1f} more seconds.")
            return False

        # It's the time sent the last message (it's called cureent time because it's all relative)
        self.last_message_time = current_time

        user_name = self.auth_manager.current_user.name
        user_color = self.auth_manager.current_user.color
        user_id = self.auth_manager.current_user.id

        # Format the message for display
        colored_message = colored(message, user_color)
        print(f"You said: {colored_message}")

        # Send to server if connected
        if hasattr(self, 'client_socket') and self.client_socket:
            try:
                # Format: name:message:color:timestamp
                #if self.server_user_count == 0:
                   # num_of_message_rows = self.database.session.query(self.message_model).delete()
                timestamp = datetime.now().strftime("%Y/%m/%d/%H:%M")
                server_message = f"{user_name}:{message}:{user_color}:{timestamp}"
                self.client_socket.send(server_message.encode('utf-8'))
            except Exception as e:
                print(f"Error sending to server: {e}")

        # Always save to local database
        self.auth_manager.database.add_message(message, user_id)

        return True

    def enough_time_has_passed(self):
        """Check if enough time has passed since the last message."""
        # Get last message
        last_message = self.get_last_message_from_current_user()

        # If no previous message, allow sending
        if last_message is None:
            print("DEBUG: No previous message found, allowing message.")
            return True

        # Calculate time difference in seconds
        current_time = datetime.now()
        last_time = last_message.timestamp
        time_diff = (current_time - last_time).total_seconds()

        print(f"DEBUG: Time since last message: {time_diff:.1f} seconds (limit: {self.delay_between_messages} seconds)")

        # Check if enough time has passed
        if time_diff >= self.delay_between_messages:
            return True
        else:
            # Calculate remaining time
            remaining = self.delay_between_messages - time_diff
            print(f"There is a time limit. Please wait {remaining:.1f} more seconds.")
            return False

    def get_last_message_from_user(self, user_id):
        """Get the most recent message from a specific user."""
        try:
            result = self.auth_manager.database.session.execute(
                select(models.Message)
                .where(models.Message.user_id == user_id)
                .order_by(models.Message.timestamp.desc())
                .limit(1)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            print(f"Error getting last message: {e}")
            return None

    def get_last_message_from_current_user(self):
        """Get the most recent message from the currently logged in user."""
        if not self.auth_manager.current_user:
            return None
        return self.get_last_message_from_user(self.auth_manager.current_user.id)

    def send_logout_message(self):
        """Send a message to the server that user has logged out."""
        if hasattr(self, 'client_socket') and self.client_socket and self.auth_manager.current_user:
            try:
                user_name = "System"
                message = f"{self.auth_manager.current_user.name} has logged out."
                color = "white"
                timestamp = datetime.now().strftime("%Y/%m/%d/%H:%M")
                server_message = f"{user_name}:{message}:{color}:{timestamp}"
                self.client_socket.send(server_message.encode('utf-8'))
                # Give a moment for the message to be sent
                time.sleep(0.1)
            except:
                pass

            try:
                self.client_socket.close()
            except:
                pass
            self.client_socket = None

    def display_recent_messages(self, minutes=10):
        """Display messages from the last 'minutes' minutes."""
        try:
            # Get current time and calculate the cutoff time
            now = datetime.now()
            cutoff_time = now - timedelta(minutes=minutes)

            # Query for messages newer than the cutoff time
            result = self.auth_manager.database.session.execute(
                select(models.Message)
                .join(models.User)
                .where(models.Message.timestamp >= cutoff_time)
                .order_by(models.Message.timestamp)
            )

            messages = result.all()

            if not messages:
                print(f"No messages in the last {minutes} minutes.")
                return

            print(f"\n--- Messages from the last {minutes} minutes ---")
            for message_row in messages:
                message = message_row[0]  # Extract the Message object from the row
                user = message.user
                timestamp_str = message.timestamp.strftime("%Y/%m/%d/%H:%M")

                # Format the message similarly to how chat messages are displayed
                formatted_message = f"{user.name} ({timestamp_str}): {message.content}"

                # Apply color if available
                colored_message = colored(formatted_message, user.color)
                print(colored_message)
            print("--- End of message history ---")
        except Exception as e:
            print(f"Error displaying recent messages: {e}")

    # This method should be called when a user joins the chat room
    def show_message_history(self):
        """Show recent message history when a user joins the chat."""
        # Default to showing messages from the last 10 minutes
        self.display_recent_messages(10)

    def connect_to_server(self, host, port):
        """Connect to the chat server."""
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((host, port))

            # Start a thread to listen for incoming messages from server
            self.receiver_thread = threading.Thread(target=self.receive_messages)
            self.receiver_thread.daemon = True
            self.receiver_thread.start()

            print(f"Connected to chat server")
            return True
        except Exception as e:
            print(f"Could not connect to chat server: {e}")
            return False

    def receive_messages(self):
        """Listen for messages from the server."""
        message_received = True

        while self.running and self.auth_manager.current_user and hasattr(self,
                                                                          'client_socket') and self.client_socket and message_received:
            try:
                # Use a timeout to prevent blocking forever
                self.client_socket.settimeout(0.1)
                try:
                    message = self.client_socket.recv(1024).decode('utf-8')
                    message_received = bool(message)  # Empty message means disconnect
                except socket.timeout:
                    # If timeout occurs, just continue the loop
                    continue
                finally:
                    # Reset the timeout to blocking mode
                    self.client_socket.settimeout(None)

                if message_received and self.auth_manager.current_user:  # Only process if still logged in
                    # Check if it's a count message
                    if message.startswith("COUNT:"):
                        try:
                            # Extract the count
                            count_str = message.split(":")[1]
                            old_count = self.server_user_count
                            self.server_user_count = int(count_str)

                            # Only show notifications for significant changes
                            if old_count < 2 and self.server_user_count >= 2:
                                print(f"\nUsers in chat: {self.server_user_count}")
                                print("Enough users have joined! You can now send messages.")
                                print("> ", end="", flush=True)
                            elif old_count >= 2 and self.server_user_count < 2:
                                print(f"\nUsers in chat: {self.server_user_count}")
                                print("Not enough users to send messages. Waiting for more to join...")
                                print("> ", end="", flush=True)
                        except Exception as e:
                            print(f"\nError parsing count message: {e}")
                            print("> ", end="", flush=True)
                    else:
                        # Print non-COUNT messages
                        # Clear the current line to avoid messing up the input prompt
                        print("\r", end="")
                        print(f"{message}")
                        print("> ", end="", flush=True)

            except Exception as e:
                print(f"\nError receiving message: {e}")
                message_received = False

        # Handle disconnection outside the loop
        if hasattr(self, 'client_socket') and self.client_socket:
            print("Disconnected from server")
            try:
                self.client_socket.close()
            except:
                pass
            self.client_socket = None
