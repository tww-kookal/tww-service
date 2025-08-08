from fastapi import FastAPI
from .routers import login, room, users, roles, reports
from .config import config

app = FastAPI()

# Include routers
app.include_router(login.router)
app.include_router(room.router)
app.include_router(users.router)
app.include_router(roles.router)
app.include_router(reports.router)
