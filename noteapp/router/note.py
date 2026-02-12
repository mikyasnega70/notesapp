from fastapi import APIRouter, HTTPException, Depends, Path, Query
from starlette import status
from pydantic import BaseModel
from sqlalchemy import or_, select
from sqlalchemy.orm import Session
from typing import Annotated, Optional, Generic, TypeVar
from datetime import datetime
from .auth import get_current_user
from ..database import sessionlocal
from ..models import Notes, Users
import markdown
# from dataclasses import dataclass

router = APIRouter(
    prefix='/notes',
    tags=['notes']
)

class NoteCreate(BaseModel):
    title:str
    content:str
    tags:Optional[list[str]] 

class NoteUpdate(BaseModel):
    title:Optional[str]
    content:Optional[str]
    tags:Optional[list[str]]

class NoteResponse(BaseModel):
    id:int
    title:str
    content:str
    tags:Optional[list[str]]
    created_at:datetime
    updated_at:Optional[datetime]
    owner_id:Optional[int]

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    total:int
    limit:int
    offset:int
    items:list[T]

# @dataclass
# class pagination:
#     limit:int=Query(10, ge=1, le=100)
#     offset:int=Query(0, ge=0)

def get_db():
    db = sessionlocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

user_dependency = Annotated[dict, Depends(get_current_user)]

@router.get('/', status_code=status.HTTP_200_OK, response_model=PaginatedResponse[NoteResponse])
async def get_all_notes(db:db_dependency, user:user_dependency, search:Optional[str]=Query(default=None, min_length=3), limit:Optional[int]=Query(default=10, ge=1,le=100), offset:Optional[int]=Query(default=0, ge=0)):
    user = db.query(Users).filter(Users.username == user.get('username'), Users.id == user.get('id')).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='can not authenticate user')
    
    if search:
        # note_model = db.query(Notes).filter(or_(Notes.title.contains(search))).all()
        note_model = db.query(Notes).filter(or_(Notes.title.ilike(f"%{search}%"), Notes.content.ilike(f"%{search}%"))).filter(Notes.is_deleted == False).filter(Notes.owner_id == user.id).offset(offset).limit(limit).all()
        if not note_model:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='note not found')
        total = db.query(Notes).filter(or_(Notes.title.ilike(f"%{search}%"), Notes.content.ilike(f"%{search}%"))).filter(Notes.is_deleted == False).filter(Notes.owner_id == user.id).count()
        return PaginatedResponse(total=total, limit=limit, offset=offset, items=note_model)
    
    note_model = db.query(Notes).filter(Notes.is_deleted == False, Notes.owner_id == user.id).all()
    total = db.query(Notes).filter(Notes.is_deleted == False, Notes.owner_id == user.id).count()
    return PaginatedResponse(total=total, limit=limit, offset=offset, items=note_model)

@router.get('/{note_id}', status_code=status.HTTP_200_OK, response_model=NoteResponse)
async def get_note(db:db_dependency, user:user_dependency, note_id:int=Path(gt=0)):
    user = db.query(Users).filter(Users.username == user.get('username'), Users.id == user.get('id')).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='can not authenticate user')
    
    note_model = db.query(Notes).filter(Notes.id == note_id, Notes.is_deleted == False, Notes.owner_id == user.id).first()
    if not note_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='note not found')
    
    return note_model

@router.post('/create', status_code=status.HTTP_201_CREATED)
async def create_note(db:db_dependency, user:user_dependency, createfield:NoteCreate):
    user = db.query(Users).filter(Users.username == user.get('username'), Users.id == user.get('id')).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='can not authenticate user')
    
    note_model = Notes(**createfield.model_dump(), owner_id=user.id)

    db.add(note_model)
    db.commit()

@router.put('/{note_id}', status_code=status.HTTP_204_NO_CONTENT)
async def update_note(db:db_dependency, user:user_dependency, updatefield:NoteUpdate, note_id:int=Path(gt=0)):
    user = db.query(Users).filter(Users.username == user.get('username'), Users.id == user.get('id')).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='can not authenticate user')
    
    note_model = db.query(Notes).filter(Notes.id == note_id, Notes.is_deleted == False, Notes.owner_id == user.id).first()
    if not note_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='note not found')
    note_model.title = updatefield.title if updatefield.title else note_model.title
    note_model.content = updatefield.content if updatefield.content else note_model.content
    note_model.tags = updatefield.tags if updatefield.tags else note_model.tags

    db.add(note_model)
    db.commit()

@router.delete('/{note_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(db:db_dependency, user:user_dependency, note_id:int=Path(gt=0)):
    user = db.query(Users).filter(Users.username == user.get('username'), Users.id == user.get('id')).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='can not authenticate user')
    
    note_model = db.query(Notes).filter(Notes.id == note_id, Notes.is_deleted == False, Notes.owner_id == user.id).first()
    if not note_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='note not found')
    note_model.is_deleted = True
    db.add(note_model)
    db.commit()

@router.patch('/{note_id}/restore', status_code=status.HTTP_204_NO_CONTENT)
async def restore_note(db:db_dependency, user:user_dependency, note_id:int=Path(gt=0)):
    user = db.query(Users).filter(Users.username == user.get('username'), Users.id == user.get('id')).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='can not authenticate user')
    
    note_model = db.query(Notes).filter(Notes.id == note_id, Notes.is_deleted==True, Notes.owner_id == user.id).first()
    if not note_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='note not found')
    
    note_model.is_deleted = False
    db.add(note_model)
    db.commit()

@router.get('/{note_id}/rendered_content', status_code=status.HTTP_200_OK)
async def render_content(db:db_dependency, user:user_dependency, note_id:int=Path(gt=0)):
    user = db.query(Users).filter(Users.username == user.get('username'), Users.id == user.get('id')).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='can not authenticate user')
    
    note_model = db.scalars(select(Notes).where(Notes.id == note_id, Notes.is_deleted== False, Notes.owner_id == user.id)).first()
    if not note_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='note not found')
    content = markdown.markdown(note_model.title)
    content1 = markdown.markdown(note_model.content)
    
    return {'title':content, 'content':content1}

