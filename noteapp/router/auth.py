from fastapi import APIRouter, HTTPException, Depends
from starlette import status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from typing import Annotated
from passlib.context import CryptContext
from ..database import sessionlocal
from ..models import Users


router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

def get_db():
    db = sessionlocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

class UserCreate(BaseModel):
    username:str
    email:EmailStr
    name:str
    password:str
    role:str

@router.post('/create', status_code=status.HTTP_201_CREATED)
async def create_user(db:db_dependency, new_user:UserCreate):
    user_model = Users(
        username=new_user.username,
        email=new_user.email,
        name=new_user.name,
        hashed_password=bcrypt_context.hash(new_user.password),
        role=new_user.role
    )

    db.add(user_model)
    db.commit()
