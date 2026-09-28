# Testing Guidelines

This document provides information about the test suite for the ETF Analytics Project, including how to run tests, write new tests, and understand the testing philosophy.

## Testing Philosophy

Tests should protect meaningful behavior, not merely increase coverage. For a quantitative finance project like this one, the testing philosophy emphasizes:

### 1. Mathematical Correctness
Financial calculations must be mathematically correct. Tests verify:
- Known values where expected results can be calculated manually
- Mathematical properties and identities
- Consistency with established financial formulas

### 2. Edge Cases
Financial data can contain unusual values that must be handled properly:
- Empty datasets
- Single data points
- All NaN values
- Extreme values (very large/small numbers)
- Missing data patterns
- Boundary conditions

### 3. Numerical Stability
Financial calculations often involve floating-point arithmetic that can accumulate errors:
- Test precision and accuracy
- Verify appropriate handling of floating-point limitations
- Ensure algorithms are numerically stable

### 4. Frequency and Annualization
Correct handling of time periods is crucial in finance:
- Verify periodic-to-annual conversions are accurate
- Test different compounding frequencies
- Confirm rolling window calculations align with intended periods

### 5. Missing Data Handling
Real-world financial data often contains missing values:
- Test behavior with NaN values in various positions
- Verify appropriate strategies (drop, fill, propagate)
- Ensure missing data doesn't corrupt calculations

### 6. Integration Points
Test that components work together correctly:
- Data flows properly between modules
- Database operations work as expected
- End-to-end functionality produces expected results

## Test Organization

The test suite is organized into two main categories:

```
tests/
├── unit/                 # Unit tests for individual components
│   ├── test_analytics.py     # Tests for financial calculation functions
│   ├── test_database.py      # Tests for database operations and schema
│   ├── test_universe.py      # Tests for ETF universe definitions
│   ├── test_ingestion.py     # Tests for data download and preprocessing
│   └── test_validation.py    # Tests for data validation and cleaning
└── integration/          # Integration tests
    ├── test_database_integration.py  # Database + ingestion workflow tests
    ├── test_api_integration.py       # Analytics + database integration tests
    └── test_end_to_end.py            # Full pipeline tests
```

### Unit Tests

Unit tests focus on individual functions or classes in isolation. They should:
- Test one thing at a time
- Have minimal dependencies (mock external services when needed)
- Run quickly (typically milliseconds)
- Be easy to understand and diagnose when failing

### Integration Tests

Integration tests verify that multiple components work together:
- Test real database connections (may use test database)
- Test actual data flow from download to storage to analysis
- Test end-to-end scenarios that users would encounter
- May take longer to run (seconds to minutes)
- Provide confidence that the system works as a whole

## Running Tests

### Prerequisites
Before running tests, ensure you have:
1. Python 3.14+ installed
2. All dependencies installed (`pip install -r requirements.txt`)
3. For some integration tests: access to a PostgreSQL database

### Running All Tests
```bash
# Using pytest (recommended)
python -m pytest

# Using unittest discovery (alternative)
python -m unittest discover tests
```

### Running Specific Test Suites
```bash
# Run only unit tests
python -m pytest tests/unit/

# Run only integration tests
python -m pytest tests/integration/

# Run tests for a specific module
python -m pytest tests/unit/test_analytics.py

# Run tests with verbose output
python -m pytest -v

# Run tests with coverage report
python -m pytest --cov=src --cov-report=html

# Run tests matching a keyword expression
python -m pytest -k "returns or volatility"

# Run tests that don't match a keyword expression
python -m pytest -k "not integration"
```

### Running Specific Tests
```bash
# Run a specific test class
python -m pytest tests/unit/test_analytics.py::TestReturns

# Run a specific test method
python -m pytest tests/unit/test_analytics.py::TestReturns::test_simple_returns

# Run multiple specific tests
python -m pytest tests/unit/test_analytics.py::TestReturns::test_simple_returns tests/unit/test_analytics.py::TestReturns::test_log_returns
```

## Writing Tests

### Unit Test Guidelines

#### Test Structure
Use the `unittest` framework with these best practices:

