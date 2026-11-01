from . import database
import logging
####### Logger ############
logger = logging.getLogger("tww.service.rolesdb")

def persistRoleDB(role_name):
    try:
        conn = database.get_connection()
        cursor = conn.cursor()

        if queryRoleByNameDB(role_name) is not None:
            raise Exception("Role already exists")

        cursor.execute("INSERT INTO roles (role_name) VALUES (%s)", (role_name,))
        conn.commit()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def queryRoleByNameDB(role_name):
    try:
        conn = database.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT role_id FROM roles WHERE role_name = %s", (role_name,))
        role_id = cursor.fetchone()
        return role_id
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def queryRolesDB():
    try:
        conn = database.get_connection()
        cursor = conn.cursor(dictionary = True)
        cursor.execute("SELECT role_id, role_name FROM roles")
        roles = cursor.fetchall()
        return roles
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
