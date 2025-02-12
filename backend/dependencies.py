import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("service")

# Якщо через докер
def get_sync_db_url():
    user = os.getenv("DOCKER_USER")
    password = os.getenv("DOCKER_PASSWORD")
    server=os.getenv("DOCKER_SERVER")
    db = os.getenv("DOCKER_NAME")
    logger.info(f"postgresql://{user}:{password}@{server}:5432/{db}")
    return f"postgresql://{user}:{password}@{server}:5432/{db}"


#Якщо через локальну БД
# def get_sync_db_url():
#     user = os.getenv("DB_USER")
#     password = os.getenv("DB_PASSWORD")
#     server=os.getenv("DB_SERVER")
#     db = os.getenv("DB_NAME")
#     logger.info(f"USERNAME:{user}")
#     return f"postgresql://{user}:{password}@{server}:5432/{db}""



# Отримуємо URL бази даних із .env (або ставимо дефолтне значення)
DATABASE_URL = get_sync_db_url()

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# from .models.users_models import Users
# from .models.projects_model import Projects

