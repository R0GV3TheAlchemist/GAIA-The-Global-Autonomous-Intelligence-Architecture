"""Alembic environment configuration for GAIA-OS.

Reads DATABASE_URL from the environment so that credentials never
live in alembic.ini or source control.
"""
from __future__ import annotations

import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# ---------------------------------------------------------------------------
# Alembic Config object — gives access to alembic.ini values.
# ---------------------------------------------------------------------------
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ---------------------------------------------------------------------------
# Import ALL SQLAlchemy models so that autogenerate can detect them.
# Add new model modules here as they are created.
# ---------------------------------------------------------------------------
from gaia.db.base import Base  # noqa: E402  (must come after config setup)

# Numerology models
from gaia.db.models.numerology import NumerologyChart, NumerologyProfile  # noqa: F401

# Add other model imports below as the project grows:
# from gaia.db.models.user import User
# from gaia.db.models.ritual import RitualSession

target_metadata = Base.metadata

# ---------------------------------------------------------------------------
# Override sqlalchemy.url with the DATABASE_URL environment variable.
# Fall back to the placeholder in alembic.ini only for tooling introspection.
# ---------------------------------------------------------------------------
database_url = os.environ.get("DATABASE_URL")
if database_url:
    config.set_main_option("sqlalchemy.url", database_url)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    Configures the context with just a URL and not an Engine.  Calls to
    context.execute() emit the given string to the script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    Creates an Engine and associates a connection with the context.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
