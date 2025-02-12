from ..dependencies import Base
from sqlalchemy import Column, Integer, String, Date,  Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

class Tasks(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    pm_id = Column(Integer, ForeignKey('users.id'), nullable=False)  # Зовнішній ключ на Users
    employee_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)  # Зовнішній ключ на Users
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    status = Column(Boolean, nullable=False, default=False)
    created_at = Column(Date, default=datetime.now)
    updated_at = Column(Date, default=datetime.now, onupdate=datetime.now)

    # Відношення до Users
    pm = relationship("Users", back_populates="tasks_as_pm", foreign_keys=[pm_id])  # pm_id
    employee = relationship("Users", back_populates="tasks_as_employee", foreign_keys=[employee_id])  # employee_id

    project = relationship("Projects", back_populates="tasks")