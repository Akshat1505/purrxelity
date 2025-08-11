from pydantic import BaseModel,EmailStr
from datetime import datetime
from typing import List,Dict,Any,Optional

class UserBase(BaseModel):
    email:EmailStr

class UserCreate(UserBase):
    password:str

class UserUpdate(BaseModel):
    email:Optional[EmailStr]=None
    password:Optional[str]=None

class UserRead(UserBase): #UserBase
    id:int
    creation_date:datetime
    hashed_password:str
    class Config:
        from_attributes=True

class ChatHistoryBase(BaseModel):
    thread_id:str
    messages:List[Dict[str,Any]]

class ChatHistoryCreate(ChatHistoryBase):
    pass

class ChatHistoryRead(ChatHistoryBase):
    id:int
    user_id:int
    created_at:datetime

    class Config:
        from_attributes=True

class MessageResponse(BaseModel):
    message:str
