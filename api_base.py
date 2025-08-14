from fastapi import BackgroundTasks, Depends, FastAPI, File,Path,Query,HTTPException, UploadFile,status
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from langchain_core.messages import HumanMessage
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import user
from sqlalchemy.future import select
from deep_research.supervisor_subgraph import supervisor_graph
from rag_processing import ingest_pdf
import schemas
from search_main import main_graph
from database.database import engine,get_db
from database import models,crud,schemas
import uuid
import json,os,shutil
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
PDF_STORAGE_PATH="pdf_storage"
os.makedirs(PDF_STORAGE_PATH,exist_ok=True)

@app.get('/')
async def root():
    return "Welcome to Purrxelity API Dashboard"

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

@app.post("/users",response_model=schemas.UserRead,status_code=status.HTTP_201_CREATED)
async def create_user(user:schemas.UserCreate,db:AsyncSession=Depends(get_db)):
    db_user=await crud.get_user_by_email(db,email=user.email)
    if db_user: 
        raise HTTPException(status_code=400,detail="Email already registered")
    return await crud.create_user(db=db,user=user)

@app.get("/users",response_model=List[schemas.UserRead])
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

@app.put("/users/{user_id}",response_model=schemas.UserRead)
async def update_user(updated_user:schemas.UserUpdate,user_id:int,db:AsyncSession=Depends(get_db)):
    db_user=await crud.get_user_by_id(db,user_id)
    if db_user is None:
        raise HTTPException(status_code=404,detail="User not Found")
    updated_user_info=await crud.update_user(db,user_id,updated_user)
    return updated_user_info

## user chat crud

@app.post("/users/{user_id}/chats",response_model=schemas.ChatHistoryRead)
async def create_chat_history(user_id:int,chat:schemas.ChatHistoryCreate,db:AsyncSession=Depends(get_db)):
    db_user=await crud.get_user_by_id(db,user_id)
    if db_user is None:
        raise HTTPException(status_code=404,detail="User not found")

    created_chat_history=await crud.create_chat_history(db=db,chat_data=chat,user_id=user_id)
    return created_chat_history

## pdf handling 

@app.post("/users/{user_id}/pdf_upload")
async def upload_pdf_to_server(user_id:int,background_tasks:BackgroundTasks,db:AsyncSession=Depends(get_db),file:UploadFile=File(...)):
    db_user=await crud.get_user_by_id(db,user_id)
    if db_user is None:
        raise HTTPException(status_code=404,detail="User not found")
    if file.filename is None or file.content_type!="application/pdf":
        raise HTTPException(status_code=400,detail="invalid file type")
    file_path=os.path.join(PDF_STORAGE_PATH,file.filename) 
    with open(file_path,"wb") as buffer:
        shutil.copyfileobj(file.file,buffer)

    background_tasks.add_task(ingest_pdf,file_path)
    return {
        "filename":file.filename,
        "detail":"File Uploaded Successfully"
    }
