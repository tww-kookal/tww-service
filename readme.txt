web: uvicorn app.main:app --host 0.0.0.0 --port $PORT

Maria Removed:
  mariadb --only-binary=:all:1.1.13

TWILIO - API - 
  ZMDJ9ML41QBGZPVZKXRMD6S1
  +14155238886
  key-load

run tests
  pytest 
  python -m pytest
  With Coverage
    python -m pytest --cov=app tests/
  
  Coverage
    coverage run -m pytest
    coverage report -m


  Specific File
    python -m pytest tests/test_auth_google.py

  Verbose 
    python -m pytest -v

  Stop on First Failure
    python -m pytest -x