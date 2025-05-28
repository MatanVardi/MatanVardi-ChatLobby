from settings import *

class ConsoleInterface:
    def __init__(self, auth_manager):
        self.auth_manager = auth_manager
        self.lobby_chat = None  # Will be set later
        self.running = True

    def set_lobby_chat(self, lobby_chat):
        """Set the lobby_chat after creation to avoid circular dependency."""
        self.lobby_chat = lobby_chat

    def run(self):
        """Main application loop."""
        while self.running:
            if not self.auth_manager.current_user:
                self.show_auth_menu()
            else:
                self.lobby_chat.enter_chat_room()
                # Handle case where we might have exited the application from chat
                self.running = self.lobby_chat.running

    def show_auth_menu(self):
        """Show login/register menu."""
        print("\n===== WELCOME TO CHAT APPLICATION =====")
        print("1. Login")
        print("2. Register")
        print("3. Exit")

        choice = input("Please enter your choice: ")

        self.process_auth_choice(choice)

    def process_auth_choice(self, choice):
        """Process choice from auth menu."""
        if choice == "1":  # Login
            self.handle_login()
        elif choice == "2":  # Register
            self.handle_register()
        elif choice == "3":
            self.exit()
        else:
            print("Invalid choice. Please try again.")

    def handle_login(self):
        """Handle the login process with retry options."""
        success = self.auth_manager.login()
        if not success:
            print("\nOptions:")
            print("1. Try logging in again")
            print("2. Return to main menu")
            retry_choice = input("Enter your choice: ")

            if retry_choice == "1":
                self.handle_login()  # Recursion for retry
            # Option 2 just returns to main menu

    def handle_register(self):
        """Handle the registration process with retry options."""
        success = self.auth_manager.register()
        if not success:
            print("\nOptions:")
            print("1. Try registering again")
            print("2. Return to main menu")
            retry_choice = input("Enter your choice: ")

            if retry_choice == "1":
                self.handle_register()  # Recursion for retry
            # Option 2 just returns to main menu

    def show_menu(self):
        """Display chat menu."""
        print("\n----- MENU -----")
        print("1. Logout")
        print("2. Exit")
        print("Enter anything else to return to chat.")

        choice = input("Enter your choice: ")

        if choice == "1":
            # Send logout message before logging out
            if self.lobby_chat:
                self.lobby_chat.send_logout_message()
            self.auth_manager.logout()
        elif choice == "2":
            self.exit()
        else:
            print("Invalid choice. Returning to chat...")

    def exit(self):
        """Exit the application."""
        print("Goodbye!")
        self.running = False
        if self.lobby_chat:
            self.lobby_chat.running = False
        sys.exit()