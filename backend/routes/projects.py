from fastapi import APIRouter, status, HTTPException
from ..dependencies import logger
from ..services.utils import user_dependency, db_dependency
from ..services.projects_service import *
from ..models.projects_model import Projects
from ..models.employee_model import Employee
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
async def get_projects(db: db_dependency, user: user_dependency):
    check_user_pm(user)
    logger.info(f"Перегляд списку проектів для {user.get('email')}")
    return db.query(Projects).all()

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

@router.delete("/delete_employee", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee(employee: EmployeeSchema, db: db_dependency, pm: user_dependency):
    check_user_pm(pm)
    check_project_exists(employee.project_id,db)
    if not is_pm_for_project(employee.project_id, pm.get("id"), db):
        raise_error("Ви не є PM проекту", status.HTTP_403_FORBIDDEN)
    user=get_user_by_id(employee.user_id,db)
    if user:
        user.project = None
    db.commit()

    logger.info(f"Працівник {user.username} видалений з проекту {employee.project_id}")

@router.get("/get_employees_by_project/{project_id}", status_code=status.HTTP_200_OK)
async def get_employees_by_project(project_id: int, db: db_dependency, pm: user_dependency):
    check_user_pm(pm)
    check_project_exists(project_id,db)
    employees=get_employee_by_project_id(project_id,db)
    logger.info(f"Отримання працівників для проекту {project_id}")
    return employees
