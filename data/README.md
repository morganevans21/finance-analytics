# Data Directory

This directory contains data-related resources for the finance analytics project.

## Purpose

The data directory is intended for:
- Sample data files used in testing and development
- Reference data exports (e.g., ETF universe definitions)
- Data documentation and dictionaries
- Fixtures for unit and integration tests

## Contents

- `sample/`: Sample data files for development and testing
- `reference/`: Reference data such as ETF universe definitions
- `fixtures/`: Test fixtures for unit and integration tests

Note: The primary market data is sourced from Yahoo Finance via yfinance and stored in PostgreSQL, so this directory does not contain the main market dataset.