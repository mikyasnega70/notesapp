from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from noteapp.main import app
from noteapp.models import Notes, Users
from noteapp.router.auth import bcrypt_context
from noteapp.database import Base
import pytest

SQLALCHEMY_DATABASE_URL = 'sqlite:///./test.db'
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread':False}, poolclass=StaticPool)

Testsessionlocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

client = TestClient(app)

Base.metadata.create_all(bind=engine)

def override_get_db():
    db = Testsessionlocal()
    try:
        yield db
    finally:
        db.close()

def override_get_current_user():
    return {'username':'testuser', 'id':1, 'role':'admin'}

@pytest.fixture
def test_note():
    note = Notes(
        title='Test Note',
        content='This is a test note.',
        tags=['test', 'note'],
        owner_id=1
    )
    db = Testsessionlocal()
    db.add(note)
    db.commit()
    yield note
    with engine.connect() as conn:
        conn.execute(text('delete from notes;'))
        conn.commit()

@pytest.fixture
def test_user():
    user = Users(
        username='testuser',
        email='testuser@gmail.com',
        name='Test User',
        hashed_password=bcrypt_context.hash('testpassword'),
        role='admin' 
    )
    db = Testsessionlocal()
    db.add(user)
    db.commit()
    yield user
    with engine.connect() as conn:
        conn.execute(text('delete from users;'))
        conn.commit()
