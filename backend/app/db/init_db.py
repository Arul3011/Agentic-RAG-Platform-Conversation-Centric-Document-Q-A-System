"""
Initializes the database: enables pgvector, validates the configured
embedding dimension, creates ORM tables, then applies raw-SQL migrations
for full-text search and vector indexes.

Run with: python -m app.db.init_db
"""
from pathlib import Path

from sqlalchemy import text

import app.models  # noqa: F401  (ensures models are registered on Base.metadata)
from app.core.logging import configure_logging, get_logger
from app.db.database import Base, engine, ensure_pgvector_extension, validate_vector_dimension

configure_logging()
logger = get_logger(__name__)

MIGRATIONS_DIR = Path(__file__).parent / "migrations"


def run_sql_migrations() -> None:
    with engine.connect() as conn:
        for sql_file in sorted(MIGRATIONS_DIR.glob("*.sql")):
            logger.info("Applying migration %s", sql_file.name)
            sql = sql_file.read_text()
            conn.execute(text(sql))
            conn.commit()


def init_db() -> None:
    logger.info("Ensuring pgvector extension...")
    ensure_pgvector_extension()

    logger.info("Validating VECTOR_DIMENSION against embedding model...")
    validate_vector_dimension()

    logger.info("Creating ORM tables...")
    Base.metadata.create_all(bind=engine)

    logger.info("Running raw SQL migrations (FTS, indexes)...")
    run_sql_migrations()

    logger.info("Database initialization complete.")


if __name__ == "__main__":
    init_db()
