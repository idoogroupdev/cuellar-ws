# Dulceria Cuellar Backend

Dulceria Cuellar backend built with Django + GraphQL.

## Requirements

- Python 3.12+
- PostgreSQL

## Quick Start

```bash
cp .env.example .env
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py setup_roles
python manage.py runserver
```

## Environment Variables

Set these variables in `.env`:

- `SECRET_KEY`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `DB_HOST`
- `DB_PORT`

## Endpoints

- `http://localhost:8000/admin/`
- `http://localhost:8000/graphql/` (GraphiQL enabled)

## Tests

```bash
pytest
```
