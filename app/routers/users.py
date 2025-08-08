from fastapi import APIRouter
from ..data import database
from .. import utils

router = APIRouter()

@router.post("/createUser")
def create_user(username: str, password: str, role_id: int):
    conn = database.get_connection()
    cursor = conn.cursor()
    hashed_pwd = utils.hash_password(password)
    cursor.execute("INSERT INTO users (username, password, role_id) VALUES (%s, %s, %s)",
                   (username, hashed_pwd, role_id))
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": "User created successfully"}