```python
import unittest
import numpy as np
import pandas as pd
from finance_analytics.analytics import some_function

class TestSomeFunction(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create reusable test data
        self.returns_data = pd.Series([0.01, 0.02, -0.01, 0.015],
                                     index=pd.date_range('2023-01-01', periods=4))
        self.price_data = pd.Series([100, 101, 99, 100.5],
                                   index=pd.date_range('2023-01-01', periods=4))
    
    def tearDown(self):
        """Clean up after each test method (if needed)."""
        # Clean up any resources created during testing
        pass
    
    def test_normal_case(self):
        """Test typical usage with normal financial data."""
        result = some_function(self.returns_data)
        expected = pd.Series([np.nan, 0.01, 0.01, -0.01], 
                            index=self.returns_data.index)
        # Use appropriate assertion for floating point comparison
        np.testing.assert_array_almost_equal(
            result.dropna().values, 
            expected.dropna().values,
            decimal=6
        )
    
    def test_empty_input(self):
        """Test behavior with empty input."""
        empty_series = pd.Series(dtype=float)
        result = some_function(empty_series)
        self.assertTrue(result.empty)
    
    def test_single_element(self):
        """Test behavior with single element (should return NaN for most financial calcs)."""
        single = pd.Series([0.01])
        result = some_function(single)
        self.assertTrue(np.isnan(result.iloc[0]))
    
    def test_all_nan(self):
        """Test behavior when all values are NaN."""
        nan_series = pd.Series([np.nan, np.nan, np.nan])
        result = some_function(nan_series)
        # Most financial functions should return all NaN
        self.assertTrue(result.isna().all())
    
    def test_negative_values(self):
        """Test behavior with negative returns/prices where appropriate."""
        negative_returns = pd.Series([-0.02, -0.01, 0.005])
        result = some_function(negative_returns)
        # Add specific assertions based on function behavior
    
    def test_large_values(self):
        """Test behavior with very large financial values."""
        large_returns = pd.Series([0.5, 1.0, 2.0])  # 50%, 100%, 200% returns
        result = some_function(large_returns)
        # Verify function handles large values appropriately
    
    def test_precision(self):
        """Test numerical precision of calculations."""
        # Use known values where exact result can be calculated
        test_data = pd.Series([0.1, 0.1, 0.1])  # Three 10% periods
        result = some_function(test_data)
        # For example, three 10% periods should give specific cumulative return
        expected_value = (1.1 ** 3) - 1  # 0.331
        self.assertAlmostEqual(result.iloc[-1], expected_value, places=10)
```

#### Assertion Guidelines
Use appropriate assertions for different types of comparisons:

- **Exact equality** (integers, booleans, strings): `assertEqual(a, b)`
- **Floating point equality**: `assertAlmostEqual(a, b, places=7)` or `np.testing.assert_array_almost_equal`
- **Inequality**: `assertNotEqual(a, b)`
- **Truthiness**: `assertTrue(condition)`, `assertFalse(condition)`
- **None checking**: `assertIsNone(value)`, `assertIsNotNone(value)`
- **Type checking**: `assertIsInstance(obj, cls)`
- **Membership**: `assertIn(item, container)`, `assertNotIn(item, container)`
- **Empty collections**: `assertTrue(len(collection) == 0)`, `assertFalse(collection)`
- **Exceptions**: `assertRaises(ExceptionType, callable, *args)`

#### Financial Test Examples

##### Testing Return Calculations
```python
def test_simple_returns_known_values(self):
    """Test simple returns with known values."""
    # Price series: 100 -> 110 -> 121 -> 110
    # Returns should be:    -> 0.1   -> 0.1   -> -0.0909...
    prices = pd.Series([100, 110, 121, 110],
                      index=pd.date_range('2023-01-01', periods=4))
    returns = simple_returns(prices)
    
    # First value should be NaN (no previous price)
    self.assertTrue(np.isnan(returns.iloc[0]))
    
    # Check remaining values with appropriate precision
    expected_returns = [0.1, 0.1, -0.0909090909]
    np.testing.assert_array_almost_equal(
        returns.dropna().values,
        expected_returns,
        decimal=6
    )
```

##### Testing Volatility Calculations
```python
def test_rolling_volatility_known_variance(self):
    """Test rolling volatility with known variance."""
    # Create returns with known variance
    # For example, returns of [0.02, -0.02, 0.02, -0.02] have variance 0.0004
    returns = pd.Series([0.02, -0.02, 0.02, -0.02],
                       index=pd.date_range('2023-01-01', periods=4))
    
    # Calculate rolling volatility with window=2
    vol = rolling_volatility(returns, window=2)
    
    # For window=2, each volatility value is std dev of two points
    # Variance of [0.02, -0.02] is 0.0004, std dev is 0.02
    # Annualized vol = 0.02 * sqrt(252) ≈ 0.3175
    expected_vol = 0.02 * np.sqrt(252)
    
    # Check that non-NaN values are close to expected
    vol_clean = vol.dropna()
    np.testing.assert_array_almost_equal(
        vol_clean.values,
        [expected_vol, expected_vol, expected_vol],
        decimal=4
    )
```

