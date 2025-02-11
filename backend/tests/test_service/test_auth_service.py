import pytest
from ...services.utils import get_db
from datetime  import timedelta
from ...services.auth_service import authenticate_user,create_access_token,get_current_user,check_positions
from ...dependencies import SECRET_KEY,ALGORITHM
from ..conftest import *
from jose import jwt
from fastapi import HTTPException

app.dependency_overrides[get_db]=override_get_db

def test_authenticate_user(test_user):
    db = TestingSessionLocal()

    authenticated_user = authenticate_user(test_user.email, 'test', db)
    assert authenticated_user is not None
    assert authenticated_user.email == test_user.email

    non_existent_user = authenticate_user('WrongUserName', 'test', db)
    assert non_existent_user is False

    wrong_password_user = authenticate_user(test_user.email, 'wrongpassword', db)
    assert wrong_password_user is False

def test_create_access_token():
    email="test@email.com"
    id=1
    role="Project Manager"
    is_active=True
    expires_delta=timedelta(days=1)
    token=create_access_token(email,id,role,is_active,expires_delta)
    payload=jwt.decode(token,SECRET_KEY, ALGORITHM)
    assert payload['sub']==email
    assert payload['id']==id
    assert payload['role']==role.strip()
    assert payload['status']==is_active
    
@pytest.mark.asyncio#+
async def test_get_current_user_valid_token():#+
    encode = {#+
        'sub': 'test@email.com',#+
        'id': 1,#+
        'role': 'Project Manager',
        "status": True
    }
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)#+
    user = await get_current_user(token=token)
    assert user == {'email': 'test@email.com', 'id': 1, 'role': 'Project Manager'}#+

def test_check_position():
    assert check_positions("Software Engineer")==True
    with pytest.raises(HTTPException) as exc_info:  # Очікуємо помилку
        check_positions("Chef")  # Викликаємо функцію з некоректною позицією
    assert exc_info.value.status_code == 422  # Перевіряємо статус-код
    assert exc_info.value.detail == "Invalid position"
