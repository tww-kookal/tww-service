from fastapi import APIRouter
from ..data import database

router = APIRouter()

@router.post("/createRole")
def create_role(role_name: str):
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO roles (role_name) VALUES (%s)", (role_name,))
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": "Role created successfully"}
