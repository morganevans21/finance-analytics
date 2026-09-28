# Setting Up Alembic Migrations

This document provides guidance on how to set up Alembic for versioned database migrations in the ETF Analytics Project. This would be beneficial if the project's schema grows more complex or if explicit migration tracking becomes desirable.

## Prerequisites

Before setting up Alembic, ensure you have:
1. Alembic installed: `pip install alembic`
2. A working PostgreSQL database (for testing migrations)
3. The project's dependencies installed: `pip install -r requirements.txt`

## Step-by-Step Setup

### 1. Install Alembic

```bash
pip install alembic
```

### 2. Initialize Alembic in the migrations directory

```bash
cd /home/me/projects/finance-analytics
alembic init migrations
```

This will create:
- `migrations/alembic.ini` - Configuration file
- `migrations/env.py` - Environment configuration
- `migrations/versions/` - Directory for migration scripts

### 3. Configure alembic.ini

Edit `migrations/alembic.ini` to configure the database connection:

```ini
[alembic]
# path to migration scripts
script_location = migrations

# template used to generate migration files
# file_template = %%(rev)s_%%(slug)s

# sys.path path, will be prepended to sys.path if present.
# defaults to the current working directory.
prepend_sys_path = .

# timezone to use when rendering the date within the migration file
# as well as the filename.
# If specified, requires the python-dateutil library that can be
# installed via `pip install python-dateutil`
# timezone =

# max length of characters to apply to the
# "caveat" blocker
# TODO: implement
# max_cached_version_length = 100

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers = qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers = qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5s [%(asctime)s] %(name)s: %(message)s
```

### 4. Configure env.py

Replace the contents of `migrations/env.py` with the following to integrate with the project's configuration system:

```python
"""Alembic environment configuration for ETF Analytics Project."""

from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
import os
import sys
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))

# Load environment variables
load_dotenv()

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import the project's database connection and metadata
# We'll need to create a metadata object that reflects our current schema
from src.finance_analytics.database.connection import get_engine

# Set the database URL in the alembic config
# Use the same connection parameters as the rest of the project
config.set_main_option(
    "sqlalchemy.url",
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

# Define the target metadata for 'autogenerate' support
# Since we don't have a centralized metadata object yet, we'll define it here
# In a more complex project, you would import this from your models
from sqlalchemy import MetaData, Table, Column, Date, String, Numeric, BigInteger
from sqlalchemy.databases import postgres

# Define the metadata for the prices table
target_metadata = MetaData()

prices_table = Table(
    'prices', target_metadata,
    Column('date', Date, nullable=False),
    Column('ticker', String(20), nullable=False),
    Column('open', Numeric),
    Column('high', Numeric),
    Column('low', Numeric),
    Column('close', Numeric),
    Column('adj_open', Numeric),
    Column('adj_high', Numeric),
    Column('adj_low', Numeric),
    Column('adj_close', Numeric),
    Column('volume', BigInteger),
    # Note: Primary key will be added explicitly below
)

# For autogenerate to work correctly with existing tables,
# we need to make sure the metadata matches what's in the database
# This is a simplified version - in practice, you'd reflect the existing schema

def include_object(object, name, type_, reflected, compare_to):
    """Determine whether to include an object in the migration process."""
    # For now, include everything
    return True

def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is still acceptable
    here for the backend. By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to
    the script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Use the project's existing connection function
    connectable = get_engine()

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=include_object
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

### 5. Create the Initial Migration

Generate an initial migration that represents the current schema state:

```bash
alembic revision --autogenerate -m "Initial schema for prices table"
```

This will create a file in `migrations/versions/` like:
`xxxxxxxx_initial_schema_for_prices_table.py`

### 6. Review and Edit the Generated Migration

Check the generated migration file to ensure it correctly represents the schema. You may need to edit it to:
- Ensure the primary key is properly defined
- Add any necessary constraints
- Adjust column definitions if needed

### 7. Apply the Migration

To apply the migration to your database:

```bash
alembic upgrade head
```

### 8. Making Schema Changes

When you need to change the schema in the future:

1. **Modify the schema** in your application code (e.g., add a column to expected_columns in schema.py)
2. **Generate a new migration**:
   ```bash
   alembic revision --autogenerate -m "Description of change"
   ```
3. **Review the generated migration** to ensure it correctly captures your changes
4. **Apply the migration**:
   ```bash
   alembic upgrade head
   ```

## Integration with Existing Schema Management

During a transition period, you might want to use both systems temporarily:

1. **Keep** the `initialize_database_schema()` function running
2. **Use** Alembic for explicit version control and team coordination
3. **Eventually phase out** the automatic schema validation in favor of explicit migrations

Alternatively, you could modify `initialize_database_schema()` to check if Alembic is being used and defer to it, but this adds complexity.

## Managing Migrations

### Common Alembic Commands

```bash
# Generate a new migration based on model changes
alembic revision --autogenerate -m "Add dividends column"

