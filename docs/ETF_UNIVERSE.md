# ETF Research Universe

## Overview

The ETF Analytics Project maintains a carefully curated research universe of Exchange-Traded Funds (ETFs) designed to support comprehensive quantitative analysis across asset classes, geographies, sectors, and investment factors.

This document describes the structure, selection criteria, and contents of the research universe.

## Universe Structure

The research universe is defined in `src/finance_analytics/universe/etfs.py` and consists of ETF objects with comprehensive metadata.

### ETF Definition

Each ETF in the universe is represented by an `ETF` dataclass with the following attributes:

#### Identity Fields
- `isin`: International Securities Identification Number - unique global identifier
- `fund_name`: Official name of the ETF
- `provider`: ETF provider/issuer (e.g., Vanguard, iShares, State Street)

#### Classification Fields
- `domicile`: Legal domicile of the ETF (ISO country code)
- `asset_class`: Broad asset classification (Equity, Fixed Income, Commodity, etc.)
- `geography`: Primary geographic focus (Global, United States, Europe, Japan, etc.)
- `strategy`: Investment strategy (Broad Market, Large Cap, Sector, Factor, etc.)
- `benchmark`: Index that the ETF seeks to track
- `distribution_policy`: Distribution policy (ACC for accumulating, DIS for distributing)
- `ter`: Total Expense Ratio as decimal (e.g., 0.0015 for 0.15%)

#### Research Metadata
- `research_role`: Role this ETF plays in the research universe (e.g., "Global equity core", "US value factor")
- `research_rationale**: Explanation of why this ETF is included in the universe

#### Market Listings
- `listings`: Tuple of `Listing` objects representing market listings
  - Each `Listing` contains:
    - `exchange`: Exchange where listed (e.g., "LSE" for London Stock Exchange)
    - `yahoo_ticker`: Ticker symbol used by Yahoo Finance
    - `trading_currency`: Currency in which the ETF trades
    - `listing_currency`: Currency in which the ETF is listed
    - `is_primary`: Boolean indicating if this is the primary listing for Yahoo Finance purposes

## Selection Criteria

ETFs are selected for inclusion in the research universe based on multiple criteria:

### 1. Liquidity
- Average daily trading volume sufficient for reliable price data
- Tight bid-ask spreads to minimize transaction costs
- Adequate market depth for reasonable execution prices

### 2. Historical Availability
- Sufficient history for meaningful backtesting and analysis
- Preference for ETFs with longer track records
- Consideration of inception date relative to analysis requirements

### 3. Representativeness
- ETF should accurately represent its target exposure
- Low tracking error relative to stated benchmark
- Transparent and rule-based index methodology

### 4. Cost Efficiency
- Competitive expense ratios within category
- Consideration of total cost of ownership (including spreads, market impact)

### 5. Structural Factors
- Physical replication preferred over synthetic where appropriate
- Transparent securities lending practices
- Clear dividend/reinvestment policies

### 6. Research Utility
- Fills a specific niche in the factor/geography/sector matrix
- Enables cross-provider or cross-index comparisons
- Supports specific investment factor or regime analysis

## Organization by Asset Class

The research universe is organized into thematic sections:

### 1. Global / Developed Market Equities
- Broad market exposure to developed economies
- Multiple providers and methodologies for comparison
- Regional breakdowns (Europe, Pacific ex-Japan, Japan, Asia-Pacific)

### 2. United States Equities
- Comprehensive coverage of US equity market
- Size-based segmentation (Large Cap, Mid Cap)
- Sector-specific ETFs for all GICS sectors
- Style and factor ETFs (Value, Growth, Quality, Momentum, Minimum Volatility, Size)

### 3. Regional / Emerging Market Equities
- Country-specific exposure for major emerging markets
- Regional emerging market baskets
- BRICS and other emerging market groupings

### 4. Factor / Smart Beta Equities
- Single-factor ETFs (Value, Momentum, Quality, Minimum Volatility, Size)
- Multi-factor implementations
- Global and regional factor exposures

### 5. Sector / Industry Equities
- All 11 GICS sectors represented
- Multiple providers for cross-comparison
- Both defensive and cyclical sectors covered

### 6. Fixed Income
- Government bonds (US Treasuries, global aggregates)
- Corporate bonds (investment grade, high yield)
- Emerging market bonds
- Duration-specific exposure (short, intermediate, long)
- Inflation-protected securities

### 7. Commodities / Precious Metals
- Physical precious metals (gold, silver)
- Broad commodity baskets
- Individual commodities (oil, copper, agricultural)
- Commodity producers equity exposure

### 8. REITS / Alternatives
- Global real estate exposure
- Infrastructure exposure
- Specialized alternative asset classes

## Usage Guidelines

### Accessing the Universe

In Python code, access the universe through the provided helper functions:

```python
from src.finance_analytics.universe.etfs import (
    get_all_etfs,
    get_etf_by_isin,
    get_primary_listings
)

