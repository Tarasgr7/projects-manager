from pydantic import BaseModel

class UsersSchema(BaseModel):
  email: str
  first_name: str
  last_name: str
  password: str
  username: str
  role: str
  