from fastapi import APIRouter, status
from ..models.tasks_model import Tasks
from ..dependencies import logger
from ..services.utils import user_dependency, db_dependency
from ..services.tasks_service import *
from ..services.projects_service import *
from ..schemas.tasks_schema import TaskSchema,TaskUpdateSchema
from ..services.user_service import *


router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/add_task/{project_id}/{user_id}",status_code=status.HTTP_201_CREATED)
async def add_task(project_id: int, user_id: int, task: TaskSchema, db: db_dependency, pm: user_dependency):
  check_user_pm(pm)
  check_project_exists(project_id, db)
  if not is_pm_for_project(project_id, pm.get("id"), db):
      raise_error("Ви не є PM даного проекту", status.HTTP_403_FORBIDDEN)
  check_user_exists(user_id,db)
  new_task = Tasks(title=task.title, description=task.description, project_id=project_id, employee_id=user_id,pm_id=pm.get('id'))
  db.add(new_task)
  db.commit()
  return new_task

@router.get("/check_task_for_user/{user_id}",status_code=status.HTTP_200_OK)
async def check_task_for_user(user_id: int, db: db_dependency, user: user_dependency):
  check_user_exists(user_id, db)
  tasks_owner_or_pm(user,user_id,db)
  tasks = check_user_tasks_by_user_id(user_id, db)
  return tasks

@router.get("/get_task/{task_id}",status_code=status.HTTP_200_OK)
async def get_task(task_id: int, db: db_dependency,pm:user_dependency):
    check_task_exists(task_id, db)
    task = get_task_by_id(task_id, db)
    tasks_owner_or_pm(pm,task.employee_id,db)
    return task



    

