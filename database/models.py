from sqlalchemy import Column,Integer,String,DateTime,ForeignKey,JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__="users"

    id=Column(Integer,primary_key=True)
    email=Column(String,unique=True,index=True,nullable=False)
    hashed_password=Column(String,nullable=False)
    creation_date=Column(DateTime(timezone=True),server_default=func.now())
    chats=relationship("ChatHistory",back_populates="owner")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"

class ChatHistory(Base):
    __tablename__="chat_histories"
    
    id=Column(Integer,primary_key=True)
    thread_id=Column(String,unique=True,index=True) #nullable=False
    user_id=Column(Integer,ForeignKey("users.id"))
    messages=Column(JSON,nullable=False)
    created_at=Column(DateTime(timezone=True),server_default=func.now())
    owner=relationship("User",back_populates="chats")

