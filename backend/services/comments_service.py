from fastapi import status
from ..models.comments_model import Comments
from .utils import raise_error
from ..dependencies import logger

def comments_for_task(task_id,db):
  comments = db.query(Comments).filter(Comments.task_id==task_id).all()
  if not comments:
    raise_error(f"Коментарів для задачі з id={task_id} не знайдено", status.HTTP_404_NOT_FOUND)
  return comments

def get_comment_by_id(comment_id,db):
  comment = db.query(Comments).filter(Comments.id==comment_id).first()
  if not comment:
    raise_error(f"Коментар з id={comment_id} не знайдено", status.HTTP_404_NOT_FOUND)
  return comment

def delete_comments_by_task_id(task_id, db):
    comments = db.query(Comments).filter(Comments.task_id == task_id).all()
    
    if not comments:
        logger.info(f"Коментарів для задачі з id={task_id} не знайдено")
        return  # Виходимо з функції, щоб уникнути помилок


    for comment in comments:
        db.delete(comment)  # Видаляємо кожен окремий коментар

    db.commit()  # Фіксуємо зміни в базі даних
    logger.info(f"Всі коментарі для задачі {task_id} успішно видалено")
