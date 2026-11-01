from fastapi import FastAPI
from .routers import login, room, users, roles, reports
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="The Westwood Booking API",
    version="1.0.0",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    openapi_url="/api/v1/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

routers = [
    login.router,
    room.router,
    users.router,
    roles.router,
    reports.router,
]

for router in routers:
    app.include_router(router, prefix="/api/v1")

for router in routers:
    app.include_router(router)

@app.get("/")
def root():
    return {
        "application": "The Westwood Booking API",
        "version": "1.0.0",
        "docs": "/api/v1/docs",
        "api_prefix": "/api/v1",
    }

# # Include routers
# app.include_router(login.router)
# app.include_router(room.router)
# app.include_router(users.router)
# app.include_router(roles.router)
# app.include_router(reports.router)
