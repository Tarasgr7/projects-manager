from fastapi import FastAPI
from .dependencies import Base, engine
from .routes import auth, users,projects,tasks
app= FastAPI()



Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(projects.router)
app.include_router(tasks.router)