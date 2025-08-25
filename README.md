# TWW Service API - README

## Project Structure
```
app/
  ├── main.py           # FastAPI app entry point
  ├── routers/
  │     ├── admin.py
  │     ├── booking.py
  │     ├── customers.py
  │     ├── login.py
  │     ├── payments.py
  │     ├── roles.py
  │     ├── rooms.py
  │     ├── users.py
  │     └── reports.py
  ├── data/
  │     ├── database.py
  │     └── ...
  ├── helpers/
  │     ├── users.py
  │     ├── booking.py
  │     ├── payments.py
  │     └── admin.py
  ├── config.py          # Configuration loader
  └── ...
tests/
  ├── test_main.py
  ├── data/
  │     └── test_database.py
  └── ...
```
  
## Routers Documentation

### 1. Admin Router (`/api/admin`)
- **Endpoints:**
  - `GET /api/admin/list` - List all admins
    - **Params:** None
    - **Returns:** JSON array of admin objects
  - `POST /api/admin/create` - Create new admin
    - **Params:** JSON body (admin details)
    - **Returns:** Created admin object or error

### 2. Booking Router (`/api/booking`)
- **Endpoints:**
  - `GET /api/booking/list` - List bookings
    - **Params:** Optional query params (date, user)
    - **Returns:** JSON array of bookings
  - `POST /api/booking/create` - Create booking
    - **Params:** JSON body (booking details)
    - **Returns:** Booking object or error

### 3. Customers Router (`/api/customers`)
- **Endpoints:**
  - `GET /api/customers/list` - List customers
    - **Params:** None
    - **Returns:** JSON array of customers

### 4. Login Router (`/api/login`)
- **Endpoints:**
  - `POST /api/login` - Authenticate user
    - **Params:** JSON body (username, password)
    - **Returns:** Auth token or error

### 5. Payments Router (`/api/payments`)
- **Endpoints:**
  - `GET /api/payments/list` - List payments
    - **Params:** Optional query params (user, date)
    - **Returns:** JSON array of payments
  - `POST /api/payments/create` - Create payment
    - **Params:** JSON body (payment details)
    - **Returns:** Payment object or error

### 6. Roles Router (`/api/roles`)
- **Endpoints:**
  - `GET /api/roles/list` - List roles
    - **Params:** None
    - **Returns:** JSON array of roles
  - `POST /api/roles/create` - Create role
    - **Params:** JSON body (role details)
    - **Returns:** Role object or error

### 7. Rooms Router (`/api/rooms`)
- **Endpoints:**
  - `GET /api/rooms/list` - List rooms
    - **Params:** Optional query params (type, availability)
    - **Returns:** JSON array of rooms
  - `POST /api/rooms/create` - Create room
    - **Params:** JSON body (room details)
    - **Returns:** Room object or error

### 8. Users Router (`/api/users`)
- **Endpoints:**
  - `GET /api/users/list` - List users
    - **Params:** None
    - **Returns:** JSON array of users
  - `POST /api/users/create` - Create user
    - **Params:** JSON body (user details)
    - **Returns:** User object or error
  - `POST /api/users/google-auth` - Google authentication
    - **Params:** JSON body (Google token)
    - **Returns:** Auth token or error

### 9. Reports Router (`/api/reports`)
- **Endpoints:**
  - `GET /api/reports/metrics` - Prometheus metrics
    - **Params:** None
    - **Returns:** Metrics data (text/plain)

## Return Types
- All endpoints return JSON objects unless specified (metrics endpoint returns text/plain).
- Error responses follow FastAPI's standard error format with status code and detail.

## Environment Configuration
Create a `.env` file with the following variables:
```
MYSQL_HOST=your_mysql_host
MYSQL_PORT=your_mysql_port
MYSQL_USER=your_mysql_user
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=your_database_name
ALLOWED_ORIGINS=http://localhost:3000,http://your-frontend-domain
PROMETHEUS_ENABLED=true LOG_LEVEL=INFO
```
- Adjust values as needed for your environment.
- For Railway.app, set these variables in the Railway environment settings.

## Local Setup
1. **Clone the repository:**
```bash
git clone https://github.com/your-org/tww-service.git
cd tww-service
```

2. **Create and activate virtual environment:**
```bash
python -m venv venv
venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure .env file:**
```
- Copy `.env.example` to `.env` and fill in your values.
```

5. **Run the application:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

6. **Access API:**
   - Open [http://localhost:8000/docs](http://localhost:8000/docs) for Swagger UI.

## Deploy on Railway.app
1. **Import your repository into Railway.**
2. **Set environment variables:**
   - Go to project settings > Variables, add all required `.env` keys.
3. **Configure service:**
   - Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. **Deploy:**
   - Railway will build and deploy automatically.
5. **Access API:**
   - Use the Railway-provided domain to access your API and docs.

## Additional Notes
- Ensure your MySQL database is accessible from Railway (use Railway's built-in database or configure external access).
- Update CORS origins in `.env` to match your frontend domain.
- For metrics, enable Prometheus in `.env` and access `/api/reports/metrics`.

---
For further details, refer to the codebase and router modules for specific parameter and response structures.

## Monitoring
- Access Prometheus metrics at `/api/reports/metrics`.
- Use Grafana for visualization.

## Contributing
- Fork the repository.
- Create a new branch.
- Submit a pull request.

## License
- MIT License. See `LICENSE` file for details.
