import os

import psycopg2
from dotenv import load_dotenv

from src.utils.config import load_config

load_dotenv()


def get_connection():
    """Create a PostgreSQL database connection."""

    config = load_config()
    database_config = config["database"]

    return psycopg2.connect(
        host=os.getenv("DB_HOST", database_config["host"]),
        port=os.getenv("DB_PORT", database_config["port"]),
        database=os.getenv("DB_NAME", database_config["name"]),
        user=os.getenv("DB_USER", database_config["user"]),
        password=os.getenv("DB_PASSWORD"),
    )
