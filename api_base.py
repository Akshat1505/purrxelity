from fastapi import BackgroundTasks, Depends, FastAPI, File,Path,Query,HTTPException, UploadFile,status
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse,StreamingResponse
from sse_starlette.sse import EventSourceResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from langchain_core.messages import AIMessage, HumanMessage
from typing import Any, List, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import user
from sqlalchemy.future import select
from deep_research.supervisor_subgraph import supervisor_graph
from rag_processing import ingest_pdf
import schemas
from search_main import stream_chat_response,get_chat_response
from database.database import engine,get_db
from database import models,crud,schemas
from datetime import datetime
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
# random_thread_id=uuid.uuid4()
PDF_STORAGE_PATH="pdf_storage"
os.makedirs(PDF_STORAGE_PATH,exist_ok=True)

@app.get('/')
async def root():
    return "Welcome to Purrxelity API Dashboard"

## text endpoints

@app.post('/chat') # SSE or websocket for streaming
async def chat(user_input:BasicChat,user_id:int,db:AsyncSession=Depends(get_db)):
    db_user=await crud.get_user_by_id(db,user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404,detail="User not found")

    formatted_message=[
        {"role":"user","content":"","timestamp":datetime.now().isoformat()},
        {"role":"assistant","content":"","timestamp":None}
    ]
    formatted_message[0]["content"]=user_input.input
    thread_id=user_input.thread_id or str(uuid.uuid4())
    # result=main_graph.invoke({
    #     "messages":HumanMessage(content=user_input.input)
    # },{"configurable":{"thread_id":thread_id}}
    # )["messages"][-1].content #not safe
    result=await get_chat_response(user_input.input,thread_id)
    formatted_message[1]["content"]=result
    formatted_message[1]["timestamp"]=datetime.now().isoformat()
    await add_message_to_chat(user_id,thread_id,formatted_message,db)
    return {
        "message":result,
        "thread_id":thread_id
    }

    
@app.post('/chat/stream')
async def chat_streaming(user_input:BasicChat,user_id:int,db:AsyncSession=Depends(get_db)):
    db_user = await crud.get_user_by_id(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    thread_id = user_input.thread_id or str(uuid.uuid4())
    return StreamingResponse(
        stream_chat_response(user_input.input,thread_id),
        media_type="text/plain"
    )

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

@app.post("/login",response_model=schemas.UserRead)
async def login_for_access(user_cred:schemas.LoginRequest,db:AsyncSession=Depends(get_db)):
    user=await crud.autheticate_user(db,email=user_cred.email,password=user_cred.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate":"Bearer"},
        )
    return user
## user chat crud

@app.post("/users/{user_id}/chats",response_model=schemas.ChatHistoryRead)
async def create_chat_history(user_id:int,chat_data:schemas.ChatHistoryCreate,db:AsyncSession=Depends(get_db)):
    db_user=await crud.get_user_by_id(db,user_id)
    if db_user is None:
        raise HTTPException(status_code=404,detail="User not found")
    
    thread_id=str(uuid.uuid4())
    created_chat_history=await crud.create_chat_history(db,chat_data,user_id,thread_id)
    return created_chat_history

@app.get("/users/{user_id}/chats",response_model=List[schemas.ChatHistoryRead])
async def get_chat_history_by_user(user_id:int,db:AsyncSession=Depends(get_db)):
    db_user=await crud.get_user_by_id(db,user_id)
    if db_user is None:
        raise HTTPException(status_code=404,detail="User not found")
    
    returned_chat_history=await crud.get_chat_history(db,user_id)
    return returned_chat_history

@app.delete("/users/{user_id}/chats",response_model=bool)
async def delete_user_chat(user_id:int,chat_thread_id:str,db:AsyncSession=Depends(get_db)):
    db_user=await crud.get_user_by_id(db,user_id)
    if db_user is None:
        raise HTTPException(status_code=404,detail="User not found")
    
    result=await crud.delete_chat_history(user_id,db,chat_thread_id)
    return result

#redundant ?
# @app.put("/users/{user_id}/chats/{thread_id}")
async def add_message_to_chat(user_id:int,thread_id:str,new_messages:List[Dict[str,Any]],db:AsyncSession=Depends(get_db)):
    db_user=await crud.get_user_by_id(db,user_id)
    if db_user is None:
        raise HTTPException(status_code=404,detail="User not found")
    # await crud.append_message_to_chat(user_id,thread_id,new_messages,db) 
    updated_chat=await crud.append_message_to_chat(user_id,thread_id,new_messages,db)
    if not updated_chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    # return updated_chat

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


