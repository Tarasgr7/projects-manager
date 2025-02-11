from fastapi import APIRouter, Query,status
from ..services.utils import db_dependency,user_dependency
from ..models.users_models import Users, Steaks, Language
from typing import List

router = APIRouter(prefix="/search", tags=["search"])

# 1. Отримання усієї інформації про користувача за user_id
@router.get("/all_info_about_user/{user_id}",status_code=status.HTTP_200_OK)
def get_user_info(user_id: int, db: db_dependency):
    user = db.query(Users).filter(Users.id == user_id).first()
    if not user:
        return {"error": "User not found"}
    
    return {
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "username": user.username,
        "role": user.role,
        "project": user.project,
        "is_active": user.is_active,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
        "technologies": [steak.technology for steak in user.steaks],
        "languages": [lang.language for lang in user.language]
    }

# 2. Пошук користувачів за технологіями
@router.get("/search_users_by_steak",status_code=status.HTTP_200_OK)
def search_users_by_steak(db: db_dependency,technologies: List[str] = Query(...)):
    users_with_steaks = (
        db.query(Users)
        .join(Steaks, Users.id == Steaks.user_id)
        .filter(Steaks.technology.in_(technologies))
        .all()
    )
    
    user_counts = {user.id: len(user.steaks) for user in users_with_steaks}
    sorted_users = sorted(users_with_steaks, key=lambda u: user_counts[u.id], reverse=True)
    
    return [{
        "id": user.id,
        "username": user.username,
        "technologies": [steak.technology for steak in user.steaks]
    } for user in sorted_users]

# 3. Пошук користувачів за іноземними мовами
@router.get("/search_users_by_language",status_code=status.HTTP_200_OK)
def search_users_by_language(db: db_dependency,languages: List[str] = Query(...)):
    users_with_languages = (
        db.query(Users)
        .join(Language, Users.id == Language.user_id)
        .filter(Language.language.in_(languages))
        .all()
    )
    
    user_counts = {user.id: len(user.language) for user in users_with_languages}
    sorted_users = sorted(users_with_languages, key=lambda u: user_counts[u.id], reverse=True)
    
    return [{
        "id": user.id,
        "username": user.username,
        "languages": [lang.language for lang in user.language]
    } for user in sorted_users]

# 4. Пошук користувачів без проєктів
@router.get("/search_users_without_projects",status_code=status.HTTP_200_OK)
def search_users_without_projects(db: db_dependency):
    users = db.query(Users).filter(Users.project == None).all()
    return [{
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name
    } for user in users]
