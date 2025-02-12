import pytest
from sqlalchemy.orm import Session
from ..conftest import *
from fastapi import status,HTTPException
from ...services.tasks_service import (
    check_user_tasks_by_user_id,
    tasks_owner_or_pm,
    check_task_exists,
    get_task_by_id,
    get_all_tasks_for_project,
    unfulfilled_tasks_for_project,
    get_all_tasks_for_employee,
    get_unfulfilled_tasks_for_employee,
    have_unfulfilled_tasks
)
from ...models.tasks_model import Tasks
from ...models.projects_model import Projects
from ...models.users_models import Users
from ...services.utils import raise_error
from ...services.utils import get_db

app.dependency_overrides[get_db]=override_get_db()


# def test_check_user_tasks_by_user_id(test_user, test_task):
#     db= TestingSessionLocal()
#     tasks = check_user_tasks_by_user_id(test_user.id, db)
#     assert len(tasks) > 0
#     assert tasks[0].employee_id == test_user.id

def test_check_user_tasks_by_user_id_not_found():
    db= TestingSessionLocal()
    with pytest.raises(Exception) as exc_info:
        check_user_tasks_by_user_id(999, db)  # Несуществующий ID
    assert "Завдань не знайдено для юзера з id=999" in str(exc_info.value)

def test_tasks_owner_or_pm_as_pm(override_get_user,test_user):
    with pytest.raises(HTTPException) as e:
        tasks_owner_or_pm(override_get_user, test_user.id, None)
    assert e.value.status_code == 500
    assert e.value.detail == "База даних не доступна"  # Дозволений доступ



def test_check_task_exists_not_found():
    db= TestingSessionLocal()
    with pytest.raises(Exception) as exc_info:
        check_task_exists(999, db) 
    assert "Завдання з id=999 не знайдено" in str(exc_info.value)


# def test_get_task_by_id_not_found():
#     db= TestingSessionLocal()
#     with pytest.raises(Exception) as exc_info:
#         get_task_by_id(999, db)  # Несуществующий ID
#     assert "Завдання з id=999 не знайдено" in str(exc_info.value)

# def test_get_all_tasks_for_project(test_project, test_task):
#     db= TestingSessionLocal()
#     tasks = get_all_tasks_for_project(test_project.id, db)
#     assert len(tasks) > 0
#     assert tasks[0].project_id == test_project.id

# def test_get_all_tasks_for_project_not_found():
#     db= TestingSessionLocal()
#     with pytest.raises(Exception) as exc_info:
#         get_all_tasks_for_project(999, db)  # Несуществующий ID
#     assert "Завдань не знайдено для проекту з id=999" in str(exc_info.value)

# def test_unfulfilled_tasks_for_project(test_project, test_task):
#     db= TestingSessionLocal()
#     tasks = unfulfilled_tasks_for_project(test_project.id, db)
#     assert len(tasks) > 0
#     assert tasks[0].project_id == test_project.id

# def test_unfulfilled_tasks_for_project_not_found():
#     db= TestingSessionLocal()
#     with pytest.raises(Exception) as exc_info:
#         unfulfilled_tasks_for_project(999, db)  # Несуществующий ID
#     assert "Завдань не знайдено для проекту з id=999" in str(exc_info.value)

# def test_get_all_tasks_for_employee(test_user, test_task):
#     db= TestingSessionLocal()
#     tasks = get_all_tasks_for_employee(test_user.id, db)
#     assert len(tasks) > 0
#     assert tasks[0].employee_id == test_user.id

# def test_get_all_tasks_for_employee_not_found():
#     db= TestingSessionLocal()
#     with pytest.raises(Exception) as exc_info:
#         get_all_tasks_for_employee(999, db)  # Несуществующий ID
#     assert "Завдань не знайдено для юзера з id=999" in str(exc_info.value)

# def test_get_unfulfilled_tasks_for_employee(test_user, test_task):
#     db= TestingSessionLocal()
#     tasks = get_unfulfilled_tasks_for_employee(test_user.id, db)
#     assert len(tasks) > 0
#     assert tasks[0].employee_id == test_user.id

# def test_get_unfulfilled_tasks_for_employee_not_found():
#     db= TestingSessionLocal()
#     with pytest.raises(Exception) as exc_info:
#         get_unfulfilled_tasks_for_employee(999, db)  # Несуществующий ID
#     assert "Не виконаних завдань не знайдено для юзера з id=999" in str(exc_info.value)

# def test_have_unfulfilled_tasks_true(test_user, test_task):
#     db= TestingSessionLocal()
#     assert have_unfulfilled_tasks(test_user.id, db) is True

# def test_have_unfulfilled_tasks_false():
#     db= TestingSessionLocal()
#     assert have_unfulfilled_tasks(999, db) is False  # Несуществующий ID
