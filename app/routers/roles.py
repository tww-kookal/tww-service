from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from ..data import database
from ..auth import get_current_user
from ..utils import isAuthorized
from ..data.rolesDB import persistRoleDB

router = APIRouter(
    prefix="/roles",  # all routes start with /users
    tags=["Roles"]    # OpenAPI grouping
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/createRole")
async def create_role(role_name: str, current_user: dict = Depends(get_current_user)):
    # Check if current user is admin
    if isAuthorized(current_user, ["admin"]) == False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="not authorized"
        )

    print ("Role To be created: ", role_name)
    try:
        persistRoleDB(role_name)
        return {
            "status": status.HTTP_201_CREATED,
            "message": "Role created successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail=str(e)
        )
@router.get("/listRoles")
async def listRoles(current_user: dict = Depends(get_current_user)):
    # Check if current user is admin
    if isAuthorized(current_user, ["admin", 'manager']) == False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="not authorized"
        )

    roles = queryRolesDB()
    return roles

def queryRolesDB():
    conn = database.get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT role_id, role_name FROM roles")
    roles = cursor.fetchall()
    cursor.close()
    conn.close()
    return roles
