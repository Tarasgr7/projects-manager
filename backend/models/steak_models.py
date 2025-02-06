from ..dependencies import Base
from sqlalchemy import Column, Integer, String, ForeignKey,Date
from sqlalchemy.orm import relationship
from datetime import datetime


class Steaks(Base):
  __tablename__ = 'steaks'
  id= Column(Integer, primary_key=True,index=True)
  user_id=Column(Integer, ForeignKey('users.id',ondelete="CASCADE"))
  technology=Column(String,nullable=False)
  created_at = Column(Date, default=datetime.now)
  updated_at = Column(Date, default=datetime.now, onupdate=datetime.now)

  user = relationship("Users", back_populates="steaks")