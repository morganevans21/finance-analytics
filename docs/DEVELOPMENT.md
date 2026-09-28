# Development Guidelines

This document outlines the guidelines and best practices for contributing to the ETF Analytics Project.

## Project Philosophy

Before contributing, it's important to understand the project's core principles:

1. **Correctness over cleverness** - Prefer explicit, readable, testable code
2. **Incremental development** - Build in small, working stages
3. **Separation of concerns** - Keep data acquisition, storage, analytics, and presentation layers distinct
4. **Reuse logic** - Avoid duplicating calculations between modules
5. **Financial methodology** - Treat calculations as quantitative methodology, not ordinary arithmetic
6. **Research integrity** - Never manufacture analytical results or invent data
7. **Portfolio quality** - Develop to professional standards appropriate for demonstrating competence

## Code Style

### Python Standards

The project targets Python 3.14 and follows these conventions:

#### Type Hints
- Use type hints for all function parameters and return values
- Use built-in collection types (list, dict, etc.) rather than typing module equivalents when possible
- Use Optional[T] for values that can be None
- Use Union[T1, T2] for values that can be one of several types

#### Naming Conventions
- **Functions and variables**: snake_case (e.g., `calculate_returns`, `price_data`)
- **Classes**: PascalCase (e.g., `ETFListing`, `PriceValidator`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `MAX_DRAWDOWN_WINDOW`, `DEFAULT_START_DATE`)
- **Modules**: snake_case (e.g., `returns.py`, `volatility.py`)
- **Packages**: snake_case (e.g., `finance_analytics`, `data_validation`)

#### Formatting
- Maximum line length: 88 characters (Black default)
- Use 4 spaces per indent (no tabs)
- Import ordering: standard library, third-party, local application
- Blank lines: 2 between function/class definitions, 1 between method definitions in a class
- Trailing commas: Use in multi-line lists/tuples/dicts for easier diffs

### Code Organization

#### File Structure
```
src/
└── finance_analytics/          # Main package
    ├── analytics/              # Financial calculation functions
    │   ├── returns.py          # Return calculations
    │   ├── volatility.py       # Volatility measures
    │   ├── drawdown.py         # Drawdown analysis
    │   ├── risk_metrics.py     # Risk metrics (VaR, Sharpe, etc.)
    │   ├── market_sensitivity.py # Beta, correlation, etc.
    │   └── utils.py            # Helper functions
    ├── database/               # Database access and schema
    │   ├── connection.py       # Database connection handling
    │   ├── schema.py           # Schema initialization and migrations
    │   └── operations.py       # Common database operations
    ├── universe/               # ETF universe definition
    │   └── etfs.py             # ETF dataclasses and universe tuple
    ├── validation/             # Data validation and cleaning
    │   ├── cleaning.py         # Data cleaning functions
    │   ├── normalization.py    # Data normalization functions
    │   └── validation.py       # Data validation functions
    ├── ingestion/              # Data ingestion pipeline
    │   ├── download.py         # Yahoo Finance data download
    │   ├── normalization.py    # Data normalization for ingestion
    │   ├── merging.py          # Data merging functions
    │   └── validation.py       # Ingestion-specific validation
    └── config.py               # Configuration management
```

#### Module Responsibilities
Each module should have a single, well-defined responsibility:

- **analytics**: Pure financial calculation functions that operate on pandas Series/DataFrames
- **database**: PostgreSQL interaction (connection, schema, operations)
- **universe**: ETF definitions and research metadata
- **validation**: Data quality checks and validation functions
- **ingestion**: Data download, normalization, cleaning, and preparation for storage
- **config**: Environment variable-based configuration management

## Development Workflow

### Making Changes

1. **Understand the Issue**: Clearly understand what problem you're solving
2. **Check Existing Code**: Look for similar patterns or existing solutions
3. **Create Branch**: Work in a feature branch (`git checkout -b feature/description`)
4. **Implement Changes**: Make the smallest coherent change that solves the problem
5. **Add Tests**: Include unit tests for new functionality
6. **Run Tests**: Ensure all tests pass
7. **Update Documentation**: Update relevant documentation files
8. **Commit**: Write clear, descriptive commit messages
9. **Pull Request**: Submit for review following the project's contribution process

### Commit Messages

Write clear, descriptive commit messages following this format:

