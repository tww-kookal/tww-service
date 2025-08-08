import os
from dotenv import load_dotenv
from pathlib import Path

# Load correct env file based on virtualenv
# Detect environment from system env or default to dev
# Default to .env.dev if not specified
env_file = os.getenv("ENV_FILE", ".env.dev")
# Explicit absolute path to the .env file
env_path = Path(__file__).resolve().parent / env_file
print(f"Loading environment file from: {env_path}")
load_dotenv(dotenv_path=env_path)

class Settings:
    MYSQL_HOST = os.getenv("MYSQL_HOST")
    MYSQL_USER = os.getenv("MYSQL_USER")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

settings = Settings()
print(f"Using environment file: {env_file}")
print(f"Database Host: {settings.MYSQL_HOST}")
print(f"Database User: {settings.MYSQL_USER}")
print(f"Database Password: {settings.MYSQL_PASSWORD}")
print(f"Database Name: {settings.MYSQL_DATABASE}")