##### Testing Drawdown Calculations
```python
def test_max_drawdown_simple_case(self):
    """Test max drawdown with simple peak-trough-recovery pattern."""
    # Cumulative returns: 0.0 -> 0.1 -> 0.2 -> 0.1 -> 0.0 -> -0.1
    # Running max:       0.0 -> 0.1 -> 0.2 -> 0.2 -> 0.2 -> 0.2
    # Drawdown:          NaN -> 0.0 -> 0.0 -> -0.5 -> -1.0 -> -1.5
    # Max drawdown: -1.5 (or -60% if expressed as percentage)
    cum_returns = pd.Series([0.0, 0.1, 0.2, 0.1, 0.0, -0.1],
                           index=pd.date_range('2023-01-01', periods=6))
    
    max_dd = max_drawdown(cum_returns)
    
    # Calculate expected max drawdown manually
    # Peak = 0.2, Trough = -0.1
    # Drawdown = (trough - peak) / (1 + peak) = (-0.1 - 0.2) / 1.2 = -0.3 / 1.2 = -0.25
    expected_dd = -0.25
    
    self.assertAlmostEqual(max_dd, expected_dd, places=6)
```

#### Testing Edge Cases
Always include tests for:
- Empty inputs
- Single element inputs
- All NaN inputs
- All zero inputs
- Extremely large values
- Extremely small values (close to zero)
- Mixed positive/negative values
- Data with gaps or irregular spacing
- Boundary values (e.g., window size equal to data length)

### Integration Test Guidelines

Integration tests verify that components work together correctly. They often require:
- Actual database connections
- Network access (for tests that download real data)
- More setup and teardown
- Longer execution times

#### Database Integration Tests
When testing database operations:

```python
import unittest
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from src.finance_analytics.database.connection import get_engine
from src.finance_analytics.database.schema import initialize_database_schema
from src.finance_analytics.database.operations import upsert_prices, get_latest_dates

class TestDatabaseIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test database connection once for all tests."""
        load_dotenv()  # Load environment variables
        # Use test database if specified, otherwise use main DB
        test_db_name = os.getenv('TEST_DB_NAME', os.getenv('DB_NAME'))
        # Modify connection to use test database
        # ... (implementation depends on your setup)
        cls.engine = get_engine()
        initialize_database_schema(cls.engine)
    
    def setUp(self):
        """Clean up before each test."""
        # Clear test data from previous runs
        with self.engine.begin() as conn:
            conn.execute(text("DELETE FROM prices"))
    
    def test_upsert_and_retrieve(self):
        """Test inserting data and retrieving it correctly."""
        # Prepare test data
        test_records = [
            {
                'date': '2023-01-03',
                'ticker': 'TEST',
                'open': 100.0,
                'high': 105.0,
                'low': 99.0,
                'close': 103.0,
                'adj_open': 100.0,
                'adj_high': 105.0,
                'adj_low': 99.0,
                'adj_close': 103.0,
                'volume': 1000000
            },
            {
                'date': '2023-01-04',
                'ticker': 'TEST',
                'open': 103.0,
                'high': 107.0,
                'low': 102.0,
                'close': 105.0,
                'adj_open': 103.0,
                'adj_high': 107.0,
                'adj_low': 102.0,
                'adj_close': 105.0,
                'volume': 1200000
            }
        ]
        
        # Upsert the data
        upsert_prices(test_records)
        
        # Retrieve and verify
        with self.engine.connect() as conn:
            result = conn.execute(
                text("SELECT * FROM prices WHERE ticker = 'TEST' ORDER BY date")
            )
            rows = result.fetchall()
            
            self.assertEqual(len(rows), 2)
            # Verify first row
            self.assertEqual(rows[0].ticker, 'TEST')
            self.assertEqual(str(rows[0].date), '2023-01-03')
            self.assertEqual(rows[0].close, 103.0)
            self.assertEqual(rows[0].volume, 1000000)
            # Verify second row
            self.assertEqual(rows[1].ticker, 'TEST')
            self.assertEqual(str(rows[1].date), '2023-01-04')
            self.assertEqual(rows[1].close, 105.0)
            self.assertEqual(rows[1].volume, 1200000)
```

#### End-to-End Integration Tests
End-to-end tests verify the complete workflow:

```python
@unittest.skipIf(os.getenv('SKIP_E2E_TESTS'), "Skipping end-to-end tests")
class TestEndToEnd(unittest.TestCase):
    def test_update_pipeline_with_sample_data(self):
        """Test the complete update pipeline with controlled data."""
        # This test might:
        # 1. Mock yfinance download to return known data
        # 2. Run the update process
        # 3. Verify data was stored correctly
        # 4. Run analytics on the stored data
        # 5. Verify results match expectations
        pass
```

