from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from slowapi import Limiter
from slowapi.util import get_remote_address
import logging

from ..biz import customersHelper as helper
from .. import auth

####### Logger ############
logger = logging.getLogger("tww.service.customers")

router = APIRouter(
    prefix="/api/v1/customers",  # all routes start with /customers
    tags=["Customers"]    # OpenAPI grouping
)
limiter = Limiter(key_func=get_remote_address) #Incorporate Rate Limiter
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

from pydantic import BaseModel

class CustomerModel (BaseModel):
    customer_id: str
    customer_name: str
    user_type: str
    phone: str
    email: str
    city: str
    area: str
    state: str
    country: str
    zip_code: str

@router.get("/", description="Gets all customers")
@limiter.limit("10/second")
async def getAllCustomers(request: Request, authorized_user: dict = Depends(auth.authorizedUser(["admin"]))):
    try:
        customers = helper.getAllCustomers()
        return {
            "status": status.HTTP_200_OK,
            "message": "Customers retrieved successfully",
            "customers": customers
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve customers, check logs"
        )

@router.get("/byID/{customer_id}", description="Gets a customer by id")
@limiter.limit("10/second")
async def getACustomerById(request: Request, customer_id: int, authorized_user: dict = Depends(auth.authorizedUser(["admin"]))):
    try:
        customer = helper.getCustomerByID(customer_id)
        return {
            "status": status.HTTP_200_OK,
            "message": "Customer retrieved successfully",
            "customer": customer
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve customer, check logs"
        )

@router.post("/create", description="Creates a customer")
@limiter.limit("10/second")
async def createCustomer(request: Request, customer: CustomerModel, authorized_user: dict = Depends(auth.authorizedUser(["admin", 'manager']))):
    try:
        createdCustomer = helper.createCustomer(customer.model_dump())
        return {
            "status": status.HTTP_200_OK,
            "message": "Customer created successfully",
            "customer": createdCustomer
        }

    except Exception as e:
        logger.error (f"Exception in createCustomer: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail="Not able to create the customer")

@router.post("/update", description="Updates a customer")
@limiter.limit("10/second")
async def updateCustomer(request: Request, customer: CustomerModel, authorized_user: dict = Depends(auth.authorizedUser(["admin", 'manager']))):
    try:
        updatedCustomer = helper.updateCustomer(customer.model_dump())
        return {
            "status": status.HTTP_200_OK,
            "message": "Customer updated successfully",
            "customer": updatedCustomer
        }

    except Exception as e:
        logger.error (f"Exception in updateCustomer: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail="Not able to update the customer")
