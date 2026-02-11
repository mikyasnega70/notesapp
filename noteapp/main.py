from fastapi import FastAPI
from .models import Base
from .database import engine
from .router import note, auth

app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.get('/')
async def test():
    return {'status':'healthy'}

app.include_router(note.router) 
app.include_router(auth.router)