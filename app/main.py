from fastapi import FastAPI
from .routers import login, rooms, users, roles, reports
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()
Instrumentator().instrument(
    app,
).expose(app, include_in_schema=False, tags=["metrics"])

# Include routers
app.include_router(login.router)
app.include_router(rooms.router)
app.include_router(users.router)
app.include_router(roles.router)
app.include_router(reports.router)
