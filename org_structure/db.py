import os
import psycopg

from dotenv import load_dotenv

load_dotenv()

DEFAULT_DSN = (
    f"postgresql://{os.environ.get('POSTGRES_USER', 'org_structure')}:"
    f"{os.environ.get('POSTGRES_PASSWORD', 'org_structure')}"
    f"@localhost:{os.environ.get('POSTGRES_PORT', '5432')}"
    f"/{os.environ.get('POSTGRES_DB', 'org_structure')}"
)

_LIBPQ_ENV_VARS = ("PGHOST", "PGPORT", "PGUSER", "PGPASSWORD", "PGDATABASE")


def get_connection(dsn: str | None = None):
    """
    Открывает соединение с PostgreSQL.

    Приоритет источников параметров подключения:
    1. явный `dsn`, переданный вызывающим кодом (например, флаг --dsn CLI);
    2. стандартные переменные окружения libpq (PGHOST, PGPORT, PGUSER,
       PGPASSWORD, PGDATABASE) — их psycopg.connect() читает сам;
    3. DEFAULT_DSN, собранный из POSTGRES_* переменных (.env или окружение)
       с дефолтами локального docker-compose из этого репозитория.
    """
    if dsn:
        return psycopg.connect(dsn)
    if any(os.environ.get(var) for var in _LIBPQ_ENV_VARS):
        return psycopg.connect()
    return psycopg.connect(DEFAULT_DSN)
