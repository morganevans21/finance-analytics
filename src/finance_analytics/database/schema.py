"""
Database schema management for the finance analytics project.
"""

from sqlalchemy import text
from .connection import get_engine


def initialize_database_schema():
    """
    Ensure the prices table has the required columns.

    The table stores both raw and adjusted OHLC prices.
    """
    engine = get_engine()

    with engine.begin() as conn:
        # -------------------------------------------------
        # Check whether prices table exists.
        # -------------------------------------------------

        result = conn.execute(
            text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = 'prices'
                );
            """)
        )

        table_exists = result.scalar()

        # -------------------------------------------------
        # Create table if it does not exist.
        # -------------------------------------------------

        if not table_exists:

            print("Creating prices table...")

            conn.execute(
                text("""
                    CREATE TABLE prices (
                        date DATE NOT NULL,
                        ticker VARCHAR(20) NOT NULL,

                        -- Raw market prices
                        open DOUBLE PRECISION,
                        high DOUBLE PRECISION,
                        low DOUBLE PRECISION,
                        close DOUBLE PRECISION,

                        -- Corporate-action-adjusted prices
                        adj_open DOUBLE PRECISION,
                        adj_high DOUBLE PRECISION,
                        adj_low DOUBLE PRECISION,
                        adj_close DOUBLE PRECISION,

                        -- Unadjusted trading volume
                        volume BIGINT,

                        PRIMARY KEY (date, ticker)
                    );
                """)
            )

            print("Created prices table.")

            return

        # -------------------------------------------------
        # Existing table.
        # -------------------------------------------------

        print("Prices table already exists.")

        result = conn.execute(
            text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_schema = 'public'
                AND table_name = 'prices';
            """)
        )

        existing_columns = {
            row[0]
            for row in result.fetchall()
        }

        # -------------------------------------------------
        # Required columns.
        # -------------------------------------------------

        expected_columns = {
            "date": "DATE",
            "ticker": "VARCHAR(20)",

            "open": "DOUBLE PRECISION",
            "high": "DOUBLE PRECISION",
            "low": "DOUBLE PRECISION",
            "close": "DOUBLE PRECISION",

            "adj_open": "DOUBLE PRECISION",
            "adj_high": "DOUBLE PRECISION",
            "adj_low": "DOUBLE PRECISION",
            "adj_close": "DOUBLE PRECISION",

            "volume": "BIGINT",
        }

        # -------------------------------------------------
        # Add missing columns.
        # -------------------------------------------------

        for column_name, column_type in expected_columns.items():

            if column_name not in existing_columns:

                print(
                    f"Adding missing column "
                    f"{column_name} "
                    f"({column_type})..."
                )

                conn.execute(
                    text(
                        f"""
                        ALTER TABLE prices
                        ADD COLUMN {column_name}
                        {column_type};
                        """
                    )
                )

        # -------------------------------------------------
        # Ensure primary key exists.
        # -------------------------------------------------

        result = conn.execute(
            text("""
                SELECT constraint_name
                FROM information_schema.table_constraints
                WHERE table_schema = 'public'
                AND table_name = 'prices'
                AND constraint_type = 'PRIMARY KEY';
            """)
        )

        pk_constraints = result.fetchall()

        if not pk_constraints:

            print(
                "Adding primary key on "
                "(date, ticker)..."
            )

            conn.execute(
                text("""
                    ALTER TABLE prices
                    ADD PRIMARY KEY (date,KEY (date, ticker);
                """)
            )

        print("Database schema verified.")