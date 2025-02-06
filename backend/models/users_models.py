from ..dependencies import Base
from sqlalchemy import Column, Integer, String, Date,Enum,Boolean,ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime


class Users(Base):
  __tablename__ = 'users'
  id=Column(Integer, primary_key=True,index=True)
  email=Column(String, unique=True,nullable=False)
  first_name=Column(String, nullable=False)
  last_name=Column(String, nullable=False)
  hashed_password=Column(String,nullable=False)
  username=Column(String,nullable=False,unique=True)
  role = Column(String, nullable=False)
  projects=Column(Boolean,default=False)
  is_active = Column(Boolean, default=False)
  verification_token = Column(String, nullable=True)
  created_at=Column(Date, default=datetime.now)
  updated_at=Column(Date, default=datetime.now,onupdate=datetime.now)
  
  projects = relationship("Projects",back_populates='users', passive_deletes=True)
  employee = relationship("Employee",back_populates='users', passive_deletes=True)
  steaks = relationship("Steaks", back_populates='users', passive_deletes=True)
  language = relationship("Language", back_populates='users', passive_deletes=True)

class Steaks(Base):
  __tablename__ = 'steaks'
  id= Column(Integer, primary_key=True,index=True)
  user_id=Column(Integer, ForeignKey('users.id',ondelete="CASCADE"))
  technology=Column(String,nullable=False)
  created_at = Column(Date, default=datetime.now)
  updated_at = Column(Date, default=datetime.now, onupdate=datetime.now)

  users = relationship("Users", back_populates="steaks")


class Language(Base):
  __tablename__ = 'language'
  id= Column(Integer, primary_key=True,index=True)
  user_id=Column(Integer, ForeignKey('users.id',ondelete="CASCADE"))
  language=Column(String,nullable=False)
  created_at = Column(Date, default=datetime.now)
  updated_at = Column(Date, default=datetime.now, onupdate=datetime.now)

  users = relationship("Users", back_populates="language")