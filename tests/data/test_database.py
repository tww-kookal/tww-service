import pytest
from app.data import database
import mysql.connector

class DummyConnection:
    pass

class DummyPool:
    def get_connection(self):
        return DummyConnection()

class DummyError(Exception):
    pass

def test_get_connection_success(monkeypatch):
    monkeypatch.setattr(database, "connection_pool", DummyPool())
    conn = database.get_connection()
    assert isinstance(conn, DummyConnection)

def test_get_connection_error(monkeypatch):
    class ErrorPool:
        def get_connection(self):
            raise mysql.connector.Error("Connection failed")
    monkeypatch.setattr(database, "connection_pool", ErrorPool())
    with pytest.raises(mysql.connector.Error):
        database.get_connection()