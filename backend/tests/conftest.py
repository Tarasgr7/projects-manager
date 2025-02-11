import os
import pytest
from sqlalchemy import create_engine,text
from sqlalchemy.orm import scoped_session, sessionmaker
from ..main import app
from ..dependencies import Base
from ..models.users_models import Users,Steaks, Language
from ..models.projects_model import Projects
from fastapi.testclient import TestClient
from ..services.utils import bcrypt_context



def get_sync_test_db_url():
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    test_db = os.getenv("TEST_DB_NAME")
    return f"postgresql://postgres:{password}@localhost:5432/{test_db}"


TEST_DB_URI = get_sync_test_db_url()
engine = create_engine(TEST_DB_URI)
TestingSessionLocal = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)
Base.metadata.create_all(bind=engine)

def override_get_db():
  db=TestingSessionLocal()
  try:
    yield db
  finally:
    db.close()

def override_get_user():
   return {'email':"test@email.com", 'id':2,'role':"Project Manager",}


client=TestClient(app)


@pytest.fixture
def test_user():
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
   db= TestingSessionLocal()
   db.add(user)
   db.commit()
   yield user
   with engine.connect() as connection:
        connection.execute(text("DELETE FROM users;"))
        connection.commit()


@pytest.fixture
def test_project(test_user):
   project=Projects(
      pm_id=test_user.id,
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