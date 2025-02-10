from time import time
import json
import redis
from ..services.redis_client import get_redis
from fastapi import APIRouter, status,Depends
from ..dependencies import logger
from ..services.utils import user_dependency, db_dependency
from ..services.projects_service import *
from ..models.projects_model import Projects
from ..services.tasks_service import have_unfulfilled_tasks
from ..models.users_models import Users
from ..schemas.project_schemas import ProjectSchema
from ..schemas.employee_schemas import EmployeeSchema

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/create_project", status_code=status.HTTP_201_CREATED)
async def create_project(project: ProjectSchema, db: db_dependency, user: user_dependency):
    check_user_pm(user)
    
    if db.query(Projects).filter_by(name=project.name).first():
        raise_error("Проект з таким іменем вже існує", status.HTTP_400_BAD_REQUEST)

    new_project = Projects(name=project.name, descriptions=project.description, pm_id=user.get("id"))
    db.add(new_project)
    db.commit()
    db.refresh(new_project)

    logger.info(f"Проект '{project.name}' успішно створено")
    return new_project

@router.put("/update_projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_project(project_id: int, project: ProjectSchema, db: db_dependency, user: user_dependency):
    check_user_pm(user)
    if not is_pm_for_project(project_id, user.get("id"), db):
        raise_error("Ви не є PM проекту", status.HTTP_403_FORBIDDEN)

    project_in_db = db.query(Projects).filter_by(id=project_id, pm_id=user.get("id")).first()
    if not project_in_db:
        raise_error("Проект не знайдено", status.HTTP_404_NOT_FOUND)

    project_in_db.name, project_in_db.descriptions = project.name, project.description
    db.commit()
    db.refresh(project_in_db)

    logger.info(f"Проект '{project_id}' оновлено")

@router.delete('/delete_project/{project_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: int, db: db_dependency, user: user_dependency):
    check_user_pm(user)
    if not is_pm_for_project(project_id, user.get("id"), db):
        raise_error("Ви не є PM проекту", status.HTTP_403_FORBIDDEN)

    project_in_db = db.query(Projects).filter_by(id=project_id, pm_id=user.get("id")).first()
    if not project_in_db:
        raise_error("Проект не знайдено", status.HTTP_404_NOT_FOUND)

    db.delete(project_in_db)
    db.commit()

    logger.info(f"Проект '{project_id}' успішно видалено")

@router.get("/get_all_projects", status_code=status.HTTP_200_OK)
async def get_projects(
    db: db_dependency, 
    user: user_dependency, 
    redis_client: redis.Redis = Depends(get_redis)  # Використовуємо Redis для кешування
):
    # Перевіряємо роль користувача
    check_user_pm(user)
    
    # Генеруємо унікальний ключ кешу для списку проектів
    cache_key = f"projects_user_{user.get('id')}"

    # Перевіряємо, чи є дані в кеші Redis
    cached_data = await redis_client.get(cache_key)
    
    if cached_data:
        logger.info("✅ Дані взяті з кешу Redis")
        projects = json.loads(cached_data)
    else:
        logger.info("⏳ Даних у кеші немає, виконуємо запит до БД")
        
        # Отримуємо список проектів з БД
        projects = db.query(Projects).all()
        logger.info(f"Знайдено {len(projects)} проектів")

        # Перетворюємо дані у формат JSON і зберігаємо в кеш Redis на 180 секунд
        projects_data = [{"id": p.id, "name": p.name,"descriptions":p.descriptions} for p in projects]
        await redis_client.set(cache_key, json.dumps(projects_data), ex=180)
        logger.info(f"✅ Додано в кеш Redis на 180 секунд: {len(projects)} проектів")

    return projects




@router.get("/projects_by_pm", status_code=status.HTTP_200_OK)
async def get_projects_by_pm(db: db_dependency, user: user_dependency):
    check_user_pm(user)
    logger.info(f"Проекти для PM {user.get('email')}")
    return db.query(Projects).filter_by(pm_id=user.get("id")).all()

@router.get("/project_by_id/{project_id}", status_code=status.HTTP_200_OK)
async def get_project_by_id(project_id: int, db: db_dependency, user: user_dependency):
    check_user_pm(user)
    project = db.query(Projects).filter_by(id=project_id).first()
    if not project:
        raise_error("Проект не знайдено", status.HTTP_404_NOT_FOUND)
    return project

@router.post("/add_employee", status_code=status.HTTP_201_CREATED)
async def add_employee(employee: EmployeeSchema, db: db_dependency, pm: user_dependency):
    check_user_pm(pm)
    check_project_exists(employee.project_id,db)
    if not is_pm_for_project(employee.project_id, pm.get("id"), db):
        raise_error("Ви не є PM проекту", status.HTTP_403_FORBIDDEN)

    user = db.query(Users).filter_by(id=employee.user_id).first()
    if not user:
        raise_error("Користувач не знайдений", status.HTTP_404_NOT_FOUND)
    if type(user.project) == int:
        raise_error("Користувач вже має проект", status.HTTP_409_CONFLICT)

    user.project = employee.project_id
    db.commit()

    logger.info(f"Працівник {user.username} доданий до проекту ID:{employee.project_id}")

@router.delete("/delete_employee", status_code=status.HTTP_200_OK)
async def delete_employee(employee: EmployeeSchema, db: db_dependency, pm: user_dependency):
    check_user_pm(pm)
    check_project_exists(employee.project_id,db)
    if not is_pm_for_project(employee.project_id, pm.get("id"), db):
        raise_error("Ви не є PM проекту", status.HTTP_403_FORBIDDEN)
    user=get_user_by_id(employee.user_id,db)
    if  have_unfulfilled_tasks(employee.user_id,db):
        logger.warning("Користувач має невиконані завдання. Змініть виконавця цих завдань, або видаліть їх. ")
        raise_error("Користувач має невиконані завдання. Змініть виконавця цих завдань, або видаліть їх.", status.HTTP_409_CONFLICT)
    if user:
        user.project = None
    db.commit()

    logger.info(f"Працівник {user.username} видалений з проекту {employee.project_id}")
    return {"message":f"Працівник {user.username} видалений з проекту {employee.project_id}"}

@router.get("/get_employees_by_project/{project_id}", status_code=status.HTTP_200_OK)
async def get_employees_by_project(
    project_id: int, 
    db: db_dependency, 
    pm: user_dependency, 
    redis_client: redis.Redis = Depends(get_redis)  # Використовуємо Redis для кешування
):
    if is_pm_for_project(project_id,pm.get("id"),db) == False:
        raise_error("Ви не є PM проекту", status.HTTP_403_FORBIDDEN)
    # Перевіряємо роль користувача та існування проекту
    check_user_pm(pm)
    check_project_exists(project_id, db)

    # Генеруємо унікальний ключ кешу для працівників проекту
    cache_key = f"employees_project_{project_id}"

    # Перевіряємо, чи є дані в кеші Redis
    cached_data = await redis_client.get(cache_key)
    
    if cached_data:
        logger.info("✅ Дані взяті з кешу Redis")
        employees = json.loads(cached_data)
    else:
        logger.info("⏳ Даних у кеші немає, виконуємо запит до БД")
        
        # Отримуємо список працівників, які працюють над проектом
        employees = get_employee_by_project_id(project_id, db)
        logger.info(f"Знайдено {len(employees)} працівників для проекту {project_id}")

        # Перетворюємо дані у формат JSON і зберігаємо в кеш Redis на 180 секунд
        employees_data = [{"id": e.id, "name": e.username, "role": e.role} for e in employees]
        await redis_client.set(cache_key, json.dumps(employees_data), ex=180)
        logger.info(f"✅ Додано в кеш Redis на 180 секунд: {len(employees)} працівників")

    return employees



