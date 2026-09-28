# Scripts Directory

This directory contains utility scripts for the ETF Analytics Project to facilitate development, testing, deployment, and maintenance tasks.

## Available Scripts

### Setup and Initialization
- `setup.py` - Initial setup script for new developers
  - Checks prerequisites
  - Installs dependencies
  - Sets up environment
  - Initializes database
  - Optionally loads initial data

### Database Management
- `reset_db.py` - Reset database to clean state (WARNING: deletes all data)
- `db_status.py` - Display current database status and statistics
- `validate_data.py` - Validate data quality and integrity
- `export_data.py` - Export data to various formats (CSV, JSON, Excel, etc.)

### Data Operations
- `update_data.py` - Enhanced wrapper around update_database.py with additional options
- `install_dev.py` - Install development dependencies

### Application Execution
- `run_app.py` - Launch the Streamlit dashboard with proper environment setup

### Testing
- `run_tests.py` - Convenient test runner with various options

## Usage Guidelines

### For New Developers
1. Run `python scripts/setup.py` to get started
2. Edit `.env` to configure your database connection
3. Run `python scripts/update_data.py` to load initial data
4. Run `python scripts/run_app.py` to launch the dashboard

### For Routine Operations
- Update data: `python scripts/update_data.py`
- Check database status: `python scripts/db_status.py`
- Validate data quality: `python scripts/validate_data.py`
- Export data for analysis: `python scripts/export_data.py`

### For Development and Testing
- Run tests: `python scripts/run_tests.py`
- Run tests with coverage: `python scripts/run_tests.py --coverage`
- Run unit tests only: `python scripts/run_tests.py --unit`
- Install dev dependencies: `python scripts/install_dev.py`

### For Database Maintenance
- Reset database (development only): `python scripts/reset_db.py`
- Fix duplicate records: `python scripts/validate_data.py --fix-duplicates`

## Script Dependencies

Most scripts depend on the project being properly set up:
1. `.env` file with database configuration
2. Python dependencies installed (`pip install -r requirements.txt`)
3. PostgreSQL server running and accessible

## Safety Notes

### Destructive Operations
- `reset_db.py` will DELETE ALL DATA in the database
- Use with extreme caution in production environments
- Always backup important data before running destructive operations

### Data Modification
- `validate_data.py --fix-duplicates` will modify the database
- This operation removes duplicate records (keeping first occurrence)
- Consider backing up data before running

## Best Practices

### Development Workflow
1. Keep your `.env` file secure and never commit it to version control
2. Use feature branches for development work
3. Run tests frequently during development
4. Validate data quality after major operations
5. Keep dependencies up to date

### Production Deployment
- Consider using proper migration tools (see migrations/ALEMBIC_SETUP.md)
- Use environment-specific configuration files
- Implement proper backup and recovery procedures
- Monitor database performance and data quality regularly

## Extending the Scripts Directory

To add a new utility script:
1. Create a new Python file in this directory
2. Follow the existing patterns for:
   - Argument parsing (using argparse)
   - Error handling and logging
   - Environment variable loading
   - Database connection handling
   - Status messaging with colored output
3. Add appropriate documentation in the script's docstring
4. Update this README to document the new script