from . import database
from .. import utils

def queryUserDB(username: str):
    conn = database.get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT user_id, username, first_name, last_name, email, phone, password FROM users WHERE username=%s", (username,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

def queryUserByIdDB(user_id):
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, username, first_name, last_name, email, phone FROM users WHERE user_id = %s", (user_id,))
    userTuple = cursor.fetchone() # Returns a tuple (user_id, username, first_name, last_name, email, phone) or None if not found
    cursor.close()
    conn.close()
    return userTuple

def persistUserDB(username, password, first_name, last_name, email, phone):
    conn = database.get_connection()
    cursor = conn.cursor()
    hashed_pwd = utils.hash_password(password)
    # Check if username already exists
    cursor.execute("SELECT user_id FROM users WHERE username = %s", (username,))
    if cursor.fetchone() is not None:
        print("Username already exists")
        raise Exception("Username already exists")

    cursor.execute("INSERT INTO users (username, password, first_name, last_name, email, phone) VALUES (%s, %s, %s, %s, %s, %s)",
                   (username, hashed_pwd, first_name, last_name, email, phone))
    conn.commit()
    cursor.close()
    conn.close()
    return True

def queryRolesForUserDB(userName: str):
    conn = database.get_connection()
    cursor = conn.cursor(dictionary=False)
    cursor.execute("select role_name from roles , user_roles , users  where user_roles.role_id = roles.role_id and user_roles.user_id = users.user_id and users.username=%s", (userName,))
    user_roles = cursor.fetchall() # Returns a list of tuples with role names or an empty list if no roles found
    print("User Roles: ", user_roles)
    
    if not user_roles:
        return []
    cursor.close()
    conn.close()
    return convertTupleToList(user_roles)

def queryAllUsersDB():
    conn = database.get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT user_id, username, first_name, last_name, email, phone FROM users")
    users = cursor.fetchall() # Returns a list of dictionaries of users in tuple format
    cursor.close()
    conn.close()
    return users

def convertTupleToList(userRoles):
    # Returns a list of role names or an empty list if no roles found
    # Example: [('admin',), ('agent',)] -> ['admin', 'agent']
    # Example: [] -> []
    convetedRoles = []
    for role in userRoles:
        convetedRoles.append(role[0])
    return convetedRoles

def assignRolesToUserDB(username: str, roleNames: list[str]):
    conn = database.get_connection()
    cursor = conn.cursor()
    try:
        user = queryUserDB(username)
        print("User Retrieved ", user)
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
        print("Exception Received in assignRolesToUserDB: ", e)
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()