## Test Data and Fixtures

### Using Existing Test Data
The project includes test data in the `tests/` directory and `data/fixtures/`:

```python
import pandas as pd
import os

def load_test_returns_data():
    """Load sample returns data for testing."""
    fixture_path = os.path.join(
        os.path.dirname(__file__), 
        '..', 'data', 'fixtures', 'sample_returns_data.csv'
    )
    return pd.read_csv(fixture_path, parse_dates=['date'])

def load_sample_prices():
    """Load sample price data for testing."""
    fixture_path = os.path.join(
        os.path.dirname(__file__), 
        '..', 'data', 'fixtures', 'sample_prices.csv'
    )
    return pd.read_csv(fixture_path, parse_dates=['date'])
```

### Creating Test Fixtures
When creating test data:
1. **Keep it simple** - use minimal data necessary to test the concept
2. **Make it deterministic** - avoid random data unless testing statistical properties
3. **Document assumptions** - clearly state what the test data represents
4. **Consider edge cases** - include boundary values and special cases
5. **Make it reusable** - structure data so it can be used in multiple tests

### Mocking External Services
For tests that would normally access external services (like Yahoo Finance), use mocking:

```python
import unittest
from unittest.mock import patch, MagicMock
import pandas as pd

class TestDownloadWithMock(unittest.TestCase):
    @patch('src.finance_analytics.ingestion.download.yf.download')
    def test_download_success(self, mock_yf_download):
        """Test successful download with mocked yfinance."""
        # Set up mock return value
        mock_data = pd.DataFrame({
            'Open': [100, 101],
            'High': [102, 103],
            'Low': [99, 100],
            'Close': [101, 102],
            'Volume': [1000000, 1100000]
        }, index=pd.date_range('2023-01-01', periods=2))
        mock_yf_download.return_value = mock_data
        
        # Call the function under test
        result = download_yfinance_data(['TEST'], '2023-01-01', '2023-01-02')
        
        # Verify the mock was called correctly
        mock_yf_download.assert_called_once()
        # Verify result processing
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)
```

## Continuous Integration

The project may use continuous integration services that automatically run tests on:
- Pull requests to the main branch
- Pushes to the main branch
- Scheduled builds (e.g., nightly)

### CI Configuration Example
If using GitHub Actions, the configuration might look like:

```yaml
name: Test Suite

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: finance_db_test
        ports: [5432:5432]
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    env:
      DB_USER: postgres
      DB_PASSWORD: postgres
      DB_HOST: localhost
      DB_PORT: 5432
      DB_NAME: finance_db_test
      TEST_DB_NAME: finance_db_test
    
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.14'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov
    - name: Run tests
      run: |
        python -m pytest --cov=src --cov-report=xml
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

## Test Coverage

While 100% coverage is not the goal, meaningful coverage helps ensure quality:
- **Target**: Reasonable coverage for core functionality (analytics, database operations)
- **Acceptable gaps**: Simple getters/setters, trivial wrapper functions, platform-specific code
- **Critical paths**: Data ingestion pipeline, core analytics functions, database operations

### Generating Coverage Reports
```bash
# Generate terminal coverage report
python -m pytest --cov=src --cov-report=term-missing

# Generate HTML coverage report
python -m pytest --cov=src --cov-report=html

