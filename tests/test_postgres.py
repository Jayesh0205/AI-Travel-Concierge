from sqlalchemy import inspect, text

from database.pg_database import engine, check_postgres_connection


def test_postgres_connection():
    assert check_postgres_connection() is True


def test_postgres_version():
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT version()")
        ).scalar()

    assert "PostgreSQL" in result


def test_required_tables_exist():
    inspector = inspect(engine)

    tables = set(inspector.get_table_names())

    expected_tables = {
        "users",
        "trips",
        "saved_searches",
        "api_activity",
    }

    assert expected_tables.issubset(tables)