```
type(scope): description

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Formatting, missing semicolons, etc. (no code change)
- `refactor`: Code refactoring (no feature change, no bug fix)
- `perf`: Performance improvement
- `test`: Adding or correcting tests
- `chore`: Changes to build process or auxiliary tools

**Examples:**
- `feat(analytics): add Sortino ratio calculation`
- `fix(database): handle missing volume column in legacy databases`
- `docs(ETF_UNIVERSE): update research rationale for Vanguard FTSE All-World`
- `refactor(validation): extract OHLC validation to separate function`
- `test(analytics): add unit tests for rolling volatility edge cases`

### Pull Request Process

1. **Ensure Branch is Up-to-Date**: `git pull origin main`
2. **Run Tests**: Confirm all tests pass locally
3. **Submit PR**: Create pull request against main branch
4. **Fill Template**: Complete all sections of the PR template
5. **Address Feedback**: Respond to reviewer comments and make requested changes
6. **Maintainers Approval**: Wait for approval from project maintainers
7. **Merge**: Once approved, maintainers will merge (or you may merge if permitted)

## Testing Guidelines

### Test Philosophy
Tests should protect meaningful behavior, not just increase coverage. For financial calculations, prioritize:
- Mathematical correctness
- Edge cases
- Numerical stability
- Correct frequency/annualization
- Correct handling of missing data

### Test Organization
```
tests/
├── unit/                 # Unit tests for individual components
│   ├── test_analytics.py     # Analytics function tests
│   ├── test_database.py      # Database operation tests
│   ├── test_universe.py      # ETF universe tests
│   └── test_ingestion.py     # Data ingestion tests
└── integration/          # Integration tests
    ├── test_database_integration.py  # Database + ingestion workflow
    └── test_end_to_end.py          # Full pipeline tests
```

### Unit Test Guidelines

#### Test Structure
Use the `unittest` framework with these patterns:

```python
import unittest
import numpy as np
import pandas as pd
from finance_analytics.analytics import some_function

class TestSomeFunction(unittest.TestCase):
    def setUp(self):
        """Set up test data and fixtures."""
        # Create reusable test data
        self.test_data = pd.Series([1, 2, 3, 4, 5])
    
    def test_normal_case(self):
        """Test typical usage scenario."""
        result = some_function(self.test_data)
        self.assertEqual(result, expected_value)
    
    def test_edge_cases(self):
        """Test boundary conditions and edge cases."""
        # Test with empty data
        # Test with single element
        # Test with all NaN values
        # Test with extreme values
    
    def test_error_conditions(self):
        """Test that appropriate errors are raised for invalid input."""
        with self.assertRaises(ValueError):
            some_function(invalid_input)
```

#### Financial Test Specifics
- **Use known values**: Test with data where expected results can be calculated manually
- **Tolerance-based comparisons**: Use `assertAlmostEqual` or `np.testing.assert_array_almost_equal` for floating point comparisons
- **Test both typical and edge cases**: Include normal market conditions and extreme scenarios
- **Test missing data handling**: Verify behavior with NaN values, empty series, etc.
- **Test annualization correctness**: Ensure periodic-to-annual conversions are accurate

### Integration Test Guidelines

Integration tests should verify:
- Database operations work correctly
- Data flows properly between components
- End-to-end functionality works as expected
- Configuration is properly loaded and used
- The update pipeline functions correctly

### Running Tests

#### Local Testing
```bash
# Run all tests
python -m pytest

# Run only unit tests
python -m pytest tests/unit/

# Run only integration tests
python -m pytest tests/integration/

# Run tests with coverage
python -m pytest --cov=src --cov-report=html

# Run specific test file
python -m pytest tests/unit/test_analytics.py

