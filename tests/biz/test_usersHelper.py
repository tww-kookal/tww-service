import pytest
from app.biz import usersHelper
from app.biz.BizExceptions import DuplicateUserException, UserNotAvailableException
from unittest.mock import patch

# validateUser
@patch('app.biz.usersHelper.utils.verify_password')
def test_validateUser_valid(mock_verify):
    mock_verify.return_value = True
    user = {"password": "hashed"}
    assert usersHelper.validateUser(user, "plain") is True

@patch('app.biz.usersHelper.utils.verify_password')
def test_validateUser_invalid(mock_verify):
    mock_verify.return_value = False
    user = {"password": "hashed"}
    assert usersHelper.validateUser(user, "plain") is False
    assert usersHelper.validateUser(None, "plain") is False

# queryUser
@patch('app.biz.usersHelper.userDB.queryUserDB')
def test_queryUser_found(mock_query):
    mock_query.return_value = {"username": "test"}
    assert usersHelper.queryUser("test") == {"username": "test"}

@patch('app.biz.usersHelper.userDB.queryUserDB')
def test_queryUser_not_found(mock_query):
    mock_query.return_value = None
    assert usersHelper.queryUser("none") is None

# createUser
@patch('app.biz.usersHelper.userDB.queryUserDB')
@patch('app.biz.usersHelper.userDB.persistUserDB')
@patch('app.biz.usersHelper.utils.hash_password')
def test_createUser_success(mock_hash, mock_persist, mock_query):
    mock_query.return_value = None
    mock_persist.return_value = {"username": "new"}
    mock_hash.return_value = "hashed"
    user = {"username": "new", "password": "plain"}
    result = usersHelper.createUser(user)
    assert result["username"] == "new"

@patch('app.biz.usersHelper.userDB.queryUserDB')
def test_createUser_duplicate(mock_query):
    mock_query.return_value = {"username": "exists"}
    user = {"username": "exists"}
    with pytest.raises(DuplicateUserException):
        usersHelper.createUser(user)

@patch('app.biz.usersHelper.userDB.queryUserDB')
@patch('app.biz.usersHelper.userDB.persistUserDB')
@patch('app.biz.usersHelper.utils.hash_password')
def test_createUser_default_password(mock_hash, mock_persist, mock_query):
    mock_query.return_value = None
    mock_persist.return_value = {"username": "new"}
    mock_hash.return_value = "hashed"
    user = {"username": "new"}
    result = usersHelper.createUser(user)
    assert result["username"] == "new"
    assert "password" in user
    assert user["password"] == "password@123"

@patch('app.biz.usersHelper.userDB.queryUserDB')
@patch('app.biz.usersHelper.userDB.persistUserDB')
@patch('app.biz.usersHelper.utils.hash_password')
def test_createUser_default_commission(mock_hash, mock_persist, mock_query):
    mock_query.return_value = None
    mock_persist.return_value = {"username": "new", "booking_commission": 0.0}
    mock_hash.return_value = "hashed"
    user = {"username": "new", "password": "plain"}
    result = usersHelper.createUser(user)
    assert result["username"] == "new"
    assert "booking_commission" in user
    assert user["booking_commission"] == 0.0

@patch('app.biz.usersHelper.userDB.queryUserByIdDB')
@patch('app.biz.usersHelper.userDB.updateUserDetailDB')
def test_updateUserDetail_success(mock_update, mock_query):
    mock_query.return_value = {"user_id": 1}
    mock_update.return_value = {"user_id": 1, "booking_commission": 0.0}
    user = {"user_id": 1}
    result = usersHelper.updateUserDetail(user)
    assert result["user_id"] == 1

@patch('app.biz.usersHelper.userDB.queryUserByIdDB')
def test_updateUserDetail_not_found(mock_query):
    mock_query.return_value = None
    user = {"user_id": 2}
    with pytest.raises(UserNotAvailableException):
        usersHelper.updateUserDetail(user)

@patch('app.biz.usersHelper.userDB.queryUserByIdDB')
@patch('app.biz.usersHelper.userDB.updateUserDetailDB')
def test_updateUserDetail_default_commission(mock_update, mock_query):
    mock_query.return_value = {"user_id": 1}
    mock_update.return_value = {"user_id": 1, "booking_commission": 0.0}
    user = {"user_id": 1}
    result = usersHelper.updateUserDetail(user)
    assert result["user_id"] == 1
    assert "booking_commission" in user
    assert user["booking_commission"] == 0.0

@patch('app.biz.usersHelper.userDB.queryUserByIdDB')
def test_getUserByID_found(mock_query):
    mock_query.return_value = {"user_id": 1}
    assert usersHelper.getUserByID(1) == {"user_id": 1}

@patch('app.biz.usersHelper.userDB.queryUserByIdDB')
def test_getUserByID_not_found_throw(mock_query):
    mock_query.return_value = None
    with pytest.raises(UserNotAvailableException):
        usersHelper.getUserByID(2)

@patch('app.biz.usersHelper.userDB.queryUserByIdDB')
def test_getUserByID_not_found_no_throw(mock_query):
    mock_query.return_value = None
    assert usersHelper.getUserByID(2, throw_exception=False) is None

@patch('app.biz.usersHelper.userDB.queryUserDB')
def test_getUserByUserName_found(mock_query):
    mock_query.return_value = {"username": "test"}
    assert usersHelper.getUserByUserName("test") == {"username": "test"}

@patch('app.biz.usersHelper.userDB.queryUserDB')
def test_getUserByUserName_not_found_throw(mock_query):
    mock_query.return_value = None
    with pytest.raises(UserNotAvailableException):
        usersHelper.getUserByUserName("none")

@patch('app.biz.usersHelper.userDB.queryUserDB')
def test_getUserByUserName_not_found_no_throw(mock_query):
    mock_query.return_value = None
    assert usersHelper.getUserByUserName("none", throw_exception=False) is None

@patch('app.biz.usersHelper.getUserByID')
def test_getFullNameOfUserByID_found(mock_get):
    mock_get.return_value = {"first_name": "John", "last_name": "Doe"}
    assert usersHelper.getFullNameOfUserByID(1) == "John Doe"

@patch('app.biz.usersHelper.getUserByID')
def test_getFullNameOfUserByID_not_found(mock_get):
    mock_get.return_value = None
    assert usersHelper.getFullNameOfUserByID(2) == ""

@patch('app.biz.usersHelper.userDB.queryRolesForUserDB')
def test_getRolesForUser(mock_query):
    mock_query.return_value = ["admin", "user"]
    assert usersHelper.getRolesForUser("test") == ["admin", "user"]