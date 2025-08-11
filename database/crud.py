from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,delete
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
        db_user.hashed_password=hashed_passwd
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

async def create_chat_history(db: AsyncSession, chat_data: schemas.ChatHistoryCreate, user_id: int) -> models.ChatHistory:
    db_chat = models.ChatHistory(**chat_data.model_dump(), user_id=user_id)
    db.add(db_chat)
    await db.commit()
    await db.refresh(db_chat)
    return db_chat


