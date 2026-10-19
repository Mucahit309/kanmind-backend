# KanMind Backend

REST API for the KanMind kanban board, built with Django and Django REST Framework.
The frontend lives in a separate repository.

## Features

- User registration and login with token authentication
- Boards with an owner and members
- Tasks with status, priority, assignee, reviewer and due date
- Comments on tasks
- Email lookup to find users when adding board members

## Requirements

- Python 3.x (developed and tested with Python 3.14)
- pip

The exact package versions are listed in `requirements.txt`.

## Setup

1. Clone the repository and enter the project folder:

```bash
git clone https://github.com/Mucahit309/kanmind-backend.git
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

All endpoints except registration and login require a token.
Send it in the header of every protected request:

```
Authorization: Token <your-token>
```

Requests without a valid token are answered with `401`.

## Endpoints

| Method | Endpoint                                 | Description                  | Permission                  |
|--------|------------------------------------------|------------------------------|-----------------------------|
| POST   | `/api/registration/`                     | Register a user, get token   | Public                      |
| POST   | `/api/login/`                            | Log in, get token            | Public                      |
| GET    | `/api/email-check/?email=`               | Find a user by email address | Authenticated               |
| GET    | `/api/boards/`                           | List boards of the user      | Authenticated               |
| POST   | `/api/boards/`                           | Create a board               | Authenticated               |
| GET    | `/api/boards/{id}/`                      | Board with members and tasks | Board owner or member       |
| PATCH  | `/api/boards/{id}/`                      | Update title and members     | Board owner or member       |
| DELETE | `/api/boards/{id}/`                      | Delete a board               | Board owner                 |
| GET    | `/api/tasks/assigned-to-me/`             | Tasks assigned to the user   | Authenticated               |
| GET    | `/api/tasks/reviewing/`                  | Tasks the user has to review | Authenticated               |
| POST   | `/api/tasks/`                            | Create a task                | Board owner or member       |
| PATCH  | `/api/tasks/{id}/`                       | Update a task                | Board owner or member       |
| DELETE | `/api/tasks/{id}/`                       | Delete a task                | Task creator or board owner |
| GET    | `/api/tasks/{id}/comments/`              | List comments of a task      | Board owner or member       |
| POST   | `/api/tasks/{id}/comments/`              | Add a comment to a task      | Board owner or member       |
| DELETE | `/api/tasks/{id}/comments/{comment_id}/` | Delete a comment             | Comment author              |

Allowed task values:

- `status`: `to-do`, `in-progress`, `review`, `done`
- `priority`: `low`, `medium`, `high`

## Notes

- The email address is used as the username (stored in lowercase).
  When creating a superuser, enter the email address as the username to be
  able to log in through the API.
- The full name is stored in the user's `first_name` field.
- Registration does not enforce Django's password validators.
- The owner of a board has the same access rights as a member, even if the
  owner is not listed in `members`. `member_count` only counts the entries in
  `members`.
- `assignee_id` and `reviewer_id` of a task must belong to a user who is the
  owner or a member of the board.
- The board of a task cannot be changed. Sending the same board id in a PATCH
  request is accepted, a different one is rejected with `400`.
- There is no general task list (`GET /api/tasks/`) and no single task
  endpoint (`GET /api/tasks/{id}/`), because they are not part of the API
  documentation and a general list would expose tasks of foreign boards.
- Tasks store their creator. Tasks without a creator (for example created in
  the admin area) can only be deleted by the board owner.
- Only the author of a comment can delete it, not even the board owner.
- Deleting a board also deletes its tasks and comments.
- The `SECRET_KEY` is read from the `.env` file, which is not part of the
  repository.
- CORS is configured for the frontend on `127.0.0.1:5500` / `localhost:5500`
  (VS Code Live Server). Adjust `CORS_ALLOWED_ORIGINS` in `core/settings.py`
  if needed.
- The database (`db.sqlite3`) is not part of the repository.

## Tests

```bash
python manage.py test
coverage run manage.py test
coverage report
```

Code style can be checked with:

```bash
flake8 . --exclude venv
```
