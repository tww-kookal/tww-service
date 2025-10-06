from ..data import accountingDB as data
from datetime import date
from . import usersHelper as userHelper
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

def createTransaction(transaction: dict):
    try:
        logger.debug(f"createTransaction: {transaction}")
        userData = userHelper.queryUser(transaction['created_by'])
        transaction['created_by'] = userData['user_id']
        if 'txn_by' not in transaction:
            transaction['txn_by'] = transaction['paid_by']
        return data.insertTransaction(transaction)
    except Exception as e:
        logger.error (f"Exception in helper.createTransaction: {e}")
        traceback.print_exc()
        raise e

def updateTransaction(transaction: dict):
    try:
        logger.debug(f"updateTransaction: {transaction}")
        userData = userHelper.queryUser(transaction['created_by'])
        transaction['created_by'] = userData['user_id']
        if 'txn_by' not in transaction:
            transaction['txn_by'] = transaction['paid_by']
        return data.updateTransaction(transaction)
    except Exception as e:
        logger.error (f"Exception in helper.updateTransaction: {e}")
        traceback.print_exc()
        raise e

def getTransactionsSince(transactionDate: date = date(2020, 1, 1)):
    try:
        logger.debug(f"inside getTransactionsSince")
        return data.queryTransactionsSince(transactionDate)
    except Exception as e:
        logger.error (f"Exception in helper.getTransactionsSince: {e}")
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

def deleteTransaction(transactionId: int):
    try:
        logger.debug(f"inside deleteTransaction {transactionId}")
        return data.deleteTransaction(transactionId)
    except Exception as e:
        logger.error (f"Exception in helper.deleteTransaction: {e}")
        traceback.print_exc()
        raise e

def searchTransactions(search_criteria: dict):
    try:
        logger.debug(f"inside searchTransactions with criteria {search_criteria}")
        return data.searchTransactions(search_criteria)
    except Exception as e:
        logger.error (f"Exception in helper.searchTransactions: {e}")
        traceback.print_exc()
        raise e