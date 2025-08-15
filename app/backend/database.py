import mariadb
from ..config.config import settings
import logging
####### Logger ############
logger = logging.getLogger("tww.service.backend.database")

def get_connection():
    try:
        # host='serverless-eu-west-3.sysp0000.db1.skysql.com',
        # port=4015,
        # user='dbpwf17950752',
        # password='OPPtUTlah7anxW5MH@Lblq8NM',
        # database='tww_database',
        # ssl_verify_cert=True
        conn = mariadb.connect (
            host=settings.MYSQL_HOST,
            user=settings.MYSQL_USER,
            password=settings.MYSQL_PASSWORD,
            database=settings.MYSQL_DATABASE,
            port=settings.MYSQL_PORT
            ssl_verify_cert=True,
        )

        return conn
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB: {e}")
        return None

# conn = mysql.connector.connect(
#     host=settings.MYSQL_HOST,
#     user=settings.MYSQL_USER,
#     password=settings.MYSQL_PASSWORD,
#     database=settings.MYSQL_DATABASE
# )
