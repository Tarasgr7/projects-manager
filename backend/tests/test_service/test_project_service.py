import pytest
from ...services.projects_service import is_pm_for_project,get_project_by_id,check_user_pm
from fastapi import HTTPException,status
from ..conftest import *

def test_is_pm_for_project(test_project, test_user):
    db = TestingSessionLocal()
    # Успішний випадок: pm_id користувача == pm_id у проекті
    assert is_pm_for_project(test_project.id, test_user.id, db) == True  
    # Невдалий випадок: неправильний pm_id
    assert is_pm_for_project(test_project.id, 999, db) == False  
    # Невдалий випадок: проект не існує
    assert is_pm_for_project(999, test_user.id, db) == False 




def test_get_project_by_id(test_project):
    db = TestingSessionLocal()

    # 1. Перевіряємо, що проект успішно отримується
    project = get_project_by_id(test_project.id, db)
    assert project is not None
    assert project.id == test_project.id
    assert project.name == "test_project"

def test_check_user_pm():
    check=check_user_pm({'email':"test@email.com", 'id':2,'role':"Project Manager",})
    assert check is None
    with pytest.raises(HTTPException) as e:
        check_user_pm({'role':"Employee"})
    assert e.value.status_code == 403
    assert e.value.detail == "Тільки Project Manager має доступ"


