# Maintenix – Maintenance & Asset Management

A beginner-friendly Django MVP for reporting maintenance issues, assigning technicians,
tracking repairs, and managing assets.

## Included
- Login, logout and basic user registration (new accounts are Reporters)
- Roles: Reporter, Technician, Manager, Admin
- Submit and view maintenance requests
- Manager dashboard and technician assignment
- Technician status updates
- Asset register (manage assets through Django admin)
- Search/filter requests by status
- Responsive HTML/CSS interface

## 1. Create and activate a virtual environment

Windows PowerShell:
```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

## 2. Install packages
```bash
python -m pip install -r requirements.txt
```

## 3. Create database tables
This project uses SQLite by default, so you can run it immediately:
```bash
python manage.py makemigrations
python manage.py migrate
```

### Optional: switch to MySQL
1. Create a database in MySQL:
```sql
CREATE DATABASE maintenix CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```
2. Open `maintenix/settings.py` and change `DB_ENGINE` to `mysql`, then set
   `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, and `DB_PORT` environment variables.
3. Install requirements and run migrations again.

For a quick Windows PowerShell session:
```powershell
$env:DB_ENGINE="mysql"
$env:DB_NAME="maintenix"
$env:DB_USER="root"
$env:DB_PASSWORD="your_mysql_password"
$env:DB_HOST="127.0.0.1"
$env:DB_PORT="3306"
python manage.py migrate
```

## 4. Create admin account
```bash
python manage.py createsuperuser
```

## 5. Run
```bash
python manage.py runserver
```
Open http://127.0.0.1:8000/

## 6. Set user roles
1. Log in using the superuser account.
2. Open http://127.0.0.1:8000/admin/
3. Open **Profiles** and change the role of users to `manager` or `technician`.
4. Create assets in **Assets**.
5. Use the normal dashboard to submit and process requests.

New registrations are assigned the `reporter` role automatically.

## Important notes
- This is a learning MVP, not a production-ready deployment.
- SQLite is the default to make first launch easy; MySQL is supported through settings.
- Before public deployment, configure a strong secret key, HTTPS, secure cookies,
  email notifications, file-upload validation, backups, and production static-file hosting.
- Never commit passwords or secret keys to GitHub.

## Quick demo (optional)
```bash
python manage.py migrate
python manage.py seed_demo      # creates reporter1 / tech1 / manager1 (password: demo12345)
python manage.py test           # run the permission tests
```
Superusers created with `createsuperuser` automatically get the `admin` role.
