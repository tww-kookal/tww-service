from . import database
import logging
####### Logger ############
logger = logging.getLogger("tww.service.rolesdb")

def persistRoleDB(role_name):
    conn = database.get_connection()
    cursor = conn.cursor()

    if queryRoleByNameDB(role_name) is not None:
        raise Exception("Role already exists")

    cursor.execute("INSERT INTO roles (role_name) VALUES (%s)", (role_name,))
    conn.commit()
    cursor.close()
    conn.close()

def queryRoleByNameDB(role_name):
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT role_id FROM roles WHERE role_name = %s", (role_name,))
    role_id = cursor.fetchone()
    cursor.close()
    conn.close()
    return role_id
