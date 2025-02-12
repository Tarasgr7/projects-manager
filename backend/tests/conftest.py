import os
import pytest
from sqlalchemy import create_engine,text
from sqlalchemy.orm import scoped_session, sessionmaker
from ..main import app
from ..dependencies import Base
from ..models.users_models import Users,Steaks, Language
from ..models.tasks_model import Tasks
from ..models.projects_model import Projects
from fastapi.testclient import TestClient
from ..services.utils import bcrypt_context
from ..services.utils import get_db
from ..services.auth_service import get_current_user



def get_sync_test_db_url():
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    test_db = os.getenv("TEST_DB_NAME")
    return f"postgresql://postgres:{password}@localhost:5432/{test_db}"


TEST_DB_URI = get_sync_test_db_url()
engine = create_engine(TEST_DB_URI)
TestingSessionLocal =sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

def override_get_db():
   db=TestingSessionLocal()
   try:
      yield db
      db.commit()
   except Exception:
      db.rollback()
      raise
   finally:
      db.close()

@pytest.fixture
def override_get_user():
    return {"email": "test@email.com", "id": 1, "role": "Project Manager"}







@pytest.fixture(scope="function")
def db_session():
    """Фікстура для створення та очищення тестової сесії"""
    db = TestingSessionLocal()

    try:
        yield db  # Віддаємо сесію тестам
    except Exception:
        db.rollback()  # Відкат транзакції, якщо сталася помилка
        raise
    finally:
        db.close()  # Закриваємо сесію після тесту

@pytest.fixture(autouse=True)
def rollback_after_test(db_session):
    """Автоматично відкатує транзакцію після кожного тесту"""
    yield
    db_session.rollback()


client=TestClient(app)


@pytest.fixture
def test_user_pm(db_session):
   db=TestingSessionLocal()
   try:
      db.rollback()
      db.execute(text("DELETE FROM users WHERE email='test@email.com';"))
      db.execute(text("DELETE FROM tasks WHERE pm_id IN (SELECT id FROM users WHERE email='test@email.com');"))
      db.execute(text("DELETE FROM projects WHERE pm_id IN (SELECT id FROM users WHERE email='test1@email.com');"))
      db.commit()
      user=Users(
         email="test@email.com",
         first_name="test",
         last_name="test",
         hashed_password=bcrypt_context.hash("test"),
         username="test",
         role="Project Manager",
         project=None,
         is_active=True
      )
      db.add(user)
      db.commit()
      yield user
   finally:
      db.rollback()
      db.execute(text("DELETE FROM users WHERE email='test@email.com';"))
      db.execute(text("DELETE FROM tasks WHERE pm_id IN (SELECT id FROM users WHERE email='test@email.com');"))
      db.execute(text("DELETE FROM projects WHERE pm_id IN (SELECT id FROM users WHERE email='test@email.com');"))
      db.commit()
      db.close()






@pytest.fixture
def test_project(test_user_pm):
   project=Projects(
      pm_id=test_user_pm.id,
      name="test_project",
      descriptions="test_project_description"
   )
   db=TestingSessionLocal()
   db.add(project)
   db.commit()
   yield project
   with engine.connect() as connection:
        connection.execute(text("DELETE FROM projects;"))
        connection.commit()

@pytest.fixture
def test_user(db_session):
   db=TestingSessionLocal()
   try:
      db.rollback()
      db.execute(text("DELETE FROM tasks WHERE employee_id IN (SELECT id FROM users WHERE email='test1@email.com');"))
        # Тепер можна видаляти користувача
      db.execute(text("DELETE FROM users WHERE email='test1@email.com';"))
      db.commit()
      user=Users(
         email="test1@email.com",
         first_name="test1",
         last_name="test1",
         hashed_password=bcrypt_context.hash("test"),
         username="tes1t",
         role="Backend Developer",
         project=None,
         is_active=True
      )
      db.add(user)
      db.commit()
      yield user
   finally:
      db.rollback()
      db.execute(text("DELETE FROM users WHERE email='test1@email.com';"))
      db.execute(text("DELETE FROM tasks WHERE employee_id IN (SELECT id FROM users WHERE email='test1@email.com');"))
        
        # Тепер можна видаляти користувача
      db.execute(text("DELETE FROM users WHERE email='test1@email.com';"))
      db.commit()
      db.close()


@pytest.fixture
def test_task(test_user,test_user_pm,test_project):
   task=Tasks(
      title="test_task",
      description="test_task_description",
      project_id=test_project.id,
      employee_id=test_user.id,
      pm_id=test_user_pm.id
   )
   db=TestingSessionLocal()
   db.add(task)
   db.commit()
   yield task
   with engine.connect() as connection:
        connection.execute(text("DELETE FROM steaks;"))
        connection.commit()



