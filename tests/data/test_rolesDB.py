import pytest
from unittest.mock import patch, MagicMock
from app.data import rolesDB

@pytest.fixture
def mock_db_connection():
    with patch('app.data.database.get_connection') as mock_conn:
        mock_cursor = MagicMock()
        mock_conn.return_value.cursor.return_value = mock_cursor
        yield mock_conn, mock_cursor

def test_persist_role_success(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    with patch('app.data.rolesDB.queryRoleByNameDB', return_value=None):
        rolesDB.persistRoleDB('admin')
        mock_cursor.execute.assert_called_once_with("INSERT INTO roles (role_name) VALUES (%s)", ('admin',))
        mock_conn.return_value.commit.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.return_value.close.assert_called_once()

def test_persist_role_already_exists(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    with patch('app.data.rolesDB.queryRoleByNameDB', return_value=1):
        with pytest.raises(Exception) as exc:
            rolesDB.persistRoleDB('admin')
        assert str(exc.value) == "Role already exists"
        mock_cursor.execute.assert_not_called()
        mock_conn.return_value.commit.assert_not_called()
        mock_cursor.close.assert_called_once()
        mock_conn.return_value.close.assert_called_once()

def test_query_role_by_name_found(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.fetchone.return_value = 2
    result = rolesDB.queryRoleByNameDB('user')
    mock_cursor.execute.assert_called_once_with("SELECT role_id FROM roles WHERE role_name = %s", ('user',))
    assert result == 2
    mock_cursor.close.assert_called_once()
    mock_conn.return_value.close.assert_called_once()

def test_query_role_by_name_not_found(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.fetchone.return_value = None
    result = rolesDB.queryRoleByNameDB('guest')
    mock_cursor.execute.assert_called_once_with("SELECT role_id FROM roles WHERE role_name = %s", ('guest',))
    assert result is None
    mock_cursor.close.assert_called_once()
    mock_conn.return_value.close.assert_called_once()

def test_query_roles_db(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.fetchall.return_value = [
        {'role_id': 1, 'role_name': 'admin'},
        {'role_id': 2, 'role_name': 'user'}
    ]
    result = rolesDB.queryRolesDB()
    mock_cursor.execute.assert_called_once_with("SELECT role_id, role_name FROM roles")
    assert isinstance(result, list)
    assert result[0]['role_name'] == 'admin'
    assert result[1]['role_id'] == 2
    mock_cursor.close.assert_called_once()
    mock_conn.return_value.close.assert_called_once()