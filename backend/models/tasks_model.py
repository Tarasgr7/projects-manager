from ..dependencies import Base
from sqlalchemy import Column, Integer, String, Date,  Boolean, ForeignKey
from datetime import datetime

class Tasks(Base):
  __tablename__ = 'tasks'
  id=Column(Integer, primary_key=True,index=True)
  project_id=Column(Integer, ForeignKey('projects.id'),nullable=False)
  pm_id=Column(Integer, ForeignKey('users.id'),nullable=False)
  employee_id=Column(Integer, ForeignKey('users.id',ondelete="CASCADE"),nullable=False)
  title=Column(String, nullable=False)
  description=Column(String, nullable=False)
  status=Column(Boolean, nullable=False,default=False)
  created_at=Column(Date, default=datetime.now)
  updated_at=Column(Date, default=datetime.now,onupdate=datetime.now)