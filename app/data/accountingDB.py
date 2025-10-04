from . import database
from datetime import date
import logging
import traceback

logger = logging.getLogger("tww.service.accountingdb")

def listAllAccountingCategories():
    try:
        conn = database.get_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT acc_category_id, acc_category_name, acc_category_type
            FROM accounting_categories
            ORDER BY acc_category_name
        """
        cursor.execute(query)
        return cursor.fetchall()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def insertTransaction(transaction: dict):
    try:
        conn = database.get_connection()
        cursor = conn.cursor()
        query = """
            INSERT INTO accounting_entries 
            (acc_category_id, acc_entry_amount, acc_entry_date, acc_entry_description, 
            created_by, txn_by, paid_by, received_by, received_for_booking_id, payment_type)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        # if receveid_for_booking_id in transaction is <=0 then reset it to none
        if "received_for_booking_id" in transaction and (transaction["received_for_booking_id"] <= 0 or transaction["received_for_booking_id"] == ''):
            transaction["received_for_booking_id"] = None

        logger.debug(f"Transaction to create: {transaction}")
        cursor.execute(query, (
            transaction["acc_category_id"],
            float(transaction["acc_entry_amount"]),
            transaction["acc_entry_date"],
            transaction["acc_entry_description"],
            transaction["created_by"],
            transaction["txn_by"],
            transaction["paid_by"],
            transaction["received_by"],
            transaction["received_for_booking_id"],
            transaction["payment_type"]
        ))
        conn.commit()
        transaction["acc_entry_id"] = cursor.lastrowid
        return transaction
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def queryTransactionsSince(transactionDate: date):
    try:
        conn = database.get_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT acc_entry_id, acc_entry_amount, acc_entry_description, acc_entry_date, 
            a.acc_category_id, ac_cat.acc_category_name, ac_cat.acc_category_type,
            created_by, u.first_name as created_by_first_name, u.last_name as created_by_last_name, 
            txn_by, CONCAT(txn_cus.first_name, ' ', txn_cus.last_name) as txn_by_customer_name, txn_cus.phone as txn_by_customer_phone,
            paid_by, CONCAT(paid_cus.first_name, ' ', paid_cus.last_name) as paid_by_customer_name, paid_cus.phone as paid_by_customer_phone,
            received_by, CONCAT(recd_cus.first_name, ' ', recd_cus.last_name) as received_by_customer_name, recd_cus.phone as received_by_customer_phone,
            received_for_booking_id, CONCAT(c.first_name, ' ', c.last_name) as booking_customer_name, 
            c.phone as booking_customer_phone, r.room_name, a.payment_type
            FROM accounting_entries a 
            LEFT OUTER JOIN bookings b ON (a.received_for_booking_id = b.booking_id)
            LEFT OUTER JOIN users c ON (b.customer_id = c.user_id)
            LEFT OUTER JOIN rooms r ON (b.room_id = r.room_id)
            INNER JOIN users recd_cus ON (a.received_by = recd_cus.user_id)
            INNER JOIN users paid_cus ON (a.paid_by = paid_cus.user_id)
            INNER JOIN users txn_cus ON (a.txn_by = txn_cus.user_id)
            INNER JOIN users u ON (a.created_by = u.user_id)
            INNER JOIN accounting_categories ac_cat ON (a.acc_category_id = ac_cat.acc_category_id)
            WHERE acc_entry_date >= %s
            ORDER BY acc_entry_date, acc_category_name
        """
        cursor.execute(query, (transactionDate,))
        return cursor.fetchall()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def queryPaymentsForBooking(bookingId: int):
    try:
        logger.debug(f"Inside queryPaymentsForBooking {bookingId}")
        conn = database.get_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT acc_entry_id, acc_entry_id as booking_payments_id,  
            acc_entry_amount, acc_entry_amount as payment_amount,
            acc_entry_date, acc_entry_date as payment_date,
            received_by, received_by as payment_to, 
            CONCAT(recd_cus.first_name, ' ', recd_cus.last_name) as received_by_customer_name, 
            recd_cus.phone as received_by_customer_phone,
            a.acc_category_id, a.acc_category_id as payment_for, 
            ac_cat.acc_category_name, ac_cat.acc_category_type,
            acc_entry_description, acc_entry_description as remarks,
            created_by, u.first_name as created_by_first_name, u.last_name as created_by_last_name, 
            txn_by, CONCAT(txn_cus.first_name, ' ', txn_cus.last_name)as txn_by_customer_name, 
            txn_cus.phone as txn_by_customer_phone,
            paid_by, CONCAT(paid_cus.first_name, ' ', paid_cus.last_name) as paid_by_customer_name, 
            paid_cus.phone as paid_by_customer_phone,
            received_for_booking_id, received_for_booking_id as booking_id, 
            CONCAT(c.first_name, ' ', c.last_name) as booking_customer_name, 
            c.phone as booking_customer_phone, r.room_name, a.payment_type
            FROM accounting_entries a 
            LEFT OUTER JOIN bookings b ON (a.received_for_booking_id = b.booking_id)
            LEFT OUTER JOIN users c ON (b.customer_id = c.user_id)
            LEFT OUTER JOIN rooms r ON (b.room_id = r.room_id)
            INNER JOIN users recd_cus ON (a.received_by = recd_cus.user_id)
            INNER JOIN users paid_cus ON (a.paid_by = paid_cus.user_id)
            INNER JOIN users txn_cus ON (a.txn_by = txn_cus.user_id)
            INNER JOIN users u ON (a.created_by = u.user_id)
            INNER JOIN accounting_categories ac_cat ON (a.acc_category_id = ac_cat.acc_category_id)
            WHERE received_for_booking_id = %s
            ORDER BY acc_entry_date, acc_entry_id
        """
        cursor.execute(query, (bookingId,))
        return cursor.fetchall()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def updateTransaction(transaction: dict):
    conn = database.get_connection()
    try:
        cursor = conn.cursor()
        query = """
            UPDATE accounting_entries 
            SET acc_category_id = %s, acc_entry_amount = %s, acc_entry_date = %s, acc_entry_description = %s, 
            created_by = %s, txn_by = %s, paid_by = %s, received_by = %s, received_for_booking_id = %s, payment_type = %s
            WHERE acc_entry_id = %s
        """
        logger.debug(f"Transaction to update: {transaction}")
        cursor.execute(query, (
            transaction["acc_category_id"],
            float(transaction["acc_entry_amount"]),
            transaction["acc_entry_date"],
            transaction["acc_entry_description"],
            transaction["created_by"],
            transaction["txn_by"],
            transaction["paid_by"],
            transaction["received_by"],
            transaction["received_for_booking_id"],
            transaction["payment_type"],
            transaction["acc_entry_id"]
        ))
        conn.commit()
        return transaction
    except Exception as e:
        conn.rollback()
        logger.error (f"Exception in updateTransaction: {e}")
        traceback.print_exc()
        raise e
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def deleteTransaction(transactionId ):
    conn = database.get_connection()
    try:
        cursor = conn.cursor()
        query = """
            DELETE FROM accounting_entries 
            WHERE acc_entry_id = %s
        """
        cursor.execute(query, (
            transactionId,
        ))
        conn.commit()
        logger.debug(f"Transaction {transactionId} deleted")
    except Exception as e:
        conn.rollback()
        logger.error (f"Exception in deleteTransaction: {e}")
        traceback.print_exc()
        raise e
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


