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
   - `DB_HOST`
   - `DB_USER`
   - `DB_PASSWORD`
   - `DB_NAME`
   - `SECRET_KEY`
5. Deploy from this GitHub repo.

## Default Login
- username: admin
- password: Admin@123
