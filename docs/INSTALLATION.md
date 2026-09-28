# Installation Guide

## Prerequisites

Before installing the ETF Analytics Project, ensure you have:

1. **Python 3.14+** - The project targets Python 3.14 for modern features
2. **PostgreSQL 12+** - The target database for storing market data
3. **Git** - For version control (optional but recommended)
4. **pip** - Python package installer

## Step-by-Step Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/finance-analytics.git
cd finance-analytics
```

### 2. Set Up Python Environment

We recommend using a virtual environment:

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root based on the provided example:

```bash
cp .env.example .env
```

Edit the `.env` file to match your PostgreSQL configuration:

```
DB_USER=your_postgres_username
DB_PASSWORD=your_postgres_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=finance_db

# Optional: Customize ETF selection and data range
ETF_TICKERS=SPY,QQQ,VTI,GLD,BND
START_DATE=2015-01-01
OVERLAP_DAYS=7
YFINANCE_PROGRESS=True
```

> **Important**: Never commit your `.env` file if it contains real credentials. The `.env.example` file is safe to commit as it contains only placeholder values.

### 5. Initialize the Database

The database schema will be automatically created when you first run the update script. However, you can manually initialize it:

```bash
python -c "
from src.finance_analytics.database.connection import get_engine
from src.finance_analytics.database.schema import initialize_database_schema
engine = get_engine()
initialize_database_schema()
print('Database schema initialized.')
"
```

### 6. Run Initial Data Download

To download the full historical data for the default ETFs (SPY and QQQ):

```bash
python update_database.py
```

This will:
1. Create the database schema if it doesn't exist
2. Download full history for all specified ETFs from START_DATE
3. Store both raw and adjusted prices in the PostgreSQL database
4. Show progress and summary statistics

### 7. Launch the Streamlit Dashboard

```bash
streamlit run app/streamlit_app.py
```

The dashboard will open in your default web browser at http://localhost:8501

## Verification

After installation, verify that everything is working:

1. **Database Connection**: Check that the update script runs without connection errors
2. **Data Ingestion**: Verify that data is stored in the `prices` table
3. **Dashboard Launch**: Confirm the Streamlit app loads and displays data
4. **Basic Functionality**: Try selecting different date ranges and ETFs

## Troubleshooting

### Common Issues

#### 1. Database Connection Errors
- Verify PostgreSQL is running and accessible
- Check `.env` file for correct credentials
- Ensure the database specified in `DB_NAME` exists (or that your user has creation privileges)

#### 2. yfinance Download Issues
- Some tickers may be invalid or delisted
- Network connectivity issues blocking Yahoo Finance access
- Temporary Yahoo Finance API limitations

#### 3. Missing Dependencies
- Ensure all packages in `requirements.txt` are installed
- Some packages may have system-level dependencies (e.g., psycopg2-binary needs PostgreSQL headers)

#### 4. Streamlit Port Conflicts
- If port 8501 is in use, specify a different port: `streamlit run app/streamlit_app.py --server.port=8502`

## Development Installation

For developers planning to contribute to the project:

```bash
# Fork and clone your fork
git clone https://github.com/yourusername/finance-analytics.git
cd finance-analytics

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install in development mode
pip install -e .

# Install development dependencies
pip install pytest ruff pytest-cov

# Pre-commit hooks (optional)
pip install pre-commit
pre-commit install
```

## Docker Installation (Alternative)

A Docker-based installation is also available:

```bash
# Build the image
docker build -t finance-analytics .

# Run the container (requires PostgreSQL running separately)
docker run -p 8501:8501 --env-file .env finance-analytics

# Or use docker-compose for full stack
docker-compose up
```

See `docker-compose.yml` for the full-stack development environment.

## Updating the Project

To pull updates and reinstall dependencies:

```bash
git pull origin main  # Or your preferred branch
pip install -r requirements.txt  # Update dependencies if needed
```

Database migrations, if needed, will be handled automatically by the schema initialization code.