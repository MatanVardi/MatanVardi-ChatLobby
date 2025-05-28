from settings import *
import models

class Base(DeclarativeBase):
    pass

class Database:
    def __init__(self):
        db_path = "data/instance/chat.db"  # This will create the DB in the current working directory
        self.db = create_engine(f"sqlite:///{db_path}")

        # Creates tables for all models that inherit from Base
        #Base.metadata.create_all(self.db)
        self.Session = sessionmaker(bind=self.db)
        self.session = self.Session()


    def __del__(self):
        self.session.close()

    def add_message(self, content, user_id):
        """
        Create a new message in the database.
        """

        new_message = models.Message(content = content, user_id = user_id)
        self.session.add(new_message)
        self.session.commit()

    def add_user(self, user_name, password, color):
        """
        Create a new user account in the database.
        """

        new_user = models.User(name=user_name, password=password, color = color)
        self.session.add(new_user)
        self.session.commit()
        print("Congratulation! your account has been created.  Joining chat....")
        return new_user

    def clear_all_messages(self):
        """Delete all messages from the database."""
        try:
            self.session.query(models.Message).delete()
            self.session.commit()
            print("All messages cleared from database")
            return True
        except Exception as e:
            print(f"Error clearing messages: {e}")
            self.session.rollback()
            return False
