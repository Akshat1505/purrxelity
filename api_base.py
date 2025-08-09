from fastapi import FastAPI,Path,Query,HTTPException
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from langchain_core.messages import HumanMessage
from pydantic import BaseModel,Field
from typing import Annotated,Sequence,Literal,Optional
from deep_research.supervisor_subgraph import supervisor_graph
from search_main import main_graph
from database.database import engine,get_db
from database import models
import uuid
import json

@asynccontextmanager
async def start_engine(app:FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    yield

app=FastAPI(lifespan=start_engine)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
random_thread_id=uuid.uuid4()

@app.get('/')
async def root():
    print("Welcome to Purrxelity API Dashboard")

@app.post('/chat')
async def chat(input:str):
    result=main_graph.invoke({
        "messages":HumanMessage(content=input)
    },{"configurable":{"thread_id":random_thread_id}}
    )
    return result["messages"][-1].content

@app.post('/chat/deep_research')
async def deep_research(initial_topic:str):
    initial_state = {
        "topic": initial_topic,
        "sections":[],
        "completed_sections": [],
        "messages": [],
        "final_report":""
    }
    result=supervisor_graph.invoke(initial_state)
    return result["final_report"][0]

## add creation,deletion,updation of user, 
