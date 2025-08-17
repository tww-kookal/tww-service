import mysql.connector
from mysql.connector import pooling
import os
from dotenv import load_dotenv
from pathlib import Path

import logging
####### Logger ############
logger = logging.getLogger("tww.service.backend.database")

# Load correct env file based on virtualenv
# Detect environment from system env or default to dev
# Default to .env.dev if not specified
env_file = '.env.backend'
# Explicit absolute path to the .env file
env_path = Path(__file__).resolve().parent / env_file
print(f"Loading environment file from: {env_path}")
load_dotenv(dotenv_path=env_path)

dbconfig = {
    'host' : os.getenv("MYSQL_HOST"),
    'user' : os.getenv("MYSQL_USER"),
    'password' : os.getenv("MYSQL_PASSWORD"),
    'database' : os.getenv("MYSQL_DATABASE"),
    'port' : os.getenv("MYSQL_PORT"),
    'charset' : "utf8mb4",
    'collation' : "utf8mb4_general_ci"            
}

print (f"dbconfig: {dbconfig["host"]}")

# Connection pool
connection_pool = pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=5,
    **dbconfig
)

def get_connection():
    try:
        return connection_pool.get_connection()
    except mysql.connector.Error as e:
        logger.error(f"Error connecting to MySQL: {e}")
        raise e
