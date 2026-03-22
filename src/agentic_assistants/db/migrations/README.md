# Database Migrations

This directory contains Alembic migrations for the Agentic Assistants database schema.

## Setup

1. Configure your database connection in `.env`:
   ```
   DATABASE_TYPE=postgres
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   POSTGRES_DATABASE=agentic
   POSTGRES_USER=agentic
   POSTGRES_PASSWORD=your_password
   ```

2. Install dependencies:
   ```bash
   poetry install --extras databases
   ```

## Creating Migrations

Generate a new migration:
```bash
cd src/agentic_assistants/db/migrations
alembic revision -m "description of changes"
```

Auto-generate from model changes:
```bash
alembic revision --autogenerate -m "description"
```

## Running Migrations

Apply all pending migrations:
```bash
alembic upgrade head
```

Revert last migration:
```bash
alembic downgrade -1
```

## Migration from SQLite to PostgreSQL

1. Export SQLite data:
   ```bash
   python scripts/migrate_to_postgres.py export
   ```

2. Run PostgreSQL migrations:
   ```bash
   alembic upgrade head
   ```

3. Import data:
   ```bash
   python scripts/migrate_to_postgres.py import
   ```
