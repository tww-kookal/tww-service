import pytest
from unittest.mock import patch
from app.biz import adminHelper

@patch('app.biz.adminHelper.adminDB.execute')
def test_execute_success(mock_execute):
    mock_execute.return_value = ['result']
    script = {'action': 'run'}
    result = adminHelper.execute(script)
    assert result == ['result']
    mock_execute.assert_called_once_with(script)

@patch('app.biz.adminHelper.adminDB.execute')
@patch('app.biz.adminHelper.logger')
def test_execute_exception(mock_logger, mock_execute):
    mock_execute.side_effect = Exception('DB error')
    script = {'action': 'run'}
    result = adminHelper.execute(script)
    assert result == []
    assert mock_logger.error.called

@patch('app.biz.adminHelper.adminDB.execute')
def test_execute_empty_script(mock_execute):
    mock_execute.return_value = []
    script = {}
    result = adminHelper.execute(script)
    assert result == []
    mock_execute.assert_called_once_with(script)