# Get all ETFs in the universe
all_etfs = get_all_etfs()

# Get a specific ETF by ISIN
vanguard_all_world = get_etf_by_isin("IE00BK5BQT80")

# Get primary Yahoo Finance listings for all ETFs
primary_listings = get_primary_listings()
# Returns tuple of Listing objects suitable for ticker extraction
```

### Extracting Ticker Lists

For use with the data ingestion and analytics functions:

```python
from src.finance_analytics.universe.etfs import get_primary_listings

def get_yahoo_tickers():
    """Extract Yahoo Finance tickers from primary listings."""
    listings = get_primary_listings()
    return [listing.yahoo_ticker for listing in listings]

# Or use the built-in function from config.py
from src.finance_analytics.config import get_etf_tickers
tickers = get_etf_tickers()  # Returns Yahoo tickers from primary listings
```

### Understanding ETF Roles

Each ETF is assigned a `research_role` that describes its purpose in the universe:

#### Core Holdings
- Broad market representations serving as benchmarks
- Examples: "Global equity core", "US large-cap core", "Global bond core"

#### Alternative Implementations
- Different providers tracking same/similar index
- Examples: "US large-cap alternative", "Developed-market alternative"
- Useful for studying tracking differences and implementation variance

#### Factor Exposures
- Pure factor exposure for attribution analysis
- Examples: "Global value factor", "European quality factor", "US momentum factor"

#### Specialized Exposures
- Country, sector, or thematic exposures
- Examples: "Japan equities", "Healthcare sector", "Gold miners"

## Maintenance and Updates

### Adding New ETFs

To add a new ETF to the universe:

1. **Research**: Verify the ETF meets selection criteria
2. **Define**: Create an ETF object with all required metadata
3. **Insert**: Add to the ETF_UNIVERSE tuple in the appropriate section
4. **Test**: Verify that the ticker downloads correctly via yfinance
5. **Document**: Update research_rationale and ensure proper categorization

### Removing ETFs

To remove an ETF from the universe:
1. **Review**: Ensure removal won't create gaps in coverage
2. **Remove**: Delete the ETF object from ETF_UNIVERSE tuple
3. **Verify**: Confirm no code depends specifically on the removed ETF (unless intended)

### Modifying Existing ETFs

Updates to existing ETFs should be made carefully:
- **Metadata Corrections**: Fix errors in provider, domicile, etc.
- ** TER Updates**: Update expense ratio when it changes
- **Research Role**: Only change if the fundamental purpose in the universe changes
- ** listings**: Update if primary listing changes or new listings become available

## Data Quality and Verification

### Ticker Symbol Verification
The `get_etf_tickers()` function in `src/finance_analytics/config.py` includes error handling:
- Attempts to load tickers from the universe definition
- Falls back to ETF_TICKERS environment variable if universe loading fails
- Validates that tickers are non-empty strings
- Converts to uppercase and strips whitespace

### Historical Data Validation
During data ingestion (`update_database.py`):
- Failed ticker downloads are logged and trigger fallback to environment variable
- Empty or invalid data responses are detected and handled
- Data validation checks for OHLC relationships and plausible values

### Survivorship Bias Considerations

#### Current Approach
The universe is defined as a point-in-time list of ETFs that are currently available. This approach introduces potential survivorship bias when analyzing historical data because:

1. **Delisted ETFs**: ETFs that have been delisted or liquidated are not included
2. **Changed Tickers**: ETFs that have changed ticker symbols may not be properly tracked
3. **Strategy Drift**: ETFs that have significantly changed their investment approach

#### Mitigation Strategies
1. **Explicit Acknowledgment**: Documentation acknowledges this limitation
2. **Long-Term Holdings**: Preference for ETFs with longer histories reduces but doesn't eliminate bias
3. **Core Focus**: Analysis often focuses on broader market exposures less susceptible to individual ETF issues
4. **Cross-Provider Comparison**: Multiple ETFs tracking similar indices help isolate ETF-specific effects

#### Recommendations for Historical Analysis
When using the universe for historical analysis:
1. **Acknowledge Limitation**: Explicitly state the potential for survivorship bias
2. **Sensitivity Analysis**: Test results with different universe definitions
3. **Benchmark Comparison**: Compare against broad market indices less affected by survivorship bias
4. **Survivorship-Free Universes**: For critical applications, consider constructing a point-in-time universe for each historical period

## Detailed Sections

### Global / Developed Market Equities
This section provides exposure to developed economies worldwide through multiple providers and methodologies, enabling:
- Cross-provider comparison of identical exposures
- Regional allocation analysis
- Global equity benchmarking

### United States Equities
The most granular section, providing:
- Complete market cap segmentation (large, mid, small)
- Comprehensive sector coverage (all 11 GICS sectors)
- Factor exposures (value, growth, quality, momentum, volatility, size)
- Multiple implementations of major indices (S&P 500, NASDAQ-100, etc.)

### Regional / Emerging Market Equities
Provides targeted exposure to:
- Individual emerging market countries (China, India, South Korea, Brazil, etc.)
- Regional emerging market baskets
- Country-specific analysis for emerging market research

### Factor / Smart Beta Equities
Enables factor-based analysis through:
- Pure factor ETFs for clean factor exposure
- Factor timing and rotation analysis
- Cross-factor comparison (value vs momentum vs quality)
- Factor integration and portfolio construction applications

### Sector / Industry Equities
Supports sector analysis via:
- Business cycle analysis (cyclical vs defensive sectors)
- Sector rotation strategies
- Relative valuation analysis
- Defensiveness testing during market stress

### Fixed Income
Provides bond market exposure for:
- Interest rate analysis and duration management
- Credit spread analysis
- Yield curve positioning
- Inflation protection strategies
- Global diversification benefits

### Commodities / Precious Metals
Enables commodity market analysis:
- Inflation hedging properties
- Dollar strength/weakness analysis
- Commodity cycle identification
- Precious metals as safe-haven assets
- Industrial commodity exposure for growth analysis

### REITS / Alternatives
Provides exposure to alternative asset classes:
- Real estate market cycles
- Infrastructure investment trends
- Diversification benefits from low-correlation assets
- Specialized income generation strategies

## Statistical Summary

As of the latest version, the research universe contains:

| Category | Count | Percentage |
|----------|-------|------------|
| Global / Developed Market Equities | 8 | 25.0% |
| United States Equities | 12 | 37.5% |
| Regional / Emerging Market Equities | 4 | 12.5% |
| Factor / Smart Beta Equities | 8 | 25.0% |
| Sector / Industry Equities | 12 | 37.5% |
| Fixed Income | 12 | 37.5% |
| Commodities / Precious Metals | 6 | 18.8% |
| REITS / Alternatives | 8 | 25.0% |

*Note: Percentages exceed 100% because some ETFs may be categorized in multiple sections based on different classification systems.*

## Design Philosophy

### Completeness vs. Manageability
The universe aims to be comprehensive enough for meaningful analysis while remaining manageable for:
- Data ingestion and storage
- Computational efficiency in analytics
- Cognitive accessibility for users

### Provider Diversity
Multiple providers are included for major exposures to:
- Enable implementation difference analysis
- Reduce reliance on any single provider
- Support cross-provider research
- Provide alternatives in case of provider-specific issues

### Methodology Transparency
Preference for ETFs that track:
- Well-known, transparent indices
- Rules-based methodologies
- Publicly documented construction rules
- Replicable investment approaches

### Research Utility Over Popularity
While liquidity is important, selection prioritizes:
- Analytical usefulness over pure popularity
- Ability to answer specific research questions
- Coverage of underrepresented niches
- Educational value for demonstrating concepts

## Limitations and Considerations

### Known Limitations
1. **Point-in-Time Bias**: Universe reflects current offerings, not historical availability
2. **Liquidity Variability**: Some specialized ETFs may have lower liquidity
3. **Tracking Error**: Not all ETFs perfectly track their stated benchmarks
4. **Structural Differences**: ETFs may differ in replication method, lending practices, etc.
5. **Geographic Definitions**: Geography classifications may differ between providers

### Usage Recommendations
1. **Define Your Analysis Universe**: Select subset appropriate for your specific analysis
2. **Check Liquidity**: Verify adequate trading volume for your trade size
3. **Understand Replication**: Know whether ETF uses physical or synthetic replication
4. **Consider Costs**: Factor in TER and trading costs for return calculations
5. **Validate Exposures**: Confirm ETF actually provides expected exposure through holdings analysis

## Example Usage Scenarios

### Scenario 1: Global Equity Analysis
```python
# Select global equity ETFs
global_etfs = [
    "VWRP.L",  # Vanguard FTSE All-World
    " VHVG.L",  # Vanguard FTSE Developed World
    "SWLD.L",  # SPDR MSCI World
    "IWDA.L"   # iShares Core MSCI World
]
# Use for: Global market benchmarking, regional allocation analysis
```

### Scenario 2: US Factor Analysis
```python
# Select US factor ETFs
us_factor_etfs = [
    "SPYV.L",  # SPDR Portfolio S&P 500 Value
    "SPYG.L",  # SPDR Portfolio S&P 500 Growth
    "IUSL.L",  # iShares Edge MSCI USA Value Factor
    "IUSQ.L",  # iShares Edge MSCI USA Quality Factor
    "IUSM.L",  # iShares Edge MSCI USA Momentum Factor
    "IUSV.L",  # iShares Edge MSCI USA Minimum Volatility
    "IUSN.L",  # iShares Edge MSCI USA Size Factor
]
# Use for: Factor timing, factor premium analysis, portfolio construction
```

### Scenario 3: Fixed Income Duration Analysis
```python
# Select bond ETFs by duration
bond_etfs = {
    "SHY": "IE00B3F81R35",  # 1-3 Year Treasury
    "IEI": "IE00B3VWN518",  # 3-7 Year Treasury
    "IEF": "IE00B3VWN843",  # 7-10 Year Treasury
    "TLT": "IE00B4WXJJ64",  # 20+ Year Treasury
    "BND": "IE00B4K48X80",  # Global Aggregate Bond
}
# Use for: Yield curve analysis, interest rate sensitivity, duration matching
```

## Conclusion

The ETF Analytics Project research universe provides a solid foundation for quantitative finance analysis, offering:
- Broad asset class coverage
- Multiple implementations for comparison
- Factor and sector granularity
- Fixed income and alternative exposure
- Transparent methodology and documentation

Users should select appropriate subsets based on their specific analysis requirements while being mindful of the universe's design principles and limitations.