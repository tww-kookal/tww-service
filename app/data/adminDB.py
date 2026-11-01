from . import database
import traceback
import logging
####### Logger ############
logger = logging.getLogger("tww.service.admindb")

def execute(script):
    try:
        conn = database.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(script["query"])
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error while executing string: {script}")
        logger.error(f"Exception {e}")
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
