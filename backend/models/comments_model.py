from ..dependencies import Base
from sqlalchemy import Column, Integer, String, Date, Enum, Boolean,ForeignKey
from datetime import datetime

class Comments(Base):
  __tablename__ = 'comments'
  id=Column(Integer, primary_key=True,index=True)
  task_id=Column(Integer, ForeignKey('tasks.id'),nullable=False)
  user_id=Column(Integer, ForeignKey('users.id'),nullable=False)
  content=Column(String, nullable=False)