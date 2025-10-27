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
        logger.debug(f"inside searchTransactions with criteria ")
        return data.searchTransactions(search_criteria)
    except Exception as e:
        logger.error (f"Exception in helper.searchTransactions: {e}")
        traceback.print_exc()
        raise e
    
def fetchConsolidatedTransactions(search_criteria: dict):
    try:
        logger.debug(f"inside fetchConsolidatedTransactions with criteria")
        transactions = data.searchTransactions(search_criteria)
        # filter for transaction's acc_category_type is 'debit' and calculate the sum
        expenses = [txn for txn in transactions if txn['acc_category_type'] == 'debit']
        total_expenses = sum([txn['acc_entry_amount'] for txn in expenses])

        sales = [txn for txn in transactions if txn['acc_category_type'] == 'credit']
        total_sales = sum([txn['acc_entry_amount'] for txn in sales])

        return {
            "expenses": total_expenses,
            "sales": total_sales,
            "revenue": total_sales - total_expenses
        }
    except Exception as e:
        logger.error (f"Exception in helper.fetchConsolidatedTransactions: {e}")
        traceback.print_exc()
        raise e
    
def addCommissionPayout(commission_payout: dict):
    try:
        logger.debug(f"inside addCommissionPayout with criteria {commission_payout}")
        selected_bookings = commission_payout["selected_bookings"] if "selected_bookings" in commission_payout else []
        if not selected_bookings or selected_bookings == []:
            logger.error("No bookings selected for commission payout")
            raise Exception("No bookings selected for commission payout")
        return data.createCommissionPayout(commission_payout)
    except Exception as e:
        logger.error (f"Exception in helper.addCommissionPayout: {e}")
        traceback.print_exc()
        raise e