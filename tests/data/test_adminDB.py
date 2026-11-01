import pytest
from unittest.mock import patch, MagicMock
from app.data import adminDB

@patch('app.data.adminDB.database.get_connection')
def test_execute_success(mock_get_conn):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_conn.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    script = {"query": "SELECT 1"}
    result = adminDB.execute(script)
    mock_cursor.execute.assert_called_once_with("SELECT 1")
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called()
    mock_conn.close.assert_called()
    assert result is True

@patch('app.data.adminDB.database.get_connection')
@patch('app.data.adminDB.logger')
def test_execute_query_exception(mock_logger, mock_get_conn):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_conn.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.execute.side_effect = Exception("Query error")
    script = {"query": "SELECT 1"}
    result = adminDB.execute(script)
    assert result is False
    assert mock_logger.error.call_count >= 2
    mock_cursor.close.assert_called()
    mock_conn.close.assert_called()

@patch('app.data.adminDB.database.get_connection')
def test_execute_resource_cleanup_on_exception(mock_get_conn):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_conn.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.commit.side_effect = Exception("Commit error")
    script = {"query": "SELECT 1"}
    result = adminDB.execute(script)
    assert result is False
    mock_cursor.close.assert_called()
    mock_conn.close.assert_called()