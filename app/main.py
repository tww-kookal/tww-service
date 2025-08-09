from fastapi import FastAPI
from .routers import login, rooms, users, roles, reports

app = FastAPI()

# Include routers
app.include_router(login.router)
app.include_router(rooms.router)
app.include_router(users.router)
app.include_router(roles.router)
app.include_router(reports.router)
