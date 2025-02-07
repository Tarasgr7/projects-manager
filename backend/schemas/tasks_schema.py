from pydantic import BaseModel

class TaskSchema(BaseModel):
  title:str
  description:str

class TaskUpdateSchema(BaseModel):
  title: str
  description: str
  employee_id: int