# Run specific test function
python -m pytest tests/unit/test_analytics.py::TestReturns::test_simple_returns
```

#### Continuous Integration
The project may use CI services (GitHub Actions, etc.) that automatically run tests on pull requests and pushes to main.

## Database Guidelines

### Schema Changes
All schema changes must go through the `initialize_database_schema()` function in `src/finance_analytics/database/schema.py`:

1. **Never manually modify the database schema** outside of this function
2. **Add new columns** to the `expected_columns` dictionary
3. **The function will automatically**:
   - Create the table if it doesn't exist
   - Add missing columns to existing tables
   - Ensure primary key constraint exists
4. **Test schema changes** with both new and existing databases

### Data Integrity
- **Prefer database constraints** when meaningful (primary key, not null where appropriate)
- **Validate data before storage** using validation functions
- **Handle errors gracefully** - don't let one bad ticker stop processing of others
- **Log data quality issues** for monitoring and debugging

### Performance Considerations
- **Use parameterized queries** to prevent SQL injection
- **Leverage the primary key index** for efficient ticker/date lookups
- **Consider appropriate indexing** for common query patterns
- **Use UPSERT** (`INSERT ... ON CONFLICT DO UPDATE`) to handle data corrections

## Analytics Guidelines

### Function Design
All analytics functions should:
1. **Be pure functions** - no side effects, same input always produces same output
2. **Handle edge cases gracefully** - empty inputs, insufficient data, NaN values
3. **Return appropriate types** - typically pandas Series/DataFrame or float
4. **Have clear, comprehensive docstrings** with examples
5. **Be thoroughly tested** - unit tests for normal cases, edge cases, and error conditions
6. **Follow financial methodology** - explicitly state assumptions and limitations

### Return Conventions
- **Return Series/DataFrame** when returning time series or panel data
- **Return float** when returning a single metric value
- **Return NaN** for undefined or incalculable results (rather than raising exceptions)
- **Preserve indices** when possible to maintain time series alignment
- **Document index/return format** clearly in docstrings

### Financial Assumptions
All financial assumptions must be:
- **Explicitly stated** in function docstrings
- **Configurable** when reasonable (risk-free rates, target returns, etc.)
- **Consistent** with industry standards where applicable
- **Documented** with rationale for non-standard choices

### Example: Well-Designed Function
```python
def example_function(returns: pd.Series, window: int = 30) -> pd.Series:
    """
    Calculate example metric from returns series.
    
    This function calculates [description of what it does].
    
    Parameters
    ----------
    returns : pd.Series
        Return series, typically daily returns. Index should be DatetimeIndex.
        NaN values are handled by [description of handling].
        
    window : int, default 30
        Rolling window size in periods. Must be positive integer.
        
    Returns
    -------
    pd.Series
        Example metric values with same index as input.
        First (window-1) values will be NaN due to insufficient history.
        
    Examples
    --------
    >>> returns = pd.Series([0.01, 0.02, -0.01, 0.015])
    >>> result = example_function(returns, window=2)
    >>> print(result)
    2023-01-01         NaN
    2023-01-02    0.0150
    2023-01-03    0.0050
    2023-01-04    0.0025
    dtype: float64
    
    Notes
    -----
    [Any important assumptions, limitations, or references]
    """
    # Input validation
    if not isinstance(returns, pd.Series):
        raise TypeError("returns must be a pandas Series")
    if window <= 0:
        raise ValueError("window must be a positive integer")
    
    # Handle edge cases
    if len(returns) == 0:
        return pd.Series(dtype=float)
    
    # Implementation
    # [Actual calculation logic]
    
    return result
