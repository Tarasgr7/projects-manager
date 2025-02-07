from ..models.projects_model import Projects
from ..models.users_models import Users
from fastapi import status,HTTPException
from ..dependencies import  logger
from .utils import raise_error

#Перевірка чи юзер є продакт менеджером проекту проекту
def is_pm_for_project(projects_id:int, pm_id:int,db):
  project = db.query(Projects).filter(Projects.id == projects_id, Projects.pm_id == pm_id).first()
  if not project:
    return False
  return True


#Виведення Помилок



#Перевірка існування проектів
def check_project_exists(project_id,db):
    project=db.query(Projects).filter(Projects.id==project_id).first()
    if not project:
        logger.error("Project is not found",project_id)
        raise_error("Проект з таким ID не знайдений", status.HTTP_404_NOT_FOUND)


#Перевірка пошук усіх співробітників проекту
def get_employee_by_project_id(project_id,db):
    users=db.query(Users).filter(Users.project==project_id).all()
    if not users:
        logger.error("Співробітники не знайдені")
        raise_error("Співробітники не знайдені", status.HTTP_404_NOT_FOUND)
    return users


#Пошук проекту по ID
def get_project_by_id(project_id,db):
    project=db.query(Projects).filter(Projects.id==project_id).first()
    if not project:
      logger.error("Project is not found", project_id)
      raise_error("Проект з таким ID не знайдений", status.HTTP_404_NOT_FOUND)
    return project


#Перевірка чи юзер є продакт менеджером
def check_user_pm(user):
    if not user or user.get("role") != "Project Manager":
        raise_error("Тільки Project Manager має доступ", status.HTTP_403_FORBIDDEN)



#Пошук юзера по ID
def get_user_by_id(user_id,db):
    user=db.query(Users).filter(Users.id==user_id).first()
    if not user:
        
        raise_error("Користувач з таким ID не знайдений", status.HTTP_404_NOT_FOUND)
    return user