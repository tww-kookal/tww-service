from fastapi import APIRouter, HTTPException, Depends, status
from ..biz import accounting as helper
from datetime import date
from fastapi.security import OAuth2PasswordBearer
from .. import auth
import logging
import traceback

router = APIRouter(prefix="/api/v1/accounting", tags=["Accounting"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

####### Logger ############
logger = logging.getLogger("tww.service.accounting")

# Category Endpoints
@router.get("/categories")
def list_categories(authorized_user: dict = Depends(auth.authorizedUser(["manager", "employee", "owner"]))):
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
    
@router.post("/expense/add")
def add_expense(expense: dict, authorized_user: dict = Depends(auth.authorizedUser(["manager", "employee", "owner"]))):
    try:
        return {
            "status": status.HTTP_201_CREATED,
            "message": "Expense added",
            "createdExpense": helper.createExpense(expense)            
        }
    except Exception as e:
        logger.error(f"Exception in add_expense: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/expense/update")
def update_expense(expense: dict, authorized_user: dict = Depends(auth.authorizedUser(["manager", "employee", "owner"]))):
    try:
        return {
            "status": status.HTTP_201_CREATED,
            "message": "Expense updated",
            "updatedExpense": helper.updateExpense(expense)            
        }
    except Exception as e:
        logger.error(f"Exception in update_expense: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/expense/deleteById/{expenseId}")
def delete_expense(expenseId: int, authorized_user: dict = Depends(auth.authorizedUser(["manager", "employee", "owner"]))):
    try:
        return {
            "status": status.HTTP_201_CREATED,
            "message": "Expense deleted",
            "deletedExpense": helper.deleteExpense(expenseId)            
        }
    except Exception as e:
        logger.error(f"Exception in update_expense: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/expenses")
def list_entries(authorized_user: dict = Depends(auth.authorizedUser(["manager", "owner"]))):
    try:
        return {
            "status": status.HTTP_200_OK,
            "message": "Success",
            "expenses": helper.getExpensesSince()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/expenses/{expenseDate}")
def list_entries(expenseDate: date, authorized_user: dict = Depends(auth.authorizedUser(["manager", "owner"]))):
    try:
        return {
            "status": status.HTTP_200_OK,
            "message": "Success",
            "expenses": helper.getExpensesSince(expenseDate)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/payment/forBookingID/{bookingId}")
def list_entries(bookingId: int, authorized_user: dict = Depends(auth.authorizedUser(["manager", "owner"]))):
    try:
        return {
            "status": status.HTTP_200_OK,
            "message": "Success",
            "payments": helper.getPaymentsForBooking(bookingId)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