""""
def create_accounting_entry(db: Session, entry: AccountingEntryCreate):
    try:
        db_entry = AccountingEntry(**entry.model_dump())
        db.add(db_entry)
        db.commit()
        db.refresh(db_entry)
        return db_entry
    except Exception as e:
        db.rollback()
        logger.error (f"Exception in create_accounting_entry: {e}")
        traceback.print_exc()
        raise e

def get_accounting_parties(db: Session):
    try:
        return db.query(AccountingParty).all()
    except Exception as e:
        logger.error (f"Exception in get_accounting_parties: {e}")
        traceback.print_exc()
        raise e

def create_accounting_party(db: Session, party: AccountingPartyCreate):
    try:
        db_party = AccountingParty(**party.model_dump())
        db.add(db_party)
        db.commit()
        db.refresh(db_party)
        return db_party
    except Exception as e:
        db.rollback()
        logger.error (f"Exception in create_accounting_party: {e}")
        traceback.print_exc()
        raise e

def update_accounting_party(db: Session, party_id: int, party: AccountingPartyCreate):
    try:
        db_party = db.query(AccountingParty).filter(AccountingParty.id == party_id).first()
        if db_party:
            for key, value in party.model_dump().items():
                setattr(db_party, key, value)
            db.commit()
            db.refresh(db_party)
            return db_party
        return None
    except Exception as e:
        db.rollback()
        logger.error (f"Exception in update_accounting_party: {e}")
        traceback.print_exc()
        raise e """
