# ETF Analytics Project

This project downloads ETF price data (SPY, QQQ) using yfinance,
stores it in PostgreSQL, and provides an interactive dashboard 
using Streamlit.

## Features
- Automated incremental data ingestion via `update_database.py`
- PostgreSQL storage with duplicate-safe UPSERT
- Streamlit dashboard for analytics and visualisation
- Jupyter notebooks (coming soon)

## Setup
1. Create `.env` file (see `.env.example`)
2. Install dependencies:
    ```bash
    pip install -r requirements.txt
3. Update database:
    ```bash
    python update_database.py
4. Launch dashboard:
    streamlit run streamlit_app.py
