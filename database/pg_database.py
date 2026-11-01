import os

from dotenv import load_dotenv
from sqlalchemy import URL, create_engine
from sqlalchemy.orm import sessionmaker

from database.pg_models import Base

load_dotenv(override=True)


def get_database_url():
    required = [
        "PGUSER",
        "PGPASSWORD",
        "PGHOST",
        "PGPORT",
        "PGDATABASE",
    ]

    missing = [key for key in required if not os.getenv(key)]

    if missing:
        raise RuntimeError(
            f"Missing PostgreSQL settings: {', '.join(missing)}"
        )

    return URL.create(
        "postgresql+psycopg",
        username=os.getenv("PGUSER"),
        password=os.getenv("PGPASSWORD"),
        host=os.getenv("PGHOST"),
        port=int(os.getenv("PGPORT")),
        database=os.getenv("PGDATABASE"),
    )


engine = create_engine(
    get_database_url(),
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)


def initialize_postgres():
    """Create NovaTrip's PostgreSQL tables if they do not exist."""
    Base.metadata.create_all(bind=engine)


def check_postgres_connection():
    """Return True when PostgreSQL is reachable."""
    with engine.connect() as connection:
        connection.exec_driver_sql("SELECT 1")

    return True