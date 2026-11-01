from ..data import customersDB as db
import logging
import traceback

####### Logger ############
logger = logging.getLogger("tww.service.customershelper")

def getAllCustomers():
    try:
        return db.queryAllCustomersDB()
    except Exception as e:
        logger.error(f"Error in getAllCustomers: {e}")
        return []

def getCustomerByID(customer_id: int):
    try:
        customer = db.queryCustomerByIDDB(customer_id)
        if customer is None:
            logger.error(f"Customer with ID {customer_id} not found")
            return None
        return customer
    except Exception as e:
        logger.error(f"Error in getCustomerByID: {e}")
        return None

def createCustomer(customer):
    try:
        return db.createCustomerDB(customer)
    except Exception as e:
        logger.error(f"Exception in createCustomer: {e}")
        traceback.print_exc()
        raise Exception("Not able to create the customer")

def updateCustomer(customer):
    try:
        return db.updateCustomerDB(customer)
    except Exception as e:
        logger.error(f"Exception in updateCustomer: {e}")
        traceback.print_exc()
        raise Exception("Not able to update the customer")
