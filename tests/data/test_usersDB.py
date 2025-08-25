import pytest
from unittest.mock import patch, MagicMock
from app.data import usersDB

@pytest.fixture
def mock_db_connection():
    with patch('app.data.database.get_connection') as mock_conn:
        mock_cursor = MagicMock()
        mock_conn.return_value.cursor.return_value = mock_cursor
        yield mock_conn, mock_cursor

def test_query_user_found(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.fetchone.return_value = {
        'user_id': 1,
        'username': 'john',
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john@example.com',
        'phone': '1234567890',
        'booking_commission': 10,
        'password': 'hashed'
    }
    result = usersDB.queryUserDB('john')
    mock_cursor.execute.assert_called_once_with("SELECT user_id, username, first_name, last_name, email, phone, booking_commission, password FROM users WHERE username=%s", ('john',))
    assert result['username'] == 'john'
    mock_cursor.close.assert_called_once()
    mock_conn.return_value.close.assert_called_once()

def test_query_user_not_found(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.fetchone.return_value = None
    result = usersDB.queryUserDB('unknown')
    assert result is None
    mock_cursor.close.assert_called_once()
    mock_conn.return_value.close.assert_called_once()

def test_query_user_by_id_found(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.fetchone.return_value = {
        'user_id': 2,
        'username': 'jane',
        'first_name': 'Jane',
        'last_name': 'Smith',
        'email': 'jane@example.com',
        'phone': '9876543210',
        'booking_commission': 15
    }
    result = usersDB.queryUserByIdDB(2)
    mock_cursor.execute.assert_called_once_with("SELECT user_id, username, first_name, last_name, email, phone, booking_commission FROM users WHERE user_id = %s", (2,))
    assert result['username'] == 'jane'
    mock_cursor.close.assert_called_once()
    mock_conn.return_value.close.assert_called_once()

def test_query_user_by_id_not_found(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.fetchone.return_value = None
    result = usersDB.queryUserByIdDB(99)
    assert result is None
    mock_cursor.close.assert_called_once()
    mock_conn.return_value.close.assert_called_once()

def test_persist_user(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.lastrowid = 5
    user = {
        'username': 'alice',
        'hashed_password': 'hashedpw',
        'first_name': 'Alice',
        'last_name': 'Wonder',
        'email': 'alice@example.com',
        'phone': '5551234567',
        'booking_commission': 20
    }
    result = usersDB.persistUserDB(user)
    mock_cursor.execute.assert_called_once()
    mock_conn.return_value.commit.assert_called_once()
    assert result['user_id'] == 5
    mock_cursor.close.assert_called_once()
    mock_conn.return_value.close.assert_called_once()

def test_update_user_detail_success(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    user = {
        'user_id': 1,
        'username': 'john',
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john@example.com',
        'phone': '1234567890',
        'booking_commission': 10
    }
    result = usersDB.updateUserDetailDB(user)
    mock_cursor.execute.assert_called_once()
    mock_conn.return_value.commit.assert_called_once()
    assert result['user_id'] == 1
    mock_cursor.close.assert_called_once()
    mock_conn.return_value.close.assert_called_once()

def test_update_user_detail_error(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    user = {
        'user_id': 1,
        'username': 'john',
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john@example.com',
        'phone': '1234567890',
        'booking_commission': 10
    }
    mock_cursor.execute.side_effect = Exception('DB Error')
    with patch('app.data.usersDB.logger') as mock_logger:
        with pytest.raises(Exception):
            usersDB.updateUserDetailDB(user)
        mock_logger.error.assert_called()
    mock_conn.return_value.rollback.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.return_value.close.assert_called_once()

def test_query_roles_for_user_found(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.fetchall.return_value = [('admin',), ('agent',)]
    with patch('app.data.usersDB.convertTupleToList', return_value=['admin', 'agent']):
        result = usersDB.queryRolesForUserDB('john')
        mock_cursor.execute.assert_called_once()
        assert result == ['admin', 'agent']
    mock_cursor.close.assert_called_once()
    mock_conn.return_value.close.assert_called_once()

def test_query_roles_for_user_not_found(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.fetchall.return_value = []
    result = usersDB.queryRolesForUserDB('unknown')
    assert result == []
    mock_cursor.close.assert_called_once()
    mock_conn.return_value.close.assert_called_once()

def test_query_all_users(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.fetchall.return_value = [
        {'user_id': 1, 'username': 'john', 'first_name': 'John', 'last_name': 'Doe', 'email': 'john@example.com', 'phone': '1234567890', 'booking_commission': 10},
        {'user_id': 2, 'username': 'jane', 'first_name': 'Jane', 'last_name': 'Smith', 'email': 'jane@example.com', 'phone': '9876543210', 'booking_commission': 15}
    ]
    result = usersDB.queryAllUsersDB()
    mock_cursor.execute.assert_called_once_with("SELECT user_id, username, first_name, last_name, email, phone, booking_commission FROM users ORDER BY first_name DESC")
    assert isinstance(result, list)
    assert result[0]['username'] == 'john'
    mock_cursor.close.assert_called_once()
    mock_conn.return_value.close.assert_called_once()

def test_assign_roles_to_user_success(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    with patch('app.data.usersDB.queryUserDB', return_value={'user_id': 1, 'username': 'john'}):
        with patch('app.data.usersDB.logger') as mock_logger:
            usersDB.assignRolesToUserDB('john', ['admin', 'agent'])
            mock_cursor.execute.assert_called_once()
            mock_conn.return_value.commit.assert_called_once()
            mock_logger.info.assert_called()
    mock_cursor.close.assert_called_once()
    mock_conn.return_value.close.assert_called_once()

def test_assign_roles_to_user_user_not_found(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    with patch('app.data.usersDB.queryUserDB', return_value=None):
        with patch('app.data.usersDB.logger') as mock_logger:
            with pytest.raises(Exception) as exc:
                usersDB.assignRolesToUserDB('unknown', ['admin'])
            assert str(exc.value) == 'User not found'
            mock_logger.error.assert_called()
    mock_conn.return_value.rollback.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.return_value.close.assert_called_once()