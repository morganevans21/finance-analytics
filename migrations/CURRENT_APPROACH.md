# Current Schema Management Approach

## Overview

The ETF Analytics Project manages database schema evolution through the `initialize_database_schema()` function in `src/finance_analytics/database/schema.py`. This approach was selected to prioritize simplicity, transparency, and ease of understanding - important considerations for a learning and portfolio project.

## How It Works

The `initialize_database_schema()` function follows this process:

### 1. Table Existence Check
```sql
SELECT EXISTS (
    SELECT FROM information_schema.tables
    WHERE table_schema = 'public'
    AND table_name = 'prices'
);
```

### 2. Table Creation (if not exists)
If the `prices` table doesn't exist, it is created with the full schema:

```sql
CREATE TABLE prices (
    date DATE NOT NULL,
    ticker VARCHAR(20) NOT NULL,
    open DOUBLE PRECISION,
    high DOUBLE PRECISION,
    low DOUBLE PRECISION,
    close DOUBLE PRECISION,
    adj_open DOUBLE PRECISION,
    adj_high DOUBLE PRECISION,
    adj_low DOUBLE PRECISION,
    adj_close DOUBLE PRECISION,
    volume BIGINT,
    PRIMARY KEY (date, ticker)
);
```

### 3. Schema Validation and Updates (if exists)
If the table already exists, the function:
- Retrieves the current schema from `information_schema.columns`
- Compares it against the expected schema defined in the code
- Adds any missing columns using `ALTER TABLE ... ADD COLUMN`
- Ensures the primary key constraint exists

### 4. Transaction Management
All operations are performed within a transaction to ensure consistency.

## Advantages of This Approach

### Simplicity
- No separate migration files to manage or version
- Schema logic is co-located with the code that uses it
- Reduced cognitive overhead for developers

### Automatic Updates
- Schema is kept current without explicit migration commands
- Works seamlessly in development, testing, and production environments
- No risk of forgetting to run migrations

### Safety
- Non-destructive updates preserve existing data
- Only adds columns, never removes or modifies existing ones
- Minimal risk of data loss or corruption

### Transparency
- Schema definition is visible in one easy-to-understand location
- No need to inspect migration files to understand current schema
- Clear relationship between code expectations and database structure

### Development Workflow Benefits
- Developers don't need to remember to run migration commands
- Schema updates happen automatically during testing
- Reduces friction in the development process

## Limitations and Considerations

### No Version History
- No explicit record of when schema changes were made
- Difficult to audit historical schema changes
- No ability to roll back to a specific schema version

### Limited Flexibility
- Primarily designed for additive changes (adding columns)
- Less suitable for complex transformations (changing column types, renaming columns, etc.)
- No support for data migrations alongside schema changes

### Scaling Concerns
- As schema grows more complex, the validation logic becomes more complex
- Large tables with many columns might experience performance impacts during schema checks
- Team development might benefit from more explicit change management

## When This Approach Works Best

This approach is particularly suitable when:
- The schema is relatively simple (few tables, straightforward relationships)
- Additive changes are the primary type of schema evolution
- The project values simplicity and transparency over formal versioning
- Development velocity is prioritized over strict schema change tracking
- The application controls all access to the database (no external applications modifying schema)

## Example Workflow

### Adding a New Column (e.g., dividends)

1. **Update schema.py**:
   Add to `expected_columns` dictionary:
   ```python
   "dividends": "DOUBLE PRECISION",
   ```

2. **Update ingestion pipeline**:
   Modify data download and processing to include dividend data

3. **Update analytics** (if applicable):
   Add functions to utilize dividend data

4. **Update dashboard** (if applicable):
   Add visualization or metrics for dividend analysis

5. **Test**:
   - Run against fresh database: verify table creation includes new column
   - Run against existing database: verify column is added correctly
   - Verify data flows from ingestion to storage to analysis
   - Verify existing functionality remains intact

6. **Deploy**:
   No explicit migration step needed - schema updates automatically on next application run

## Comparison with Formal Migration Systems

| Feature | Current Approach | Alembic/Similar |
|---------|------------------|-----------------|
| Setup Complexity | Minimal (no extra config) | Requires initialization and configuration |
| Execution | Automatic on app startup | Explicit commands (`upgrade`, `downgrade`) |
| Schema History | Implicit (in code) | Explicit (versioned migration files) |
| Rollback Capability | Limited (forward-only via code) | Full (can downgrade to specific versions) |
| Data Migration Support | Limited (application-level) | Built-in support for data migrations |
| Team Development | Simple (no conflict resolution) | Requires merge conflict resolution for migration files |
| Tool Familiarity | Project-specific | Industry-standard tooling |
| Complexity Handling | Best for simple additive changes | Handles complex schema changes well |
| Visibility | Schema logic in code | Migration files show change history |

## Transitioning to a Formal Migration System

If the project evolves to benefit from a formal migration system, the transition would involve:

1. **Selecting a migration tool** (e.g., Alembic for SQLAlchemy-based projects)
2. **Creating an initial migration** representing the current schema state
3. **Updating the application** to use migration commands instead of (or in addition to) schema validation
4. **Maintaining both approaches temporarily** during transition
5. **Eventually removing** the schema validation approach in favor of explicit migrations

See `ALEMBIC_SETUP.md` for guidance on setting up Alembic if this transition becomes desirable.