from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class Base(DeclarativeBase):
    pass


engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=settings.DEBUG,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables and enable pgvector."""
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialised — all tables created.")


def verify_vector_dimension():
    """Validate that stored chunks match configured VECTOR_DIMENSION."""
    with engine.connect() as conn:
        result = conn.execute(
            text(
                "SELECT atttypmod FROM pg_attribute "
                "JOIN pg_class ON pg_class.oid = pg_attribute.attrelid "
                "WHERE pg_class.relname = 'document_chunks' "
                "AND pg_attribute.attname = 'embedding'"
            )
        ).fetchone()
        if result:
            dim = result[0]
            if dim != settings.VECTOR_DIMENSION:
                raise RuntimeError(
                    f"VECTOR_DIMENSION mismatch: schema={dim}, "
                    f"config={settings.VECTOR_DIMENSION}. "
                    "Update VECTOR_DIMENSION in .env or recreate the table."
                )
    logger.info(f"Vector dimension verified: {settings.VECTOR_DIMENSION}")
