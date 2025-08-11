from . import database
import logging
import traceback

###### Logger #########
logger = logging.getLogger("tww.service.customersDB")

def queryAllCustomersDB():
    conn = database.get_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT customer_id, full_name as customer_name, email, phone, area, 
        city, state, country, zip_code 
        FROM customers 
        ORDER BY customer_name
    """
    cursor.execute(query)
    customers = cursor.fetchall()
    cursor.close()
    conn.close()
    return customers

def queryCustomerByIDDB(customer_id: int):
    conn = database.get_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT customer_id, full_name as customer_name, email, phone, area, 
        city, state, country, zip_code 
        FROM customers 
        WHERE customer_id = %s
    """
    cursor.execute(query, (customer_id,))
    customer = cursor.fetchone()
    cursor.close()
    conn.close()
    return customer

def queryCustomerByNameAndPhoneDB(customer_name: str, phone: str):
    conn = database.get_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT customer_id, full_name as customer_name, email, phone, area, 
        city, state, country, zip_code 
        FROM customers 
        WHERE full_name = %s AND phone = %s
    """
    cursor.execute(query, (customer_name, phone))
    customer = cursor.fetchall()
    cursor.close()
    conn.close()
    return customer


def createCustomerDB(customer):
    conn = database.get_connection()
    try:
        duplicateCustomer = queryCustomerByNameAndPhoneDB(customer["customer_name"], customer["phone"])
        if len(duplicateCustomer) > 0:
            logger.info(f"Customer Already Exists")
            raise Exception("Customer Already Exists")

        query = """
            INSERT INTO customers 
            (full_name, email, phone, area, city, state, country, zip_code) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        cursor = conn.cursor()
        response = cursor.execute(query, (
            customer["customer_name"] if customer["customer_name"] is not None else None, 
            customer["email"] if customer["email"] is not None else None,
            customer["phone"] if customer["phone"] is not None else None,
            customer["area"] if customer["area"] is not None else None, 
            customer["city"] if customer["city"] is not None else None,
            customer["state"] if customer["state"] is not None else None, 
            customer["country"] if customer["country"] is not None else None, 
            customer["zip_code"] if customer["zip_code"] is not None else None,
        ))
        customer["customer_id"] = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        return customer
    except Exception as e:
        logger.error(f"Exception in createCustomerDB: {e}")
        traceback.print_exc()
        raise e


def updateCustomerDB(customer):
    conn = database.get_connection()
    try:
        query = """
            UPDATE customers 
            SET full_name = %s, email = %s, phone = %s, area = %s, city = %s, 
            state = %s, country = %s, zip_code = %s
            WHERE customer_id = %s
        """

        cursor = conn.cursor()
        cursor.execute(query, (
            customer["customer_name"] if customer["customer_name"] is not None else None, 
            customer["email"] if customer["email"] is not None else None,
            customer["phone"] if customer["phone"] is not None else None,
            customer["area"] if customer["area"] is not None else None, 
            customer["city"] if customer["city"] is not None else None,
            customer["state"] if customer["state"] is not None else None, 
            customer["country"] if customer["country"] is not None else None, 
            customer["zip_code"] if customer["zip_code"] is not None else None,
            customer["customer_id"] if customer["customer_id"] is not None else None,
        ))
        conn.commit()
        cursor.close()
        conn.close()
        return customer
    except Exception as e:
        logger.error(f"Exception in updateCustomerDB: {e}")
        traceback.print_exc()
        raise e
