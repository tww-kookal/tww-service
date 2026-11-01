import pytest
from unittest.mock import patch
from datetime import datetime, timedelta
from jose import jwt
from app.utils import hash_password, verify_password, create_access_token
from app.config.config import settings

def test_hash_password():
    password = "testpassword"
    hashed = hash_password(password)
    assert hashed is not None
    assert isinstance(hashed, str)
    assert hashed != password

def test_verify_password():
    password = "testpassword"
    hashed = hash_password(password)
    assert verify_password(password, hashed) is True
    assert verify_password("wrongpassword", hashed) is False

def test_create_access_token():
    data = {"sub": "testuser"}
    token = create_access_token(data)
    assert token is not None
    decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert decoded_token["sub"] == "testuser"
    assert "exp" in decoded_token

def test_create_access_token_with_expires():
    data = {"sub": "testuser"}
    expires = timedelta(minutes=30)
    token = create_access_token(data, expires_delta=expires)
    decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert decoded_token["sub"] == "testuser"
    expiration_time = datetime.utcfromtimestamp(decoded_token["exp"])
    assert expiration_time > datetime.utcnow()
    assert expiration_time < datetime.utcnow() + expires

def test_create_access_token_default_expiry():
    data = {"sub": "testuser"}
    token = create_access_token(data)
    decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    expiration_time = datetime.utcfromtimestamp(decoded_token["exp"])
    expected_expiration = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    assert abs(expiration_time - expected_expiration) < timedelta(seconds=5)