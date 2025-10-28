from . import database
from .. import utils
import logging

###### Logger #########
logger = logging.getLogger("tww.service.usersdb")

def queryUserDB(username: str):
    try:
        conn = database.get_connection()
        cursor = conn.cursor(dictionary=True)
        query  = """
                SELECT user_id, username, first_name, last_name, email, phone, booking_commission, user_type, 
                password FROM users WHERE username=%s
        """
        cursor.execute(query, (username,))
        user = cursor.fetchone()
        return user
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def queryUserByIdDB(user_id):
    try:
        conn = database.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT user_id, username, first_name, last_name, email, phone, booking_commission, user_type FROM users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone() # Returns a tuple (user_id, username, first_name, last_name, email, phone) or None if not found
        return user
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def persistUserDB(user):
    try:    
        conn = database.get_connection()
        cursor = conn.cursor()
        query = """
            INSERT INTO users 
                (username, password, first_name, last_name, email, phone, booking_commission, user_type) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query,                       
                    (user["username"], 
                     user["hashed_password"], 
                     user["first_name"], 
                     user["last_name"], 
                     user["email"], 
                     user["phone"], 
                     user["booking_commission"], 
                     user["user_type"])
                )
        user["user_id"] = cursor.lastrowid
        conn.commit()
        return user
    except Exception as e:
        logger.error("Exception while persisting user: %s", e)
        conn.rollback()
        raise e
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def updateUserDetailDB(user):
    try:
        conn = database.get_connection()
        cursor = conn.cursor()
        query = """
                UPDATE users SET 
                    username=%s, first_name=%s, last_name=%s, email=%s, phone=%s, 
                    booking_commission=%s, user_type=%s WHERE user_id=%s
        """

        try:
            cursor.execute(query,(user["username"], user["first_name"], 
                                user["last_name"], user["email"], user["phone"], user["booking_commission"], 
                                user["user_type"],
                                user["user_id"]))
            conn.commit()
            return user
        except Exception as e:
            logger.error(f"Exception Received in updateUserDetailDB: {e}")
            conn.rollback()
            raise e
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def queryRolesForUserDB(userName: str):
    try:
        conn = database.get_connection()
        cursor = conn.cursor(dictionary=False)
        cursor.execute("SELECT role_name FROM roles, user_roles, users  WHERE user_roles.role_id = roles.role_id AND user_roles.user_id = users.user_id AND users.username=%s", (userName,))
        user_roles = cursor.fetchall() # Returns a list of tuples with role names or an empty list if no roles found
        
        if not user_roles:
            return []
        return convertTupleToList(user_roles)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def queryAllUsersDB():
    try:
        conn = database.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT user_id, username, first_name, last_name, email, phone, booking_commission, user_type FROM users ORDER BY first_name DESC")
        users = cursor.fetchall() # Returns a list of dictionaries of users in tuple format
        return users
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def convertTupleToList(userRoles):
    # Returns a list of role names or an empty list if no roles found
    # Example: [('admin',), ('agent',)] -> ['admin', 'agent']
    # Example: [] -> []
    convetedRoles = []
    for role in userRoles:
        convetedRoles.append(role[0])
    return convetedRoles

def assignRolesToUserDB(username: str, roleNames: list[str]):
    try:
        conn = database.get_connection()
        cursor = conn.cursor()
        try:
            user = queryUserDB(username)
            logger.info("User Retrieved ", user)
            if user is None or user["user_id"] is None :
                raise Exception("User not found")

            # Create placeholders: %s, %s for the query
            placeholders = ", ".join(["%s"] * len(roleNames))
            query = f"""
                INSERT INTO user_roles (user_id, role_id)
                SELECT %s, role_id FROM roles WHERE role_name IN ({placeholders})
            """

            # Combine user_id with roleNames for parameters
            params = [user["user_id"]] + roleNames
            cursor.execute(query, params)
            conn.commit()
        except Exception as e:
            logger.error(f"Exception Received in assignRolesToUserDB: {e}")
            conn.rollback()
            raise e
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def queryAllBookingSourcesDB():
    try:
        conn = database.get_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
                SELECT user_id, username, first_name, last_name, email, phone, booking_commission, user_type 
                FROM users 
                WHERE user_type IN ('BOOKING-AGENT', 'EMPLOYEE', 'PARTNER', 'CXO', 'COMPANY')
                ORDER BY first_name DESC
        """
        cursor.execute(query)
        return cursor.fetchall() # Returns a list of dictionaries of booking sources in tuple format
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def queryAllEmployeesDB():
    try:
        conn = database.get_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
                SELECT user_id, username, first_name, last_name, email, phone, booking_commission, user_type 
                FROM users 
                WHERE user_type IN ('EMPLOYEE', 'PARTNER', 'CXO', 'COMPANY')
                ORDER BY first_name DESC
        """
        cursor.execute(query)
        return cursor.fetchall() # Returns a list of dictionaries of employees in tuple format
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def queryAllVendorsDB():
    try:
        conn = database.get_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
                SELECT user_id, username, first_name, last_name, email, phone, booking_commission, user_type 
                FROM users 
                WHERE user_type IN ('VENDOR')
                ORDER BY first_name DESC
        """
        cursor.execute(query)
        return cursor.fetchall() # Returns a list of dictionaries of vendors in tuple format
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def queryAllNonCustomersDB():
    try:
        conn = database.get_connection()
        cursor = conn.cursor(dictionary=True)
        query = """
                SELECT user_id, username, first_name, last_name, email, phone, booking_commission, user_type 
                FROM users 
                WHERE user_type NOT IN ('CUSTOMER')
                ORDER BY first_name DESC
        """
        cursor.execute(query)
        return cursor.fetchall() # Returns a list of dictionaries of non-customers in tuple format
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()