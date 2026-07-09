from fastapi import FastAPI, Depends, HTTPException
from backend.routers import employees


app = FastAPI()

# Create a new employee

app.include_router(employees.router)
