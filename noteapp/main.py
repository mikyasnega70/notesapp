from fastapi import FastAPI, status
from .models import Base, Users
from .database import engine
from .router import note, auth
from sqlalchemy.orm import Session
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

app = FastAPI()

Base.metadata.create_all(bind=engine)
app.mount('/static', StaticFiles(directory='noteapp/static'), name='static')

@app.get('/')
async def test():
    response = RedirectResponse(url='/notes/home-page/', status_code=status.HTTP_302_FOUND)
    return response

app.include_router(note.router) 
app.include_router(auth.router)