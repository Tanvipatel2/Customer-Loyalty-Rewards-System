# PerkBox — Customer Loyalty Rewards

A full-stack Django loyalty platform for a factory selling boxed products. Customers enter a unique code placed inside each genuine box to earn points, then redeem points for rewards. Factory staff can create code batches, monitor activity, manage rewards, and process claims.

## Features
- Customer registration, login, logout and personal dashboard
- Unique one-time product codes; duplicate redemption blocked by a database uniqueness constraint and atomic transaction
- Points wallet and immutable-style transaction history
- Rewards catalogue, stock tracking, pending claims, approval and rejection/refund workflow
- Owner dashboard with redemption and claim metrics
- Staff code-batch generation with downloadable CSV for packaging/printing
- Django admin for operational data review
- Responsive commercial-style UI

## Stack
- Python 3.11+ and Django 5.2
- SQLite for local demonstration
- Django templates, HTML, CSS and vanilla JavaScript

## Run locally (Windows PowerShell)
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
Copy-Item .env.example .env
py manage.py makemigrations rewards
py manage.py migrate
py manage.py createsuperuser
py manage.py runserver
```
Open http://127.0.0.1:8000/

For Ubuntu/macOS:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py makemigrations rewards
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## First-time demo setup
1. Create a superuser and sign in at `/accounts/login/`.
2. Open `/owner/` and use **Generate code batch**. Download the CSV and treat each code as a unique code printed under a scratch panel inside a sealed box.
3. In Django admin (`/admin/`), add reward catalogue entries (name, description, points cost, stock, active).
4. Register a customer in a separate browser/incognito window, redeem one code, and visit Rewards.
5. Request a reward. From the owner dashboard, approve or reject it. Rejection restores the points.

## Tests
Run `py manage.py test`. The automated suite covers one-time code redemption, duplicate prevention, point credit, reward claim, approval and rejection refund. See `TEST_PLAN.md`.

## Security and production notes
This is a local academic prototype. Set a strong secret key, `DEBUG=False`, and production `ALLOWED_HOSTS` before deployment. For production use PostgreSQL, HTTPS, email verification, CAPTCHA/rate limiting, audit logging, backup/monitoring, and a secure packaging workflow. Never expose generated code CSVs publicly. Codes are random and one-time, but the prototype does not integrate with factory ERP/POS or shipping systems.

## Repository delivery
Push the complete project to one public GitHub repository. Do not commit `.env`, database files, or generated customer code batches.
