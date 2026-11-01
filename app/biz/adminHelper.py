from ..data import adminDB
import traceback
import logging

####### Logger ############
logger = logging.getLogger("tww.service.adminhelper")

def execute(script: dict):
    try:
        return adminDB.execute(script)
    except Exception as e:
        logger.error(f"Exception in execute: {e}")
        traceback.print_exc()
        return []
