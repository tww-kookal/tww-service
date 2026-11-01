import sys
import os

# Add the project root directory to the python path
sys.path.insert(0, os.path.dirname(__file__))

# Import the adapter
from a2wsgi import ASGIMiddleware

# Import your FastAPI instance from app/main.py
from app.main import app

# Wrap the ASGI app into a WSGI application for Phusion Passenger
application = ASGIMiddleware(app)
