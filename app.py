# app.py
from console_interface import ConsoleInterface
from auth_manager import AuthManager
from lobby_chat import LobbyChat
from database import Database

# Create instances
database = Database()

auth_manager = AuthManager(database)
console_interface = ConsoleInterface(auth_manager)

# Create lobby_chat with reference to both auth_manager and console_interface
lobby_chat = LobbyChat(auth_manager, console_interface)

# Set the lobby_chat in console_interface
console_interface.set_lobby_chat(lobby_chat)

# Start the application
console_interface.run()

