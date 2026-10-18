# KanMind Backend

REST API for the KanMind kanban board, built with Django and Django REST Framework.
The frontend lives in a separate repository.

## Features

- User registration and login with token authentication
- (Boards and tasks will be added)

## Requirements

- Python 3.10+
- pip

## Setup

1. Clone the repository and enter the project folder:

```bash
git clone <your-repo-url>
cd kanmind-backend
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
```

Linux / macOS:

```bash
source venv/bin/activate
```

Windows (PowerShell):

```powershell
venv\Scripts\activate
```

3. Install the dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root (see `.env.example`) and set your own `SECRET_KEY`:

Linux / macOS:

```bash
cp .env.example .env
```

Windows (PowerShell):

```powershell
copy .env.example .env
```

You can generate a new secret key with:

```bash
python -c "from django.core.management.utils import get_random_secret_key as k; print(k())"
```

5. Create the database and start the server:

```bash
python manage.py migrate
python manage.py createsuperuser   # optional, for the admin area
python manage.py runserver
```

The API is available at `http://127.0.0.1:8000/api/`,
the admin area at `http://127.0.0.1:8000/admin/`.

## Authentication

Send the token in the header of every protected request:

```
Authorization: Token <your-token>
```

| Method | Endpoint             | Description                | Auth |
|--------|----------------------|----------------------------|------|
| POST   | `/api/registration/` | Register a user, get token | No   |
| POST   | `/api/login/`        | Log in, get token          | No   |
| GET    | `/api/boards/`       | List boards of the user    | Yes  |
| POST   | `/api/boards/`       | Create a board             | Yes  |
| GET    | `/api/boards/{id}/`  | Board with members & tasks | Owner or member |
| PATCH  | `/api/boards/{id}/`  | Update title and members   | Owner or member |
| DELETE | `/api/boards/{id}/`  | Delete a board             | Owner only |
| GET    | `/api/email-check/?email=` | Find a user by email address | Yes |

## Notes

- The email address is used as the username (stored in lowercase).
  When creating a superuser, enter the email address as the username to be
  able to log in through the API.
- The full name is stored in the user's `first_name` field.
- The `SECRET_KEY` is read from the `.env` file, which is not part of the
  repository.
- CORS is configured for the frontend on `127.0.0.1:5500` / `localhost:5500`
  (VS Code Live Server). Adjust `CORS_ALLOWED_ORIGINS` in `core/settings.py`
  if needed.
- The database (`db.sqlite3`) is not part of the repository.

## Tests

```bash
coverage run manage.py test
coverage report
```
