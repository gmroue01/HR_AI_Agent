from fastapi import FastAPI, Depends, HTTPException
from backend.routers import employees


app = FastAPI()


app.include_router(employees.router)
