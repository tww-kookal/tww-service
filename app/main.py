from fastapi import FastAPI, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from .routers import login, rooms, users, roles, reports, customers, booking, admin, payments, accounting
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi.middleware.cors import CORSMiddleware
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from .config.config import settings

### Logger Settings ###
# ANSI escape codes for colors
COLORS = {
    "DEBUG": "\033[37m",     # White
    "INFO": "\033[34m",      # BLUE
    "WARNING": "\033[33m",   # Yellow
    "ERROR": "\033[31m",     # Red
    "CRITICAL": "\033[41m",  # Red background
}
RESET = "\033[0m"

class ColorFormatter(logging.Formatter):
    def format(self, record):
        log_fmt = "%(levelname)s: [%(asctime)s.%(msecs)03d] %(name)s: %(message)s"
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        
        # Apply color based on level name
        if record.levelname in COLORS:
            record.levelname = f"{COLORS[record.levelname]}{record.levelname}{RESET}"
        
        return formatter.format(record)

# Application log directory
# Change this line in your main.py file to log inside the application directory
LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / "fastapi.log"

# Log format
LOG_FORMAT = (
    "%(levelname)s: [%(asctime)s.%(msecs)03d] "
    "%(name)s: %(message)s"
)

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# File handler with rotation
file_handler = RotatingFileHandler(
    LOG_FILE,
    maxBytes=10 * 1024 * 1024,  # 10 MB
    backupCount=5,
)

# FORCE IMMEDIATELY FLUSH TO DISK
file_handler.flush() 

file_handler.setFormatter(
    logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(
    logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
)

# Configure root logger
root_logger = logging.getLogger()
root_logger.setLevel(settings.LOG_LEVEL)

# Avoid adding duplicate handlers
if not any(
    isinstance(handler, RotatingFileHandler)
    and getattr(handler, "baseFilename", None) == str(LOG_FILE)
    for handler in root_logger.handlers
):
    root_logger.addHandler(file_handler)

if not any(
    isinstance(handler, logging.StreamHandler)
    and not isinstance(handler, logging.FileHandler)
    for handler in root_logger.handlers
):
    root_logger.addHandler(console_handler)

# # Configure root logger
# handler = logging.StreamHandler()
# #handler.setFormatter(ColorFormatter())
# logging.basicConfig(
#     level=settings.LOG_LEVEL,  # Set the logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL
#     format="%(levelname)s: [%(asctime)s.%(msecs)03d] %(name)s: %(message)s",  # Format with time, level, logger name
#     datefmt="%Y-%m-%d %H:%M:%S",  # Date format
#     handlers=[handler]
# )

logger = logging.getLogger("tww.service.main")

########## Log Setup Completed ############
logger.info("The Westwood FastAPI application logging initialized")
logger.info(f"Log Level: {settings.LOG_LEVEL}")

#Incorporate Rate Limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="The Westwood Booking API",
    version="1.0.0",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    openapi_url="/api/v1/openapi.json",
)

# Register exception handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

Instrumentator().instrument(
    app,
).expose(app, include_in_schema=False, tags=["metrics"])

######## Add CORS Error
app.add_middleware(
  CORSMiddleware,
  allow_origins=["http://localhost:5173", 
                 "https://tww-kookal.github.io", 
                 "https://backofficestage.thewestwood.in", 
                 "https://backoffice.thewestwood.in"],  # Allowed origins
  allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # HTTP methods
  allow_headers=["*"],
  expose_headers=["*"],
  allow_credentials=True,
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code} for {request.url.path}")
    return response

# Include routers
app.include_router(admin.router)
app.include_router(login.router)
app.include_router(rooms.router)
app.include_router(customers.router)
app.include_router(users.router)
app.include_router(roles.router)
app.include_router(reports.router)
app.include_router(booking.router)
app.include_router(payments.router)
app.include_router(accounting.router)

@app.get("/")
def root():
    return {
        "application": "The Westwood Booking API",
        "version": "1.0.0",
        "docs": "/api/v1/docs",
        "api_prefix": "/api/v1",
    }
