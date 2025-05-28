from settings import *
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(Integer, primary_key = True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(100), unique = True)
    color: Mapped[str] = mapped_column(String(20))
    messages = relationship("Message", back_populates="user")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.name}>"


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    content: Mapped[str] = mapped_column(String(500))
    timestamp: Mapped[datetime] = mapped_column(default=datetime.now())

    # Foreign key to User
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    # Relationship to User model
    user = relationship("User", back_populates="messages")

    def __repr__(self) -> str:
        return f"<Message(id={self.id}, user_id={self.user_id}, timestamp={self.timestamp})>"
