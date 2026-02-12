from noteapp.test.utils import *
from noteapp.router.note import get_db, get_current_user
from fastapi import status

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

def test_get_all_notes_with_search(test_note):
    response = client.get('/notes/?search="test"')
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