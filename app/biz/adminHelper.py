from ..data import adminDB
import traceback
import logging

####### Logger ############
logger = logging.getLogger("tww.service.adminhelper")

def execute():
    try:
        return adminDB.execute()
    except Exception as e:
        logger.error(f"Exception in execute: {e}")
        traceback.print_exc()
        return []
