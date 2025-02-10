from fastapi import APIRouter, status,Depends
from time import time
import json
import redis
from ..services.redis_client import get_redis
from ..models.tasks_model import Tasks
from ..models.comments_model import Comments
from ..dependencies import logger
from ..services.utils import user_dependency, db_dependency
from ..services.tasks_service import *
from ..services.projects_service import *
from ..schemas.tasks_schema import TaskSchema
from ..schemas.comment_schemas import CommentSchema
from ..services.user_service import *
from ..services.comments_service import comments_for_task,get_comment_by_id,delete_comments_by_task_id


router = APIRouter(prefix="/tasks", tags=["tasks"])

#Дії з tasks
@router.post("/add_task/{project_id}/{user_id}",status_code=status.HTTP_201_CREATED)
async def add_task(project_id: int, user_id: int, task: TaskSchema, db: db_dependency, pm: user_dependency):
  check_user_pm(pm)
  check_project_exists(project_id, db)
  if not is_pm_for_project(project_id, pm.get("id"), db):
      raise_error("Ви не є PM даного проекту", status.HTTP_403_FORBIDDEN)
  check_user_exists(user_id,db)
  if project_id == get_project_id_by_user_id(user_id,db):
    new_task = Tasks(title=task.title, description=task.description, project_id=project_id, employee_id=user_id,pm_id=pm.get('id'))
    db.add(new_task)
    db.commit()
    return new_task
  else:
    raise_error("Працівник не має відношення до проекту, до якого належить ця задача", status.HTTP_403_FORBIDDEN)

@router.get('/complete_task/{task_id}',status_code=status.HTTP_200_OK)
async def complete_task(task_id: int, db: db_dependency, pm: user_dependency):
    check_task_exists(task_id, db)
    task = get_task_by_id(task_id, db)
    tasks_owner_or_pm(pm,task.employee_id,db)
    if task.status == True:
        raise_error("Задача вже завершена", status.HTTP_400_BAD_REQUEST)
    task.status = True
    db.commit()
    logger.info(f"Задача з ID {task_id} успішно завершена")
    return {"message": "Задача успішно завершена"}


@router.delete('/delete_task/{task_id}',status_code=status.HTTP_200_OK)
async def delete_task(task_id: int, db: db_dependency, pm: user_dependency):
    check_task_exists(task_id, db)
    task = get_task_by_id(task_id, db)
    is_pm=is_pm_for_project(task.project_id,pm.get('id'),db)
    if is_pm:
      db.delete(task)
      db.commit()
      delete_comments_by_task_id(task_id,db)
      logger.info(f"Задача з ID {task_id} успішно видалена")
      return {"message": "Задача успішно видалена"}
    else:
      logger.warning(f"Користувач {pm.get('email')} не �� PM проекту")
      raise_error("Ви не є PM даного проекту", status.HTTP_403_FORBIDDEN)

#Отримання tasks
@router.get("/all_tasks_for_projects/{project_id}", status_code=status.HTTP_200_OK)
async def all_tasks_for_projects(
    project_id: int, 
    db: db_dependency, 
    pm: user_dependency, 
    redis_client: redis.Redis = Depends(get_redis)  # Використання змінної для залежності Redis
):
    if is_pm_for_project(project_id,pm.get("id"),db)==False:
        raise_error("Ви не є PM проекту", status.HTTP_403_FORBIDDEN)
    start_time = time()  # Початок вимірювання часу
    logger.info(f"Отримання списку завдань для проекту {project_id}")

    # Генеруємо унікальний ключ кешу для кожного користувача та проєкту
    cache_key = f"tasks_project_{project_id}_user_{pm.get('id')}"

    # Перевіряємо, чи є дані в кеші Redis
    cached_data = await redis_client.get(cache_key)
    
    if cached_data:
        logger.info("✅ Дані взяті з кешу Redis")
        tasks = json.loads(cached_data)
    else:
        logger.info("⏳ Даних у кеші немає, виконуємо запит до БД")
        
        # Перевіряємо існування проекту
        check_project_exists(project_id, db)
        
        # Отримуємо список завдань з БД
        tasks = get_all_tasks_for_project(project_id, db)
        logger.info(f"Знайдено {len(tasks)} завдань")

        # Перетворюємо дані у формат JSON і зберігаємо в кеш Redis на 180 секунд
        tasks_data = [{"id": t.id, "title": t.title, "status": t.status} for t in tasks]
        await redis_client.set(cache_key, json.dumps(tasks_data), ex=180)
        logger.info(f"✅ Додано в кеш Redis на 180 секунд: {len(tasks)} завдань")

    return tasks





