# 🗂️ Django CRM

A full-stack Customer Relationship Management web app built with Django 5, PostgreSQL, and Tailwind CSS. Includes Google Contacts integration, JWT-based auth, and a REST API layer.

## What It Does

- Manage customer records and contact data through a clean web UI
- Sync contacts with **Google Contacts API** via OAuth2
- Expose data through a **REST API** (Django REST Framework + JWT auth)
- Store time-series-friendly data using **TimescaleDB** (PostgreSQL extension)
- Serve static assets efficiently with **WhiteNoise**

---

## 🛠 Tech Stack

| Layer | Tools |
|---|---|
| Backend | Django 5.2 · Django REST Framework |
| Auth | JWT (SimpleJWT) · Google OAuth2 |
| Database | PostgreSQL · TimescaleDB |
| Frontend | Tailwind CSS · Flowbite |
| Package Management | uv |
| Code Quality | pre-commit |
| Static Files | WhiteNoise |

---

## 📁 Project Structure

```
django-crm/
├── src/                    # Django project source
├── requirements.prod.txt   # Auto-generated via uv export
├── pyproject.toml          # Project metadata and deps
├── rav.yaml                # Static file download config (Flowbite/Tailwind)
├── tailwind.config.js
├── .pre-commit-config.yaml
└── .python-version
```

---

## 🚀 How to Run

```bash
# 1. Clone the repo
git clone https://github.com/shris2810/django-crm.git
cd django-crm

# 2. Install dependencies with uv
uv sync

# 3. Set up environment variables
cp .env.example .env
# Fill in DB credentials, Google OAuth keys, SECRET_KEY

# 4. Run migrations
uv run python src/manage.py migrate

# 5. Download static vendor files (Flowbite/Tailwind)
rav run staticfiles_dev

# 6. Start the dev server
uv run python src/manage.py runserver
```

> Requires Python 3+ and a running PostgreSQL + TimescaleDB instance.

---

## 📌 Notes

- Google Contacts sync requires a Google Cloud project with the Contacts API enabled and OAuth2 credentials configured
- TimescaleDB must be enabled as a PostgreSQL extension before running migrations
- JWT tokens are used for API authentication — obtain via `/api/token/`
