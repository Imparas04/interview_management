# Interview Management System — Phase 1

## Setup (Windows)

1. Extract this zip to your desired folder (e.g. Desktop).
2. Open cmd/terminal inside the extracted `interview_management` folder.
3. Create and activate a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate
   ```
4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
5. Open `.env` and set `DB_PASSWORD` to your actual MySQL root password
   (and change `SECRET_KEY` to any random string).
6. Create the MySQL database (in MySQL shell or Workbench):
   ```sql
   CREATE DATABASE interview_management_db CHARACTER SET utf8mb4;
   ```
7. Generate and apply migrations:
   ```
   python manage.py makemigrations
   python manage.py migrate
   ```
8. Create a superuser:
   ```
   python manage.py createsuperuser
   ```
9. Run the server:
   ```
   python manage.py runserver
   ```
10. Visit `http://127.0.0.1:8000/admin/` and log in. You should see
    **Users** with a **Role** field (admin/hr/interviewer/candidate).

## Notes
- `Django>=5.2,<6.0` is pinned in `requirements.txt` on purpose — Django 6.1
  requires MySQL 8.4+, and most local installs are still on MySQL 8.0.x.
- Never commit `.env` — it's already in `.gitignore`.
- Next: say "START PHASE 2" in chat for JWT login, registration, and
  role-based permissions.
