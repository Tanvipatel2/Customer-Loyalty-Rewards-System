@echo off
py -m venv .venv
call .venv\Scripts\activate
py -m pip install -r requirements.txt
if not exist .env copy .env.example .env
py manage.py makemigrations rewards
py manage.py migrate
py manage.py runserver
pause
