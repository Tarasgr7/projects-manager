from fastapi import status
from ..models.tasks_model import Tasks
from ..dependencies import logger
from .utils import raise_error
from ..models.tasks_model import Tasks
from ..services.tasks_service import *



def check_user_tasks_by_user_id(user_id,db):
  tasks = db.query(Tasks).filter(Tasks.employee_id == user_id).all()
  if not tasks:
    raise_error(f"Завдань не знайдено для юзера з id={user_id}", status.HTTP_404_NOT_FOUND)
  return tasks

def tasks_owner_or_pm(user,user_id,db):
  if db == None:
    raise_error("База даних не доступна", status.HTTP_500_INTERNAL_SERVER_ERROR)
  if user.get('role')!="Project Manager" and user.get("id")!=user_id:
    raise_error("You are not allowed to check tasks",status.HTTP_405_METHOD_NOT_ALLOWED)

def check_task_exists(task_id,db):
  task=db.query(Tasks).filter(Tasks.id==task_id).first()
  if not task:
    raise_error(f"Завдання з id={task_id} не знайдено", status.HTTP_404_NOT_FOUND)

def get_task_by_id(task_id,db):
  task=db.query(Tasks).filter(Tasks.id==task_id).first()
  if not task:
    raise_error(f"Завдання з id={task_id} не знайдено", status.HTTP_404_NOT_FOUND)
  return task


def get_all_tasks_for_project(project_id,db):
  tasks = db.query(Tasks).filter(Tasks.project_id == project_id).all()
  if not tasks:
    raise_error(f"Завдань не знайдено для проекту з id={project_id}", status.HTTP_404_NOT_FOUND)
  return tasks

def unfulfilled_tasks_for_project(project_id,db):
  tasks = db.query(Tasks).filter(Tasks.project_id == project_id, Tasks.status == False).all()
  
  if not tasks:
    raise_error(f"Завдань не знайдено для проекту з id={project_id}, не виконаних", status.HTTP_404_NOT_FOUND)
  return tasks

def get_all_tasks_for_employee(employee_id,db):
  tasks=db.query(Tasks).filter(Tasks.employee_id==employee_id).all()
  if not tasks:
    raise_error(f"Завдань не знайдено для юзера з id={employee_id}", status.HTTP_404_NOT_FOUND)
  return tasks

def get_unfulfilled_tasks_for_employee(employee_id,db):
  tasks=db.query(Tasks).filter(Tasks.employee_id==employee_id, Tasks.status==False).all()
  if not tasks:
    raise_error(f"Не виконаних завдань не знайдено для юзера з id={employee_id}", status.HTTP_404_NOT_FOUND)
  return tasks

def have_unfulfilled_tasks(user_id,db):
  tasks = db.query(Tasks).filter(Tasks.employee_id == user_id, Tasks.status == False).first()
  if tasks:
    return True
  return False
