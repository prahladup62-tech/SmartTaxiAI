# Ananya Travel / SmartTaxiAI

A professional taxi booking website built with Flask, SQLite, and Bootstrap.

## Features
- User registration and login
- Customer dashboard and profile
- Booking form with trip options
- Admin panel for bookings, users, cars, and reviews
- Mobile-friendly responsive design

## Setup
1. Create a Python virtual environment:

```bash
python -m venv venv
```

2. Activate it:

```powershell
venv\Scripts\Activate.ps1
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run the application:

```bash
python app.py
```

5. Open your browser at:

```text
http://127.0.0.1:5000
```

## Admin Access
- Username: `admin`
- Password: `admin123`

## Notes
- The database file `database.db` is created automatically on first run.
- To change admin credentials, set the environment variables `ADMIN_USERNAME` and `ADMIN_PASSWORD`.
