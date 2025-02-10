from ..models.users_models import Users
from fastapi import status
from .utils import raise_error

def get_user_by_id(user_id,db):
    user=db.query(Users).filter(Users.id==user_id).first()
    if not user:
        raise_error("Користувач з таким ID не знайдений", status.HTTP_404_NOT_FOUND)
    return user

def check_user_exists(user_id,db):
    user=db.query(Users).filter(Users.id==user_id).first()
    if not user:
        raise_error("Користувач з таким ID не знайдений", status.HTTP_404_NOT_FOUND)

def get_project_id_by_user_id(user_id,db):
    user=db.query(Users).filter(Users.id==user_id).first()
    if not user:
        raise_error("Користувач з таким ID не знайдений", status.HTTP_404_NOT_FOUND)
    return user.project