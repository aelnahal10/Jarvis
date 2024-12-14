from fastapi import FastAPI
from app.routes import alexa

app = FastAPI(title="Alexa Skill Backend")

# Include Alexa routes
app.include_router(alexa.router)

@app.get("/")
def root():
    return {"message": "Backend is running!"}
