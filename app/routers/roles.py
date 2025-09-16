from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from slowapi import Limiter
from slowapi.util import get_remote_address
import logging
from pydantic import BaseModel
from .. import auth
from ..data import rolesDB

router = APIRouter(
    prefix="/api/v1/roles",  # all routes start with /api/v1/roles
    tags=["Roles"]    # OpenAPI grouping
)
limiter = Limiter(key_func=get_remote_address) #Incorporate Rate Limiter
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
####### Logger ############
logger = logging.getLogger("tww.service.roles")

class RoleCreate(BaseModel):
    role_name: str

@router.post("/create", description="Creates a new role")
@limiter.limit("1/second")
async def create_role(request: Request, role: RoleCreate, authorized_user: dict = Depends(auth.authorizedUser(["admin"]))):
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
    
@router.get("/", description="Lists all roles")
@limiter.limit("1/second")
async def listRoles(request: Request, authorized_user: dict = Depends(auth.authorizedUser(["admin"]))):
    roles = rolesDB.queryRolesDB()
    return {
        "status": status.HTTP_200_OK,
        "roles": roles
    }

