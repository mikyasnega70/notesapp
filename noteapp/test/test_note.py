from noteapp.test.utils import *
from noteapp.router.note import get_db, get_current_user
from fastapi import status

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

def test_get_all_notes(test_note, test_user):
    response = client.get('/notes/')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        'total':1,
        'limit':10,
        'offset':0,
        'items':[
            {
                'id':test_note.id,
                'title':'Test Note',
                'content':'This is a test note.',
                'tags':['test', 'note'],
                'created_at':test_note.created_at.isoformat(),
                'updated_at':test_note.updated_at.isoformat() if test_note.updated_at else None,
                'owner_id':1
            }
        ]
    }
    

def test_get_all_notes_with_search(test_note, test_user):
    response = client.get('/notes/?search=test')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        'total':1,
        'limit':10,
        'offset':0,
        'items':[{
            'id':test_note.id,
            'title':'Test Note',
            'content':'This is a test note.',
            'tags':['test', 'note'],
            'created_at':test_note.created_at.isoformat(),
            'updated_at':test_note.updated_at.isoformat() if test_note.updated_at else None,
            'owner_id':1
        }]
    }

def test_get_all_note_invalid_search(test_note, test_user):
    response = client.get('/notes/?search=error')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail':'note not found'}

def test_get_note(test_note, test_user):
    response = client.get('/notes/1')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        'id':test_note.id,
        'title':'Test Note',
        'content': 'This is a test note.',
        'tags': ['test', 'note'],
        'created_at':test_note.created_at.isoformat(),
        'updated_at':test_note.updated_at.isoformat() if test_note.updated_at else None,
        'owner_id':1
    }

def test_get_note_invalid(test_note, test_user):
    response = client.get('/notes/2')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail':'note not found'}

def test_create_note(test_note, test_user):
    request_test = {
        'title':'new note',
        'content':'new content',
        'tags':['new']
    }

    response = client.post('/notes/create', json=request_test)
    assert response.status_code == status.HTTP_201_CREATED

    db = Testsessionlocal()
    model = db.query(Notes).filter(Notes.id == 2).first()
    assert model.title == request_test.get('title')
    assert model.content == request_test.get('content')
    assert model.tags == request_test.get('tags')

def test_update_note(test_note, test_user):
    request_test = {
        'title':'update note',
        'content':'',
        'tags':[]
    }

    response = client.put('/notes/1', json=request_test)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = Testsessionlocal()
    model = db.query(Notes).filter(Notes.id == test_note.id).first()
    assert model.title == request_test.get('title')
    assert model.content == test_note.content

def test_update_note_invalid(test_note, test_user):
    request_test = {
        'title':'update note',
        'content':'',
        'tags':[]
    }

    response = client.put('/notes/2', json=request_test)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail':'note not found'}

def test_delete_note(test_note, test_user):
    response = client.delete('/notes/1')
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = Testsessionlocal()
    model = db.query(Notes).filter(Notes.id == 1).first()
    assert model.is_deleted == True

def test_delete_note_invalid(test_note, test_user):
    response = client.delete('/notes/2')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail':'note not found'}

def test_restore_note(test_note, test_user):
    db = Testsessionlocal()
    note = db.query(Notes).filter(Notes.id == test_note.id).first()
    note.is_deleted = True
    db.commit()

    response = client.patch('/notes/1/restore')
    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_render_content(test_note, test_user):
    response = client.get('/notes/1/rendered_content')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        'title':'<p>Test Note</p>',
        'content':'<p>This is a test note.</p>'
    }
