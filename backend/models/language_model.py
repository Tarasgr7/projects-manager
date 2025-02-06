from ..dependencies import Base
from sqlalchemy import Column, Integer, String, ForeignKey,Date
from sqlalchemy.orm import relationship
from datetime import datetime


class Language(Base):
  __tablename__ = 'language'
  id= Column(Integer, primary_key=True,index=True)
  user_id=Column(Integer, ForeignKey('users.id',ondelete="CASCADE"))
  language=Column(String,nullable=False)
  created_at = Column(Date, default=datetime.now)
  updated_at = Column(Date, default=datetime.now, onupdate=datetime.now)

  user = relationship("Users", back_populates="language")