# Generate XML coverage report (for CI tools)
python -m pytest --cov=src --cov-report=xml
```

## Best Practices for Testing Financial Code

### 1. Test Mathematical Properties
Verify that your functions satisfy known mathematical identities:
- `log_returns(P) ≈ simple_returns(P)` for small returns
- ` cumulative_returns(simple_returns(P)) = (P_t / P_0) - 1`
- `annualize_return(periodic_return, periods) = (1 + periodic_return)^periods - 1`
- For a series of identical returns r, rolling volatility should converge to r * sqrt(periods_per_year)

### 2. Use Financial Test Data
Create test data that mimics real financial characteristics:
- Returns typically follow approximately normal distributions (though with fatter tails)
- Volatility clusters (periods of high/low volatility)
- Returns show autocorrelation in squares (but not necessarily in returns themselves)
- Price series tend to trend and mean-revert

### 3. Test Regime Changes
Financial markets have different regimes (bull/bear markets, high/low volatility):
- Test functions across different market regimes
- Verify behavior doesn't break during extreme market stress
- Test transition points between regimes

### 4. Consider Transaction Costs
While not always modeled in analytics functions, be aware of:
- How bid-ask spreads affect returns
- How market impact affects large trades
- How fees affect net performance

### 5. Validate Against Known Sources
When possible, compare results against:
- Established financial calculators
- Published examples in textbooks
- Known values from financial data providers
- Independent implementations

## Troubleshooting Tests

### Common Issues and Solutions

#### Tests Fail Due to Floating Point Precision
**Problem**: `assertEqual(0.1 + 0.2, 0.3)` fails due to floating point representation
**Solution**: Use `assertAlmostEqual` or `np.testing.assert_array_almost_equal` with appropriate decimal places

#### Tests Are Non-Deterministic
**Problem**: Tests that use random data fail intermittently
**Solution**: 
- Set random seeds: `np.random.seed(42)` at start of test
- Use fixed test data instead of random when possible
- For statistical tests, use appropriate tolerances

#### Tests Depend on External State
**Problem**: Tests fail when run in isolation but pass when run after other tests
**Solution**:
- Use proper setUp and tearDown methods
- Don't rely on state created by other tests
- Clean up resources (database connections, files) in tearDown
- Use unique identifiers for test data (e.g., test-specific ticker symbols)

#### Database Tests Fail Due to Missing Test Database
**Problem**: Integration tests requiring database fail when no test database is available
**Solution**:
- Set up a test database following instructions in INSTALLATION.md
- Use environment variables to specify test database connection
- Consider using SQLite for unit tests that don't require PostgreSQL-specific features
- Mark tests that require PostgreSQL with appropriate skip decorators

#### Tests Are Too Slow
**Problem**: Test suite takes too long to run, discouraging frequent testing
**Solution**:
- Separate unit tests (fast) from integration tests (slower)
- Use mocking for external services in unit tests
- Use fixtures to avoid expensive setup in each test
- Consider parallel test execution with `pytest-xdist`
- Skip slow tests by default in development (enable via environment variable)

## Testing Specific Components

### Testing Analytics Functions
Focus on:
- Mathematical correctness with known values
- Edge cases (empty data, single point, all NaN)
- Missing data handling
- Numerical precision
- Consistency with financial theory
- Proper annualization and frequency handling

### Testing Database Operations
Focus on:
- Correct SQL execution
- Proper transaction handling
- Constraint enforcement (primary key, etc.)
- Error handling and recovery
- Performance of common queries
- Schema migration correctness

### Testing ETF Universe
Focus on:
- Completeness of metadata
- Validity of ISIN formats
- Consistency of ticker symbols
- Proper categorization of ETFs
- Correctness of helper functions

### Testing Ingestion Pipeline
Focus on:
- Correct data download (mocked)
- Proper data normalization and cleaning
- Validation of OHLC relationships
- Correct handling of missing/invalid data
- Proper UPSERT behavior
- Handling of failed tickers

## Test Maintenance

### When Tests Fail
When a test fails, follow this process:
1. **Verify the failure** - run the test again to confirm
2. **Understand what changed** - what code or data modification caused the failure
3. **Determine if the test is correct** - does it still test meaningful behavior?
4. **Fix either the code or the test** - if the test is wrong, update it; if the code is wrong, fix it
5. **Add preventive measures** - consider if similar issues could happen elsewhere

### When to Update Tests
Update tests when:
- **Requirements change** - the specification for what the code should do has changed
- **Bugs are fixed** - tests were incorrectly expecting the buggy behavior
- **Refactoring occurs** - internal implementation changes but external behavior should stay the same
- **Edge cases are discovered** - new test cases needed to cover previously untested scenarios
- **Test becomes obsolete** - the functionality being tested has been removed or significantly changed

### When NOT to Update Tests
Generally avoid updating tests when:
- **Just to make them pass** - if the test is testing meaningful behavior and the code is wrong, fix the code
- **To increase coverage artificially** - don't add trivial tests just to boost coverage numbers
- **To test implementation details** - focus on behavior, not how it's implemented internally
- **For flaky tests** - fix the underlying cause of flakiness rather than working around it

## Conclusion

A comprehensive test suite is essential for maintaining the correctness and reliability of the ETF Analytics Project. By following these guidelines, contributors can ensure that:

1. **New functionality is properly tested** before being merged
2. **Existing functionality remains working** as the project evolves
3. **Regression bugs are caught early** in the development process
4. **The test suite remains meaningful and maintainable** over time
5. **Users can have confidence** in the correctness of financial calculations and data handling

Remember that the goal of testing is not to achieve a specific percentage of coverage, but to gain confidence that the software behaves correctly under the conditions it's designed to handle. Well-written tests serve as documentation, regression prevention, and design assistance all in one package.