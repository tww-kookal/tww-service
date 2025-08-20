from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import logging
from pydantic import BaseModel
from .. import auth
from ..data import rolesDB

router = APIRouter(
    prefix="/api/v1/roles",  # all routes start with /api/v1/roles
    tags=["Roles"]    # OpenAPI grouping
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
####### Logger ############
logger = logging.getLogger("tww.service.roles")

class RoleCreate(BaseModel):
    role_name: str

@router.post("/create")
async def create_role(role: RoleCreate, authorized_user: dict = Depends(auth.authorizedUser(["admin"]))):
    role_name = role.role_name

    logger.info(f"Role To be created: {role_name}")
    try:
        rolesDB.persistRoleDB(role_name)
        return {
            "status": status.HTTP_201_CREATED,
            "message": "Role created successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail=str(e)
        )
    
@router.get("/")
async def listRoles(authorized_user: dict = Depends(auth.authorizedUser(["admin"]))):
    roles = rolesDB.queryRolesDB()
    return {
        "status": status.HTTP_200_OK,
        "roles": roles
    }

