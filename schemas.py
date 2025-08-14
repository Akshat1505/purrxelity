from pydantic import BaseModel,Field
from fastapi import Query

class BasicChat(BaseModel):
    input:str=Field(...,description="client side message for chat model.")
