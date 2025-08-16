from typing import Optional
from pydantic import BaseModel,Field
from fastapi import Query

class BasicChat(BaseModel):
    input:str=Field(...,description="client side message for chat model.")
    thread_id:Optional[str]=Field(None,description="thread id for the current chat")
