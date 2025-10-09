from fastapi import FastAPI, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from .routers import login, rooms, users, roles, reports, customers, booking, admin, payments, accounting, gateway
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi.middleware.cors import CORSMiddleware
import logging
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

# Configure root logger
handler = logging.StreamHandler()
#handler.setFormatter(ColorFormatter())
logging.basicConfig(
    level=settings.LOG_LEVEL,  # Set the logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL
    format="%(levelname)s: [%(asctime)s.%(msecs)03d] %(name)s: %(message)s",  # Format with time, level, logger name
    datefmt="%Y-%m-%d %H:%M:%S",  # Date format
    handlers=[handler]
)

logger = logging.getLogger("tww.service.main")

########## Log Setup Completed ############

logger.debug(f"Database Host: {settings.LOG_LEVEL}")

#Incorporate Rate Limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI()

# Register exception handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

Instrumentator().instrument(
    app,
).expose(app, include_in_schema=False, tags=["metrics"])

######## Add CORS Error
app.add_middleware(
  CORSMiddleware,
  allow_origins=["http://localhost:5173","https://tww-kookal.github.io"],
  allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # HTTP methods
  allow_headers=["*"],
  expose_headers=["*"],
  allow_credentials=True,
)

# Include routers
app.include_router(gateway.router)

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

app.include_router(gateway.router)