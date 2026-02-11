from fastapi import FastAPI
from .models import Base, Users
from .database import engine
from .router import note, auth
from sqlalchemy.orm import Session
from passlib.context import CryptContext

app = FastAPI()

Base.metadata.create_all(bind=engine)
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
@app.get('/')
async def test():
    return {'status':'healthy'}

app.include_router(note.router) 
app.include_router(auth.router)