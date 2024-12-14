from fastapi import FastAPI
from app.routes import alexa

app = FastAPI()
app.include_router(alexa.router)
