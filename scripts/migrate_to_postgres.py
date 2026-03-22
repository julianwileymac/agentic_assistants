"""
Migration script for SQLite to PostgreSQL.

Usage:
    python scripts/migrate_to_postgres.py export
    python scripts/migrate_to_postgres.py import
    python scripts/migrate_to_postgres.py migrate
"""

import argparse
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

try:
    import psycopg
    PSYCOPG_AVAILABLE = True
except ImportError:
    PSYCOPG_AVAILABLE = False

from agentic_assistants.config import AgenticConfig
from agentic_assistants.utils.logging import get_logger

logger = get_logger(__name__)


def export_sqlite_data(db_path: Path, output_dir: Path) -> None:
    """Export data from SQLite to JSON files."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    # Get all tables
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cur.fetchall()]
    
    logger.info(f"Exporting {len(tables)} tables from SQLite")
    
    for table in tables:
        logger.info(f"Exporting table: {table}")
        
        cur.execute(f"SELECT * FROM {table}")
        rows = cur.fetchall()
        
        # Convert to list of dicts
        data = [dict(row) for row in rows]
        
        # Save to JSON
        output_file = output_dir / f"{table}.json"
        with open(output_file, "w") as f:
            json.dump(data, f, indent=2, default=str)
        
        logger.info(f"Exported {len(data)} rows from {table}")
    
    conn.close()
    logger.info("SQLite export completed")


def import_to_postgres(input_dir: Path, postgres_dsn: str) -> None:
    """Import data from JSON files to PostgreSQL."""
    if not PSYCOPG_AVAILABLE:
        raise ImportError("psycopg is required for PostgreSQL import")
    
    conn = psycopg.connect(postgres_dsn)
    cur = conn.cursor()
    
    # Get all JSON files
    json_files = list(input_dir.glob("*.json"))
    
    logger.info(f"Importing {len(json_files)} tables to PostgreSQL")
    
    for json_file in json_files:
        table_name = json_file.stem
        logger.info(f"Importing table: {table_name}")
        
        with open(json_file, "r") as f:
            data = json.load(f)
        
        if not data:
            logger.info(f"No data in {table_name}, skipping")
            continue
        
        # Get column names from first row
        columns = list(data[0].keys())
        placeholders = ", ".join(["%s"] * len(columns))
        column_names = ", ".join(columns)
        
        # Insert data
        insert_sql = f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})"
        
        for row in data:
            values = [row[col] for col in columns]
            try:
                cur.execute(insert_sql, values)
            except Exception as e:
                logger.error(f"Error inserting row into {table_name}: {e}")
                logger.error(f"Row data: {row}")
        
        conn.commit()
        logger.info(f"Imported {len(data)} rows into {table_name}")
    
    conn.close()
    logger.info("PostgreSQL import completed")


def migrate_direct() -> None:
    """Perform direct migration from SQLite to PostgreSQL."""
    config = AgenticConfig()
    
    sqlite_path = Path(config.data_dir) / "control_panel.db"
    if not sqlite_path.exists():
        logger.error(f"SQLite database not found: {sqlite_path}")
        return
    
    # Export SQLite
    export_dir = Path(config.data_dir) / "migration_export"
    logger.info(f"Exporting SQLite data to: {export_dir}")
    export_sqlite_data(sqlite_path, export_dir)
    
    # Import to PostgreSQL
    postgres_dsn = config.postgresql.dsn
    logger.info(f"Importing to PostgreSQL: {postgres_dsn}")
    import_to_postgres(export_dir, postgres_dsn)
    
    logger.info("Migration completed successfully")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Migrate SQLite to PostgreSQL")
    parser.add_argument(
        "action",
        choices=["export", "import", "migrate"],
        help="Action to perform",
    )
    parser.add_argument(
        "--sqlite-db",
        default="./data/control_panel.db",
        help="Path to SQLite database",
    )
    parser.add_argument(
        "--export-dir",
        default="./data/migration_export",
        help="Directory for export files",
    )
    parser.add_argument(
        "--postgres-dsn",
        help="PostgreSQL connection DSN",
    )
    
    args = parser.parse_args()
    
    if args.action == "export":
        export_sqlite_data(Path(args.sqlite_db), Path(args.export_dir))
    
    elif args.action == "import":
        if not args.postgres_dsn:
            config = AgenticConfig()
            postgres_dsn = config.postgresql.dsn
        else:
            postgres_dsn = args.postgres_dsn
        
        import_to_postgres(Path(args.export_dir), postgres_dsn)
    
    elif args.action == "migrate":
        migrate_direct()


if __name__ == "__main__":
    main()
