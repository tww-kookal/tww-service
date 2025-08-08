# FastAPI Hotel Booking API

This project is a modular FastAPI application for hotel booking, including:
- OAuth2 login
- Room availability
- Booking system
- User & Role management
- Reporting

## Deployment on Railway
1. Create a new project in Railway.
2. Add a MySQL service.
3. Import `sql/hotel_schema.sql` into your MySQL instance.
4. Add environment variables:
   - `MYSQL_HOST`
   - `MYSQL_USER`
   - `MYSQL_PASSWORD`
   - `MYSQL_DATABASE`
   - `SECRET_KEY`
   - `ALGORITHM`
   - `ACCESS_TOKEN_EXPIRE_MINUTES`
   - `APP_ENV`

5. Deploy from this GitHub repo.

## Default Login
- username: admin
- password: Admin@123
