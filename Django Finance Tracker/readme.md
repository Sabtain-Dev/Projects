# 💰 Django Finance Tracker

A full-stack finance management web application built with Django.

## Features

- User Authentication (Login/Register)
- Add Income & Expenses
- Dashboard with Financial Summary
- Goal Tracking System
- Delete Goals
- Export Transactions (CSV)
- Clean UI with Tailwind CSS

## Project Structure

- djfintracker (main project)
- finance (main app)
- templates (UI files)

- djfintracker/
- │
- ├── manage.py
- ├── requirements.txt
- ├── Procfile
- ├── README.md
- ├── .gitignore
- │
- ├── djfintracker/
- ├── finance/

## Installation

```bash
git clone https://github.com/yourusername/yourrepo.git
cd djfintracker
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Export Feature
Download your transaction data as CSV from:
```bash
/export-transactions/
```

## Tech Stack
- Django
- SQLite (development)
- Tailwind CSS