# @router.get("/all_tasks_for_projects/{project_id}",status_code=status.HTTP_200_OK)
# async def all_tasks_for_projects(project_id: int, db: db_dependency, pm: user_dependency):
#     check_project_exists(project_id, db)
#     tasks = get_all_tasks_for_project(project_id, db)
#     logger.info("Tasks was successfully found")
#     return tasks

@router.get('/get_unfulfilled_tasks_for_project/{project_id}',status_code=status.HTTP_200_OK)
async def get_unfulfilled_tasks_for_project(project_id: int, db: db_dependency, pm: user_dependency):
    if is_pm_for_project(project_id,pm.get('id'),db):
      check_project_exists(project_id, db)
      tasks = unfulfilled_tasks_for_project(project_id, db)
      logger.info("Tasks was successfully found")
      return tasks
    else:
      logger.warning(f"Користувач {pm.get('email')} не є PM проекту")
      raise_error("Ви не є PM даного проекту", status.HTTP_403_FORBIDDEN)




@router.get("/check_task_for_user/{user_id}", status_code=status.HTTP_200_OK)
async def check_task_for_user(
    user_id: int, 
    db: db_dependency, 
    user: user_dependency, 
    redis_client: redis.Redis = Depends(get_redis)  # Використання Redis для кешування
):
    # Генеруємо унікальний ключ кешу для кожного користувача
    cache_key = f"tasks_user_{user_id}"

    # Перевіряємо, чи є дані в кеші Redis
    cached_data = await redis_client.get(cache_key)
    
    if cached_data:
        logger.info("✅ Дані взяті з кешу Redis")
        tasks = json.loads(cached_data)
    else:
        logger.info("⏳ Даних у кеші немає, виконуємо запит до БД")

        # Перевіряємо існування користувача
        check_user_exists(user_id, db)
        tasks_owner_or_pm(user, user_id, db)

        # Отримуємо список завдань для користувача з БД
        tasks = get_all_tasks_for_employee(user_id, db)
        logger.info(f"Знайдено {len(tasks)} завдань для користувача")

        # Перетворюємо дані у формат JSON і зберігаємо в кеш Redis на 180 секунд
        tasks_data = [{"id": t.id, "title": t.title, "status": t.status} for t in tasks]
        await redis_client.set(cache_key, json.dumps(tasks_data), ex=180)
        logger.info(f"✅ Додано в кеш Redis на 180 секунд: {len(tasks)} завдань")

    return tasks



@router.get("/unfulfilled_tasks_for_employee/{user_id}",status_code=status.HTTP_200_OK)
async def unfulfilled_tasks_for_employee(user_id: int, db: db_dependency, user: user_dependency):
    check_user_exists(user_id, db)
    tasks_owner_or_pm(user,user_id,db)
    tasks = get_unfulfilled_tasks_for_employee(user_id, db)
    logger.info("Tasks was successfully found")
    return tasks



@router.get("/get_task/{task_id}",status_code=status.HTTP_200_OK)
async def get_task(task_id: int, db: db_dependency,pm:user_dependency):
    check_task_exists(task_id, db)
    task = get_task_by_id(task_id, db)
    tasks_owner_or_pm(pm,task.employee_id,db)
    return task

