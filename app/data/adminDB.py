from . import database
import traceback
import logging
####### Logger ############
logger = logging.getLogger("tww.service.admindb")

def execute(string):
    try:
        conn = database.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(string)
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error while executing string: {string}")
        logger.error(f"Exception {e}")
        return False
    