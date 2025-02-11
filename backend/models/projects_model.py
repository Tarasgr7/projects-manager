from ..dependencies import Base
from datetime import datetime
from sqlalchemy import Integer,Column,String,ForeignKey,Date
from sqlalchemy.orm import relationship



class Projects(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    pm_id=Column(Integer, ForeignKey("users.id"))
    name = Column(String, unique=True, nullable=False)
    descriptions = Column(String, unique=True, nullable=False)

    users=relationship("Users", back_populates="projects")

