from settings import *
import models


class AuthManager:
    """
    Manages user authentication including login, registration, and logout.
    Handles all user credential validation and maintains the current user session.
    """

    def __init__(self, database):
        self.current_user = None  # Stores the currently logged-in user
        self.database = database  # Database connection for user operations

    def login(self):
        """
        Handle user login process.
        Prompts for username and password, validates credentials against the database,
        and sets the current_user if authentication succeeds.
        Returns:
            bool: True if login successful, False otherwise
        """
        user_name = input("Please enter your account's username: ")
        user_password = input("Enter your account's password: ")

        # Query user from database
        result = self.database.session.execute(select(models.User).where(models.User.name == user_name))
        user = result.scalar_one_or_none()

        if user and check_password_hash(user.password, user_password):
            # Valid credentials - set current user and return success
            self.current_user = user
            print(f"Welcome back, {user.name}!")
            return True
        elif user is None:
            # Username not found in database
            print("Sorry, that username doesn't exist.")
            return False
        else:
            # Username exists but password is incorrect
            print("Sorry, password incorrect.")
            return False

    def register(self):
        """
        Handle user registration process.
        Collects username and password with validation, checks for existing users,
        hashes the password securely, and creates a new user account.
        Returns:
            bool: True if registration successful, False otherwise
        """
        # Get username with validation (minimum 6 characters)
        user_name = input("please enter your username (min of 6 characters): ")
        while len(user_name) < 6:
            user_name = input("please enter your username (min of 6 characters): ")

        # Get password with validation (minimum 8 characters)
        password = input("please enter your password (min of 8 characters): ")
        while len(password) < 8:
            password = input("please enter your password (min of 8 characters): ")

        # Check if username is already taken
        result = self.database.session.execute(select(models.User).where(models.User.name == user_name))
        existing_user = result.scalar_one_or_none()

        if existing_user:
            print("Couldn't register you, Username already taken!")
            return False

        # Hash the password securely before storing
        password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=6)

        # Assign a random color to the new user
        color_name = random.choice(USER_COLOR_NAMES)

        # Create user in database and set as current user
        self.current_user = self.database.add_user(user_name, password, color_name)

        return True

    def logout(self):
        """
        Log out the current user.
        Clears the current_user attribute and displays logout message.
        Returns:
            bool: Always returns False to indicate user is no longer logged in
        """
        self.current_user = None
        print("You have logged out.  Thank you for choosing my service 0_0")
        return False