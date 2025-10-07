from . import database
import logging
import traceback

###### Logger #########
logger = logging.getLogger("tww.service.customersDB")

def queryAllCustomersDB():
    try:
        conn = database.get_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT user_id as customer_id, concat(first_name, ' ', last_name) as customer_name, email, phone, area, 
            city, state, country, zip_code, user_type 
            FROM users 
            WHERE user_type = 'CUSTOMER'
            ORDER BY customer_name;
        """
        cursor.execute(query)
        return cursor.fetchall()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def queryCustomerByIDDB(customer_id: int):
    try:
        conn = database.get_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT user_id as customer_id, concat(first_name, ' ', last_name) as customer_name, 
            email, phone, area, city, state, country, zip_code, user_type 
            FROM users 
            WHERE user_id = %s AND user_type = 'CUSTOMER'
        """
        cursor.execute(query, (customer_id,))
        customer = cursor.fetchone()
        return customer
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def queryCustomerByNameAndPhoneDB(customer_name: str, phone: str):
    try:
        conn = database.get_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT user_id as customer_id, concat(first_name, ' ', last_name) as customer_name, 
            email, phone, area, city, state, country, zip_code, user_type 
            FROM users 
            WHERE user_type = 'CUSTOMER' AND CONCAT(first_name, ' ', last_name) = %s AND phone = %s
        """
        cursor.execute(query, (customer_name, phone))
        customer = cursor.fetchall()
        return customer
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def extract_names(full_name: str):
    customer_name_parts = full_name.split()
        # Handle cases where customer_name is just a first name
        # If customer_name is just a first name, set last_name to empty string
        # If customer_name has more than one part, set first_name to first part and last_name to second part
        # If customer_name has more than two parts, set first_name to first part and last_name to rest of parts joined by space
        # If customer_name has more than two parts, set first_name to first part and last_name to rest of parts joined by space
    first_name = customer_name_parts[0]
    last_name = customer_name_parts[1] if len(customer_name_parts) > 1 else ''
    if len(customer_name_parts) > 2:
        last_name = ' '.join(customer_name_parts[2:])
    return first_name,last_name

def createCustomerDB(customer):    
    conn = database.get_connection()
    try:
        # Check if customer_name is empty
        if not customer["user_type"]:
            logger.error(f"User Type is empty")
            raise Exception("User Type is empty")
        # Check if phone is empty
        if not customer["phone"]:
            logger.error(f"Phone is empty")
            raise Exception("Phone is empty")
        
        duplicateCustomer = queryCustomerByNameAndPhoneDB(customer["customer_name"], customer["phone"])
        if len(duplicateCustomer) > 0:
            logger.info(f"Customer Already Exists")
            raise Exception("Customer Already Exists")
        first_name, last_name = extract_names(customer["customer_name"])
        #create a username of 50 characters or less with customer_name and phone
        username = f"{first_name.lower()}_{last_name.lower()}_{customer['phone'][:5]}"
        if len(username) > 50:
            username = username[:50]
        query = """
            INSERT INTO users 
            (username, password, user_type, first_name, last_name, email, phone, area, city, state, country, zip_code) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        cursor = conn.cursor()
        response = cursor.execute(query, (
            username,
            'no-password',
            customer["user_type"] if customer["user_type"] is not None else None,
            first_name if first_name is not None else None,
            last_name if last_name is not None else None,
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
        return customer
    except Exception as e:
        logger.error(f"Exception in createCustomerDB: {e}")
        traceback.print_exc()
        raise e
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()    


def updateCustomerDB(customer):
    conn = database.get_connection()
    try:
        # Check if customer_name is empty
        if not customer["user_type"]:
            logger.error(f"User Type is empty")
            raise Exception("User Type is empty")
        # Check if phone is empty
        if not customer["phone"]:
            logger.error(f"Phone is empty")
            raise Exception("Phone is empty")
        first_name, last_name = extract_names(customer["customer_name"])
        query = """
            UPDATE users 
            SET first_name = %s, last_name = %s, email = %s, phone = %s, area = %s, city = %s, 
            state = %s, country = %s, zip_code = %s, user_type = %s
            WHERE user_id = %s
        """

        cursor = conn.cursor()
        cursor.execute(query, (
            first_name if first_name is not None else None, 
            last_name if last_name is not None else None,
            customer["email"] if customer["email"] is not None else None,
            customer["phone"] if customer["phone"] is not None else None,
            customer["area"] if customer["area"] is not None else None, 
            customer["city"] if customer["city"] is not None else None,
            customer["state"] if customer["state"] is not None else None, 
            customer["country"] if customer["country"] is not None else None, 
            customer["zip_code"] if customer["zip_code"] is not None else None,
            customer["user_type"] if customer["user_type"] is not None else None,
            customer["customer_id"] if customer["customer_id"] is not None else None,
        ))
        conn.commit()
        return customer
    except Exception as e:
        logger.error(f"Exception in updateCustomerDB: {e}")
        traceback.print_exc()
        raise e
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
