from pydantic import BaseModel

class ProjectSchema(BaseModel):
  name: str
  description: str

class ProjectsUpdateSchema(BaseModel):
  name: str
  description: str
  status: bool
  