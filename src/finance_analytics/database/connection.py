"""
Database connection management for the finance analytics project.
"""

import os
from sqlalchemy import create_engine
from dotenv import load_dotenv


def get_engine():
    """
    Create and return a SQLAlchemy engine for PostgreSQL connection.

    Loads database configuration from environment variables.

    Returns:
        sqlalchemy.engine.Engine: Configured database engine

    Raises:
        RuntimeError: If required database environment variables are missing
    """
    load_dotenv()

    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")

    required_env_vars = {
        "DB_USER": DB_USER,
        "DB_PASSWORD": DB_PASSWORD,
        "DB_HOST": DB_HOST,
        "DB_PORT": DB_PORT,
        "DB_NAME": DB_NAME,
    }

    missing_env_vars = [
        name
        for name, value in required_env_vars.items()
        if not value
    ]

    if missing_env_vars:
        raise RuntimeError(
            "Missing required database environment variables: "
            + ", ".join(missing_env_vars)
        )

    DATABASE_URL = (
        f"postgresql://{DB_USER}:{DB_PASSWORD}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
    )

    return engine