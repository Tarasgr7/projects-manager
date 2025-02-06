from ..dependencies import Base
from sqlalchemy import Column, Integer, String, Date, Enum, Boolean, ForeignKey
from sqlalchemy.orm import relationship


class Employee(Base):
  __tablename__ = 'employees'
  id=Column(Integer, primary_key=True,index=True)
  user_id=Column(Integer, ForeignKey('users.id',ondelete="CASCADE"))
  projects_id=Column(Integer,ForeignKey('projects.id',ondelete="CASCADE"))
  
  users=relationship("Users", back_populates="employee")
  projects=relationship("Projects", back_populates="employee")