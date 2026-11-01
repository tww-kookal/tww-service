import sys
import os

# Get the directory where passenger_wsgi.py is located
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Force the working directory to match your app root
os.chdir(current_dir)

# Import the adapter
from a2wsgi import ASGIMiddleware

# Import your FastAPI instance from app/main.py
from app.main import app

# Wrap the ASGI app into a WSGI application for Phusion Passenger
application = ASGIMiddleware(app)