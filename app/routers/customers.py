from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import logging
from ..biz import customersHelper as helper

from ..auth import get_current_user
from ..utils import isAuthorized

####### Logger ############
logger = logging.getLogger("tww.service.customers")

router = APIRouter(
    prefix="/api/v1/customers",  # all routes start with /customers
    tags=["Customers"]    # OpenAPI grouping
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

from pydantic import BaseModel

class CustomerModel (BaseModel):
    customer_id: str
    customer_name: str
    phone: str
    email: str
    city: str
    area: str
    state: str
    country: str
    zip_code: str

@router.get("/", description="Gets all customers")
async def getAllCustomers(current_user: dict = Depends(get_current_user)):
    # Check if current user is admin
    if isAuthorized(current_user, ["admin"]) == False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="not authorized"
        )
        
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
async def getACustomerById(customer_id: int, current_user: dict = Depends(get_current_user)):
    # Check if current user is admin
    if isAuthorized(current_user, ["admin"]) == False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="not authorized"
        )
        
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

@router.post("/create")
async def createCustomer(customer: CustomerModel, current_user: dict = Depends(get_current_user)):
    if isAuthorized(current_user, ["admin", 'manager']) == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
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

@router.post("/update")
async def updateCustomer(customer: CustomerModel, current_user: dict = Depends(get_current_user)):
    if isAuthorized(current_user, ["admin", 'manager']) == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
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
