from fastapi import Depends, FastAPI,Path,Query,HTTPException,status
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from langchain_core.messages import HumanMessage
from typing import Annotated,Sequence,Literal,Optional,List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import user
from deep_research.supervisor_subgraph import supervisor_graph
import schemas
from search_main import main_graph
from database.database import engine,get_db
from database import models,crud,schemas
import uuid
import json
from schemas import BasicChat

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

## text endpoints

@app.post('/chat')
async def chat(user_input:BasicChat):
    result=main_graph.invoke({
        "messages":HumanMessage(content=user_input.input)
    },{"configurable":{"thread_id":random_thread_id}}
    )
    return {"message":result["messages"][-1].content}

@app.post('/chat/deep_research')
async def deep_research(initial_topic:BasicChat):
    initial_state = {
        "topic": initial_topic,
        "sections":[],
        "completed_sections": [],
        "messages": [],
        "final_report":""
    }
    result=supervisor_graph.invoke(initial_state)
    return {"message":result["final_report"][0]}

## user crud 

@app.post("/users/",response_model=schemas.UserRead,status_code=status.HTTP_201_CREATED)
async def create_user(user:schemas.UserCreate,db:AsyncSession=Depends(get_db)):
    db_user=await crud.get_user_by_email(db,email=user.email)
    if db_user: 
        raise HTTPException(status_code=400,detail="Email already registered")
    return await crud.create_user(db=db,user=user)

@app.get("/users/",response_model=List[schemas.UserRead])
async def read_users(skip:int=0,limit:int=100,db:AsyncSession=Depends(get_db)):
    users = await crud.get_users(db,skip=skip,limit=limit)
    return users

@app.get("/users/{user_id}",response_model=schemas.UserRead)
async def read_user(user_id:int,db:AsyncSession=Depends(get_db)):
    db_user=await crud.get_user_by_id(db,user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404,detail="User not found")
    return db_user

@app.delete("/users/{user_id}",response_model=schemas.MessageResponse)
async def delete_user(user_id:int,db:AsyncSession=Depends(get_db)):
    db_user=await crud.get_user_by_id(db,user_id)
    if db_user is None:
        raise HTTPException(status_code=404,detail="User not Found")
    await crud.delete_user(db,user_id)    
    return {"message":"User Deleted Successfully"}

## user chat crud

@app.post("/users/{user_id}/chats/",response_model=schemas.ChatHistoryRead,status_code=201)
async def create_chat_history(user_id:int,chat:schemas.ChatHistoryCreate,db:AsyncSession=Depends(get_db)):
    db_user=await crud.get_user_by_id(db,user_id)
    if db_user is None:
        raise HTTPException(status_code=404,detail="User not found")

    return await crud.create_chat_history(db=db,chat_data=chat,user_id=user_id)


