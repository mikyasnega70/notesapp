from fastapi import APIRouter, HTTPException, Depends
from starlette import status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from typing import Annotated
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt, JWTError
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from ..database import sessionlocal
from ..models import Users
import os


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

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
load_dotenv()
SECRET_KEY=os.getenv("SECRET_KEY")
ALGORITHM = 'HS256'

class UserCreate(BaseModel):
    username:str
    email:EmailStr
    name:str
    password:str
    role:str

class Token(BaseModel):
    access_token:str
    token_type:str


def authenticate_user(username:str, password:str, db:Session):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

def create_access_token(username:str, id:int, role:str, expires:timedelta):
    to_encode = {'sub':username, 'id':id, 'role':role}
    expire = datetime.now(timezone.utc) + expires
    to_encode.update({'exp':expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token

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

@router.post('/token', response_model=Token)
async def login_access(db:db_dependency, formdata:Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(formdata.username, formdata.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='can not authenticate user')
    
    token = create_access_token(user.username, user.id, user.role, timedelta(minutes=20))
    return {'access_token':token, 'token_type':'bearer'}

