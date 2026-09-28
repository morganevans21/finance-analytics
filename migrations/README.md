# Migrations Directory

This directory contains database migration scripts and related files for the ETF Analytics Project.

## Current Schema Management Approach

The ETF Analytics Project currently manages database schema evolution through the `initialize_database_schema()` function in `src/finance_analytics/database/schema.py` rather than using a traditional migration framework like Alembic.

This approach was chosen for its simplicity and transparency, particularly suitable for a project with a relatively simple schema (single table) and emphasis on readability and learning.

For details on the current approach, see [CURRENT_APPROACH.md](CURRENT_APPROACH.md).

## Directory Contents

- `001_initial_schema.sql` - SQL representation of the initial database schema
- `CURRENT_APPROACH.md` - Detailed explanation of the current schema management approach
- `ALEMBIC_SETUP.md` - Template for how to set up Alembic migrations if desired in the future
- `TEMPLATE_MIGRATION.sql` - Template showing what a migration file would look like

## Future Migration Options

While the current approach works well for the project's current scale, as the project grows more complex, transitioning to a formal migration system may be beneficial. The files in this directory provide guidance for such a transition.

See `ALEMBIC_SETUP.md` for instructions on setting up Alembic, which would provide:
- Versioned migrations
- Ability to roll forward and backward
- Explicit migration tracking
- Better support for complex schema changes
- Standard tooling familiar to many developers