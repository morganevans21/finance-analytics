# Documentation

This directory contains comprehensive documentation for the ETF Analytics Project.

## Contents

- [Architecture](./ARCHITECTURE.md) - System architecture and design decisions
- [Installation](./INSTALLATION.md) - Setup and installation guide
- [Usage](./USAGE.md) - How to use the project
- [Data Model](./DATA_MODEL.md) - Database schema and data flow
- [ETF Universe](./ETF_UNIVERSE.md) - Details about the ETF research universe
- [API Reference](./API_REFERENCE.md) - Documentation of public APIs and functions
- [Development](./DEVELOPMENT.md) - Guidelines for contributing to the project
- [Testing](./TESTING.md) - Information about the test suite
- [Financial Methodology](./FINANCIAL_METHODOLOGY.md) - Details on calculations and assumptions

## Overview

The ETF Analytics Project is a personal quantitative finance and data engineering project focused on building a reusable ETF performance analytics platform. It retrieves historical ETF market data, validates and transforms it, stores it in PostgreSQL, calculates investment performance and risk analytics, and provides an interactive analytics interface through Streamlit.

## Key Features

- Automated incremental data ingestion via `update_database.py`
- PostgreSQL storage with duplicate-safe UPSERT
- Streamlit dashboard for analytics and visualization
- Comprehensive ETF universe covering global equities, fixed income, commodities, and more
- Reusable financial analytics functions for returns, volatility, drawdown, risk metrics, and market sensitivity
- Configurable ETF ticker list via environment variable

## Getting Started

See [Installation](./INSTALLATION.md) for setup instructions.

## Project Structure

```
.
├── app/                    # Streamlit application
├── data/                   # Sample data, fixtures, and reference data
├── docs/                   # Documentation (this directory)
├── migrations/             # Database migrations
├── notebooks/              # Jupyter notebooks for analysis
├── scripts/                # Utility scripts
├── src/                    # Source code
│   └── finance_analytics/  # Main Python package
├── tests/                  # Test suite
│   ├── unit/               # Unit tests
│   └── integration/        # Integration tests
├── update_database.py      # Main data ingestion script
├── requirements.txt        # Python dependencies
└── README.md               # Project overview
```