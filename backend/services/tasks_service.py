from fastapi import status, HTTPException
from ..models.tasks_model import Tasks
from ..dependencies import logger
from ..services.projects_service import is_pm_for_project
from .utils import raise_error
from ..models.users_models import Users
from ..models.projects_model import Projects
from ..models.employee_model import Employee
from ..models.tasks_model import Tasks
from ..services.tasks_service import *
from enum import Enum


def check_user_tasks_by_user_id(user_id,db):
  tasks = db.query(Tasks).filter(Tasks.employee_id == user_id).all()
  if not tasks:
    raise_error(f"Завдань не знайдено для юзера з id={user_id}", status.HTTP_404_NOT_FOUND)
  return tasks

def tasks_owner_or_pm(user,user_id,db):
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

