from fastapi import FastAPI
from .dependencies import Base, engine
from .routes import auth
app= FastAPI()



Base.metadata.create_all(bind=engine)

app.include_router(auth.router)