# Generate a blank migration for manual editing
alembic revision -m "Manual schema change"

# Apply pending migrations
alembic upgrade head

# Apply a specific number of migrations
alembic upgrade +2

# Roll back the last migration
alembic downgrade -1

# Roll back to a specific revision
alembic downgrade base
alembic downgrade 1a2b3c4d5e6f

# Show current revision
alembic current

# Show migration history
alembic history

# Show the SQL for a migration without executing it
alembic upgrade head --sql

# Create a migration without executing it
alembic revision --autogenerate -m "test" --head-only
```

## Best Practices

### Migration Naming
Use descriptive messages that clearly indicate what the migration does:
- ✅ "Add dividends column to prices table"
- ✅ "Create indexes on frequently queried columns"
- ❌ "Fix schema"
- ❌ "Update database"

### Testing Migrations
Always test migrations on a copy of your production data before applying to production:
1. Copy production database to test database
2. Apply migrations to test database
3. Verify application works correctly with migrated schema
4. Check performance and data integrity

### Backward Compatibility
When making schema changes, consider backward compatibility:
- Add new columns as nullable initially
- Provide default values where appropriate
- Update application code to handle both old and new schemas
- Consider complex migrations in multiple steps if needed

### Documentation
Keep migration messages clear and concise, and consider maintaining a CHANGELOG.md that summarizes schema changes over time.

## When to Use This Approach

Consider migrating to Alembic when:
- The schema involves multiple tables with relationships
- You need explicit version tracking for audit or compliance reasons
- Team development benefits from seeing explicit migration plans
- You want the ability to roll back to specific schema versions
- Data migrations alongside schema changes become common
- The project adopts more formal DevOps practices

## Transition Example: Adding a Dividends Column

Here's how adding a dividends column would work with Alembic:

1. **Update application code** to expect and handle the dividends column
2. **Generate migration**:
   ```bash
   alembic revision --autogenerate -m "Add dividends column to prices table"
   ```
3. **Review generated migration** (might look like):
   ```python
   """Add dividends column to prices table

   Revision ID: 1a2b3c4d5e6f
   Revises: xxxxxxxxxxxx
   Create Date: 2026-09-25 10:00:00.000000

   """
   from alembic import op
   import sqlalchemy as sa

   # revision identifiers, used by alembic.
   revision = '1a2b3c4d5e6f'
   down_revision = 'xxxxxxxxxxx'
   branch_labels = None
   depends_on = None


   def upgrade():
       # ### commands auto generated by Alembic - please adjust! ###
       op.add_column('prices', sa.Column('dividends', sa.Numeric(), nullable=True))
       # ### end Alembic commands ###


   def downgrade():
       # ### commands auto generated by Alembic - please adjust! ###
       op.drop_column('prices', 'dividends')
       # ### end Alembic commands ###
   ```
4. **Apply migration**:
   ```bash
   alembic upgrade head
   ```
5. **Verify** that the application works correctly with the new column

## Conclusion

While the current schema management approach serves the project well, setting up Alembic provides a path to more formal, version-controlled schema management as the project evolves. This setup guide provides the foundation for making that transition when the time comes.

For now, the project can continue using the existing schema management approach, with this directory serving as preparation for future evolution.