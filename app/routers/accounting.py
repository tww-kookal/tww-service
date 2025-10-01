from fastapi import APIRouter, HTTPException, Depends, status, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from ..biz import accounting as helper
from datetime import date
from fastapi.security import OAuth2PasswordBearer
from .. import auth
import logging
import traceback

router = APIRouter(prefix="/api/v1/accounting", tags=["Accounting"])
limiter = Limiter(key_func=get_remote_address) #Incorporate Rate Limiter
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

####### Logger ############
logger = logging.getLogger("tww.service.accounting")

# Category Endpoints
@router.get("/categories")
@limiter.limit("10/second")
def list_categories(request: Request, authorized_user: dict = Depends(auth.authorizedUser(["manager", "employee", "owner"]))):
    try:
        return {
            "status": status.HTTP_200_OK,
            "message": "Success",
            "categories": helper.getAllAccountingCategories()
        }
    except Exception as e:
        logger.error(f"Exception in list_categories: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/transaction/add")
@limiter.limit("10/second")
def add_transaction(request: Request, transaction: dict, authorized_user: dict = Depends(auth.authorizedUser(["manager", "employee", "owner"]))):
    try:
        transaction['created_by'] = authorized_user['user_name']
        return {
            "status": status.HTTP_201_CREATED,
            "message": "Transaction added",
            "createdTransaction": helper.createTransaction(transaction)            
        }
    except Exception as e:
        logger.error(f"Exception in add_transaction: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/transaction/update")
@limiter.limit("10/second")
def update_transaction(request: Request, transaction: dict, authorized_user: dict = Depends(auth.authorizedUser(["manager", "employee", "owner"]))):
    try:
        transaction['created_by'] = authorized_user['user_name']
        return {
            "status": status.HTTP_201_CREATED,
            "message": "Transaction updated",
            "updatedTransaction": helper.updateTransaction(transaction)            
        }
    except Exception as e:
        logger.error(f"Exception in update_transaction: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/transaction/deleteById/{transactionId}")
@limiter.limit("10/second")
def delete_transaction(request: Request, transactionId: int, authorized_user: dict = Depends(auth.authorizedUser(["manager", "employee", "owner"]))):
    try:
        return {
            "status": status.HTTP_201_CREATED,
            "message": "Transaction deleted",
            "deletedTransaction": helper.deleteTransaction(transactionId)            
        }
    except Exception as e:
        logger.error(f"Exception in delete_transaction: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/transactions")
@limiter.limit("10/second")
def list_entries(request: Request, authorized_user: dict = Depends(auth.authorizedUser(["manager", "owner"]))):
    try:
        return {
            "status": status.HTTP_200_OK,
            "message": "Success",
            "transactions": helper.getTransactionsSince()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/transactions/{transactionDate}")
@limiter.limit("10/second")
def list_entries(request: Request, transactionDate: date, authorized_user: dict = Depends(auth.authorizedUser(["manager", "owner"]))):
    try:
        return {
            "status": status.HTTP_200_OK,
            "message": "Success",
            "transactions": helper.getTransactionsSince(transactionDate)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/payment/forBookingID/{bookingId}")
@limiter.limit("30/second")
def list_entries(request: Request, bookingId: int, authorized_user: dict = Depends(auth.authorizedUser(["manager", "owner"]))):
    try:
        return {
            "status": status.HTTP_200_OK,
            "message": "Success",
            "payments": helper.getPaymentsForBooking(bookingId)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
