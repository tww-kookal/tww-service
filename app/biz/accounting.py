from ..data import accountingDB as data
from datetime import date

import logging
import traceback

####### Logger ############
logger = logging.getLogger("tww.service.accountingHelper")

def getAllAccountingCategories():
    try:
        logger.debug(f"inside getAllAccountingCategories")
        return data.listAllAccountingCategories()
    except Exception as e:
        logger.error (f"Exception in helper.getAllAccountingCategories: {e}")
        traceback.print_exc()
        raise e

def createExpense(expense: dict):
    logger.debug(f"createExpense:")
    return data.createExpense(expense)

def updateExpense(expense: dict):
    logger.debug(f"updateExpense:")
    return data.updateExpense(expense)

def getExpensesSince(expenseDate: date = date(2020, 1, 1)):
    try:
        logger.debug(f"inside getExpensesSince")
        return data.queryExpensesSince(expenseDate)
    except Exception as e:
        logger.error (f"Exception in helper.getExpensesSince: {e}")
        traceback.print_exc()
        raise e

def getPaymentsForBooking(bookingId: int):
    try:
        logger.debug(f"inside getPaymentsForBooking {bookingId}")
        return data.queryPaymentsForBooking(bookingId)
    except Exception as e:
        logger.error (f"Exception in helper.getPaymentsForBooking: {e}")
        traceback.print_exc()
        raise e

def deleteExpense(expenseId: int):
    try:
        logger.debug(f"inside deleteExpense {expenseId}")
        return data.deleteExpense(expenseId)
    except Exception as e:
        logger.error (f"Exception in helper.deleteExpense: {e}")
        traceback.print_exc()
        raise e