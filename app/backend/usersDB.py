from app.backend import database
import logging

###### Logger #########
logger = logging.getLogger("tww.service.backend.usersdb")

def queryUserDB(username: str, conn):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT user_id, username, first_name, last_name, email, phone, booking_commission, password FROM users WHERE username=%s", (username,))
    user = cursor.fetchone()
    cursor.close()
    return user

def queryUserByIdDB(user_id, conn):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT user_id, username, first_name, last_name, email, phone, booking_commission FROM users WHERE user_id = %s", (user_id,))
    user = cursor.fetchone() # Returns a tuple (user_id, username, first_name, last_name, email, phone) or None if not found
    cursor.close()
    return user

def persistUserDB(user, conn):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, password, first_name, last_name, email, phone, booking_commission) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                   (user["username"], user["hashed_password"], user["first_name"], user["last_name"], user["email"], user["phone"], user["booking_commission"]))
    user["user_id"] = cursor.lastrowid
    cursor.close()
    return user

def updateUserDetailDB(user, conn):
    cursor = conn.cursor()
    query = """
            UPDATE users SET 
                username=%s, first_name=%s, last_name=%s, email=%s, phone=%s, 
                booking_commission=%s WHERE user_id=%s
    """
    try:
        cursor.execute(query,(user["username"], user["first_name"], 
                            user["last_name"], user["email"], user["phone"], user["booking_commission"], user["user_id"]))
        cursor.close()
        return user
    except Exception as e:
        logger.error(f"Exception Received in updateUserDetailDB: {e}")
        raise e


def queryRolesForUserDB(userName: str, conn):
    cursor = conn.cursor(dictionary=False)
    cursor.execute("SELECT role_name FROM roles, user_roles, users  WHERE user_roles.role_id = roles.role_id AND user_roles.user_id = users.user_id AND users.username=%s", (userName,))
    user_roles = cursor.fetchall() # Returns a list of tuples with role names or an empty list if no roles found
    
    if not user_roles:
        return []
    cursor.close()
    return convertTupleToList(user_roles)

def queryAllUsersDB(conn):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT user_id, username, first_name, last_name, email, phone, booking_commission FROM users ORDER BY first_name DESC")
    users = cursor.fetchall() # Returns a list of dictionaries of users in tuple format
    cursor.close()
    return users

def convertTupleToList(userRoles):
    # Returns a list of role names or an empty list if no roles found
    # Example: [('admin',), ('agent',)] -> ['admin', 'agent']
    # Example: [] -> []
    convetedRoles = []
    for role in userRoles:
        convetedRoles.append(role[0])
    return convetedRoles

def assignRolesToUserDB(username: str, roleNames: list[str], conn):
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
    except Exception as e:
        logger.error(f"Exception Received in assignRolesToUserDB: {e}")
        raise e
    finally:
        cursor.close()