```

## Ingestion Guidelines

### Data Download
- **Respect rate limits** - be conservative with Yahoo Finance API calls
- **Handle failures gracefully** - log failed tickers but continue processing others
- **Validate downloaded data** - check for empty responses, invalid formats
- **Store both raw and adjusted prices** - as provided by Yahoo (do not re-adjust)

### Data Validation
- **Validate OHLC relationships** - High >= Low, High >= Open/Close, Low <= Open/Close
- **Check for extreme values** - prices should be positive, volume non-negative
- **Verify date continuity** - reasonable gaps for weekends/holidays, not massive unexplained gaps
- **Check data completeness** - reasonable amount of data for requested date range

### Data Normalization
- **Standardize formats** - consistent date formats, ticker casing, column names
- **Handle missing data** - decide on strategy (drop, fill, interpolate) based on context
- **Remove duplicates** - ensure uniqueness by (date, ticker) before storage
- **Sort data** - typically by ticker then date for efficient processing

## UI/Streamlit Guidelines

### Separation of Concerns
- **Keep calculations in analytics module** - don't implement financial logic directly in Streamlit code
- **Use caching appropriately** - `@st.cache_data` for data, `@st.cache_resource` for expensive resources
- **Handle loading states** - show spinners or progress indicators for long operations
- **Graceful degradation** - if parts of the dashboard fail, others should still work

### Performance
- **Minimize data transfers** - only fetch needed data from database
- **Use efficient queries** - leverage indexes, avoid SELECT * when not needed
- **Cache expensive computations** - don't recalculate the same metrics repeatedly
- **Consider pagination** - for large datasets, show reasonable amounts at a time

### User Experience
- **Clear labels and units** - always indicate what numbers represent and their units
- **Informative tooltips** - explain complex metrics on hover
- **Responsive design** - work well on different screen sizes
- **Accessibility considerations** - color contrast, keyboard navigation, etc.

## Documentation Guidelines

### Docstrings
All public functions and classes should have docstrings following the NumPy or Google style:
- **Summary line**: One-sentence description
- **Parameters**: List each parameter with type and description
- **Returns**: Describe return value and type
- **Examples**: Optional but encouraged for complex functions
- **Notes**: Optional for important assumptions, limitations, or references

### Documentation Files
Keep documentation in the `docs/` directory up to date:
- **API_REFERENCE.md**: Complete reference for all public APIs
- **USAGE.md**: How to use the project for various tasks
- **DEVELOPMENT.md**: This file - contribution guidelines
- **DATA_MODEL.md**: Database schema and data flow
- **ETF_UNIVERSE.md**: Description of the ETF research universe
- **ARCHITECTURE.md**: System architecture and design decisions
- **INSTALLATION.md**: Setup and installation instructions

### Documentation Principles
- **Write for the audience** - assume readers have basic Python and finance knowledge
- **Be explicit about assumptions** - don't make readers guess how calculations work
- **Provide examples** - show how to use functions and interpret results
- **Acknowledge limitations** - be transparent about what the software does and doesn't do
- **Keep it updated** - documentation should match the current implementation

## Security Guidelines

### Secrets Management
- **Never hard-code secrets** - passwords, API keys, etc.
- **Use environment variables** - via python-dotenv and `.env` file
- **Never commit `.env` with real credentials** - only commit `.env.example`
- **Use least-privilege principles** - database users should have only necessary permissions

### Data Security
- **Market data is public** - but still follow responsible data handling practices
- **No PII stored** - the project should not collect or store personally identifiable information
- **Volume data sensitivity** - be aware that volume patterns could reveal trading behavior for large positions

### Secure Coding
- **Use parameterized queries** - prevent SQL injection
- **Validate inputs** - don't trust external data without validation
- **Handle errors safely** - don't leak stack traces or internal details to users
- **Keep dependencies updated** - regularly update to patch security vulnerabilities

## Performance Guidelines

### When to Optimize
Follow this progression:
1. **Make it work** - implement correct solution
2. **Make it right** - follow best practices and guidelines
3. **Make it fast** - only optimize after profiling shows a bottleneck

### Profiling
Use profiling tools to identify bottlenecks:
- **cProfile** - for CPU profiling
- **memory_profiler** - for memory usage analysis
- **line_profiler** - for line-by-line profiling
- **Streamlit's built-in profiling** - for dashboard performance

### Common Optimization Techniques
- **Vectorization** - use pandas/numpy vectorized operations instead of loops
- **Efficient algorithms** - choose appropriate algorithms for the problem size
- **Caching** - cache expensive computations that are reused
- **Database indexing** - ensure appropriate indexes for query patterns
- **Connection pooling** - reuse database connections instead of recreating

### Performance Targets
- **Data ingestion**: Should complete in reasonable time for target universe size
- **Analytics functions**: Should return quickly for typical dataset sizes
- **Dashboard interactions**: Should feel responsive (<1 second for simple interactions)
- **Memory usage**: Should be reasonable for target deployment environments

## Legal and Ethical Considerations

### Data Usage
- **Yahoo Finance Terms**: Comply with Yahoo Finance's terms of service for data usage
- **Attribution**: Acknowledge data sources when appropriate
- **Usage restrictions**: Respect any limitations on data redistribution or commercial use

### Financial Advice
- **Educational purpose only** - the project is for educational and research use
- **Not financial advice** - do not present analysis as investment recommendations
- **Past performance disclaimer** - remember that past performance does not guarantee future results
- **Risk disclosure** - all investments carry risk of loss

### Reproducibility
- **Enable reproducibility** - make it possible for others to replicate your analysis
- **Version control** - track changes to code, configuration, and data definitions
- **Document assumptions** - clearly state all assumptions made in analysis
- **Seed randomness** - if using random numbers, use fixed seeds for reproducibility

## Review Process

### What Maintainers Look For
When reviewing pull requests, maintainers typically check:

1. **Correctness**: Does the code solve the stated problem correctly?
2. **Guideline adherence**: Does the code follow the project's guidelines?
3. **Test coverage**: Are there appropriate tests for new functionality?
4. **Documentation**: Is documentation updated as needed?
5. **Breaking changes**: Does the change introduce breaking changes that need consideration?
6. **Performance**: Are there any obvious performance issues?
7. **Security**: Are there any security concerns?
8. **Merge readiness**: Is the change ready to be merged into main?

### Responding to Reviews
1. **Be grateful** - thank reviewers for their time and feedback
2. **Be clear** - respond to each point raised in the review
3. **Be timely** - address review comments in a reasonable timeframe
4. **Be flexible** - be willing to adjust your approach based on feedback
5. **Explain decisions** - when disagreeing, explain your reasoning clearly
6. **Keep it focused** - address the feedback, don't introduce unrelated changes

## Getting Help

If you need help during development:

1. **Check the documentation** - most questions are answered in the docs/
2. **Look at existing code** - see how similar problems were solved
3. **Run the tests** - see how similar functionality is tested
4. **Ask in project channels** - if available, ask in designated communication channels
5. **Open an issue** - if you've encountered a bug or need clarification
6. **Consult maintainers** - for complex architectural or design questions

## Conclusion

By following these guidelines, you'll help ensure that the ETF Analytics Project remains:
- Correct and reliable
- Maintainable and extensible
- Consistent in quality and approach
- Aligned with the project's goals and values
- Suitable for inclusion in a professional portfolio

Remember that the project is as much about learning and demonstrating good engineering practice as it is about the specific functionality being implemented. Your contributions should reflect both technical competence and thoughtful consideration of the broader context in which the software will be used.