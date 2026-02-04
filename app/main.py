from fastapi import FastAPI
import os

app = FastAPI()

VERSION = os.getenv("APP_VERSION", "v1")

@app.get("/")
def root():
    return {
        "message": "Hello from Argo Rollouts",
        "version": VERSION
    }

@app.get("/health")
def health():
    return {"status": "ok"}

