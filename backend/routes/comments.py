from fastapi import APIRouter, status
from ..models.comments_model import Comments
from ..dependencies import logger
from ..services.utils import user_dependency, db_dependency
from ..services.tasks_service import *
from ..schemas.comment_schemas import CommentSchema
from ..services.user_service import *
from ..services.comments_service import comments_for_task,get_comment_by_id

router = APIRouter(prefix="/comments", tags=["comments"])




@router.post("/add_comment_for_task/{task_id}",status_code=status.HTTP_201_CREATED)
async def add_comment_for_task(task_id:int,comment:CommentSchema,db:db_dependency,user: user_dependency):
    check_task_exists(task_id, db)
    task = get_task_by_id(task_id, db)
    tasks_owner_or_pm(user,task.employee_id,db)
    new_comment = Comments(content=comment.content, task_id=task_id, user_id=user.get('id'))
    db.add(new_comment)
    db.commit()
    return new_comment

@router.get("/get_comments_for_task/{task_id}",status_code=status.HTTP_200_OK)
async def get_comments_for_task(task_id: int, db: db_dependency, user: user_dependency):
    check_task_exists(task_id, db)
    task = get_task_by_id(task_id, db)
    tasks_owner_or_pm(user,task.employee_id,db)
    comments = comments_for_task(task_id, db)
    if not comments:
        raise_error("Коментарів для цієї задачі немає", status.HTTP_404_NOT_FOUND)
    logger.info("Коментар було успішно знайдено")
    return comments

@router.delete('/delete_comments/{comment_id}',status_code=status.HTTP_200_OK)
async def delete_comment(comment_id: int, db: db_dependency, user: user_dependency):
    comment = get_comment_by_id(comment_id, db)
    tasks_owner_or_pm(user,comment.user_id,db)
    db.delete(comment)
    db.commit()
    logger.info(f"Коментар з ID {comment_id} успішно видален")
    return {"message": "Коментар успішно видален"}