-- Template for a database migration script
-- This shows what a migration file would look like if using a formal migration system

-- Migration: Add dividends column to prices table
-- Description: Add column to track cash dividends per share for dividend yield calculations
-- Author: [Your Name]
-- Date: YYYY-MM-DD

-- ===========================================
--   UPGRADE MIGRATION
-- ===========================================

-- Add new column for dividends
-- Using NULLABLE to allow for gradual rollout and handling of historical data
ALTER TABLE prices
ADD COLUMN dividends DOUBLE PRECISION;

-- Optional: Add comment for documentation
COMMENT ON COLUMN prices.dividends IS 'Cash dividends per share';

-- ===========================================
--   DOWNGRADE MIGRATION
-- ===========================================
-- To rollback this migration, you would:
ALTER TABLE prices
DROP COLUMN dividends;

-- ===========================================
--   NOTES
-- ===========================================
-- 1. This migration assumes the application code has been updated to:
--    - Handle the dividends column in data ingestion
--    - Store dividend data when available
--    - Handle NULL values appropriately (no dividends or missing data)
--
-- 2. For a production rollout, consider:
--    - Backfilling historical dividend data if available
--    - Updating analytics functions to calculate dividend yields
--    - Adding dashboard components to display dividend information
--
-- 3. Testing procedure:
--    - Apply to copy of production database
--    - Verify data ingestion works correctly with new column
--    - Verify analytics functions handle new data appropriately
--    - Verify dashboard displays new information correctly
--    - Verify application still works with existing data
--
-- 4. Performance considerations:
--    - Adding a column to a large table may take time and lock the table
--    - Consider scheduling during maintenance windows for large tables
--    - Monitor performance after adding the column