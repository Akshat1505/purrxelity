from sys import thread_info
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,delete
from sqlalchemy.orm import attributes
from typing import List,Optional,Sequence
from . import models,schemas
from passlib.context import CryptContext

pwd_context=CryptContext(schemes=["bcrypt"],deprecated="auto")

def get_passwd_hash(password:str) -> str:
    return pwd_context.hash(password)

async def create_user(db:AsyncSession,user:schemas.UserCreate) -> models.User:
    hashed_passwd=get_passwd_hash(user.password)
    db_user=models.User(email=user.email,hashed_password=hashed_passwd)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def get_user_by_id(db:AsyncSession,user_id:int) -> Optional[models.User]:
    result = await db.execute(select(models.User).where(models.User.id==user_id))
    return result.scalar_one_or_none()

async def get_user_by_email(db:AsyncSession,email:str) -> Optional[models.User]:
    result = await db.execute(select(models.User).where(models.User.email==email))
    return result.scalar_one_or_none()

async def get_users(db:AsyncSession,skip:int=0,limit:int=100) -> Sequence[models.User]:
    result = await db.execute(select(models.User).offset(skip).limit(limit))
    return result.scalars().all()

async def update_user(db:AsyncSession,user_id:int,updated_user:schemas.UserUpdate)->Optional[models.User]:
    db_user=await get_user_by_id(db,user_id)
    if not db_user:
        return None
    
    updated_data=updated_user.model_dump(exclude_unset=True)
    if "password" in updated_data:
        hashed_passwd=get_passwd_hash(updated_data["password"])
        db_user.hashed_password=hashed_passwd #works
        del updated_data["password"]

    for key,value in updated_data.items():
        setattr(db_user,key,value)
    
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def delete_user(db: AsyncSession, user_id: int) -> bool:
    stmt = delete(models.User).where(models.User.id == user_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0

async def create_chat_history(db: AsyncSession, chat_data: schemas.ChatHistoryCreate, user_id: int,thread_id:str) -> models.ChatHistory:
    db_chat = models.ChatHistory(
        thread_id=thread_id,
        messages=chat_data.messages,
        user_id=user_id
    )
    db.add(db_chat)
    await db.commit()
    await db.refresh(db_chat)
    return db_chat

async def get_chat_history(db:AsyncSession,user_id:int) -> Sequence[models.ChatHistory]:
    stmt = await db.execute(select(models.ChatHistory).where(models.ChatHistory.user_id==user_id))
    return stmt.scalars().all()

async def delete_chat_history(user_id:int,db:AsyncSession,chat_thread_id:str) -> bool:
    stmt=(
        delete(models.ChatHistory)
        .where(
            models.ChatHistory.thread_id==chat_thread_id,
            models.ChatHistory.user_id==user_id
        )
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0 

async def append_message_to_chat(user_id:int,thread_id:str,new_messages:List[dict],db:AsyncSession) -> Optional[models.ChatHistory]:
    
    stmt=select(models.ChatHistory).where(
        models.ChatHistory.user_id==user_id,
        models.ChatHistory.thread_id==thread_id
    )
    result=await db.execute(stmt)
    chat=result.scalar_one_or_none()

    if not chat: return None
    attributes.flag_modified(chat, "messages")
    chat.messages.extend(new_messages)
    await db.commit()
    await db.refresh(chat)
    return chat
