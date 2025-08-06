from fastapi import FastAPI,Path,Query,HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
from langchain_core.messages import HumanMessage
from pydantic import BaseModel,Field
from typing import Annotated,Sequence,Literal,Optional
from search_main import main_graph
import uuid
import json

app=FastAPI()
random_thread_id=uuid.uuid4()

@app.get('/')
async def root():
    print("Hello world")

@app.post('/chat')
async def chat(input:str):
    result=main_graph.invoke({
        "messages":HumanMessage(content=input)
    },{"configurable":{"thread_id":random_thread_id}}
    )
    return result["messages"][-1].content

