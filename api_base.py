from fastapi import FastAPI,Path,Query,HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
from langchain_core.messages import HumanMessage
from pydantic import BaseModel,Field
from typing import Annotated,Sequence,Literal,Optional
from deep_research.supervisor_subgraph import supervisor_graph
from search_main import main_graph
from fastapi import Form # FORM for Form Submisson from The Frontend
import uuid
import json
from fastapi.middleware.cors import CORSMiddleware 

app=FastAPI()
# Cors Setup
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
    print("Hello world")

@app.post('/chat')
async def chat(input:str = Form(...)):
    print("Recieved INPUT", input)
    result=main_graph.invoke({
        "messages":HumanMessage(content=input)
    },{"configurable":{"thread_id":random_thread_id}}
    )

    print("RESULT", result)
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
    result=supervisor_graph.invoke(initial_topic)
    print(result)
