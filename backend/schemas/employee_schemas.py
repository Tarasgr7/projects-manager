from pydantic import BaseModel

class EmployeeSchema(BaseModel):
  user_id:int
  project_id:int