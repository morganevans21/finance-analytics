"""
Definition of the ETF research universe.

This module contains the ETFs selected for analysis in the project.

The universe is deliberately defined separately from:
    - market-data acquisition;
    - database access;
    - financial calculations;
    - Streamlit presentation.

ISIN identifies the fund/security.
Yahoo Finance ticker identifies a particular market listing.
"""

from dataclasses import dataclass


# ---------------------------------------------------------------------
# Listing
# ---------------------------------------------------------------------

@dataclass(frozen=True)
class Listing:
    """A market listing of an ETF."""

    exchange: str
    yahoo_ticker: str
    trading_currency: str
    listing_currency: str
    is_primary: bool = True


# ---------------------------------------------------------------------
# ETF
# ---------------------------------------------------------------------

@dataclass(frozen=True)
class ETF:
    """Definition of an ETF in the research universe."""

    # Identity
    isin: str
    fund_name: str
    provider: str

    # Fund classification
    domicile: str
    asset_class: str
    geography: str
    strategy: str

    # Fund characteristics
    benchmark: str
    distribution_policy: str
    ter: float

    # Research metadata
    research_role: str
    research_rationale: str

    # Market listings
    listings: tuple[Listing, ...]


# ---------------------------------------------------------------------
# Research universe
# ---------------------------------------------------------------------

ETF_UNIVERSE: tuple[ETF, ...] = (

    ETF(
        isin="IE00BK5BQT80",
        fund_name="Vanguard FTSE All-World UCITS ETF",
        provider="Vanguard",
        domicile="IE",
        asset_class="Equity",
        geography="Global",
        strategy="Broad Market",
        benchmark="FTSE All-World Index",
        distribution_policy="ACC",
        ter=0.0022,
        research_role="Global equity core",
        research_rationale=(
            "Broad developed- and emerging-market equity exposure "
            "providing a representative global equity allocation."
        ),
        listings=(
            Listing(
                exchange="LSE",
                yahoo_ticker="VWRP.L",
                trading_currency="GBP",
                listing_currency="GBP",
            ),
        ),
    ),

    # =================================================================

    # GLOBAL / DEVELOPED MARKET EQUITIES

    # =================================================================

    ETF(
        isin="IE00BK5BQV03",
        fund_name="Vanguard FTSE Developed World UCITS ETF",
        provider="Vanguard",
        domicile="IE",
        asset_class="Equity",
        geography="Developed Markets",
        strategy="Broad Market",
        benchmark="FTSE Developed World Index",
        distribution_policy="ACC",
        ter=0.0012,
        research_role="Developed-market alternative",
        research_rationale=(
            "Alternative developed-market benchmark using the FTSE "
            "methodology for cross-index comparison."
        ),
        listings=(
            Listing("LSE", "VHVG.L", "USD", "GBP"),
        ),
    ),

    ETF(
        isin="IE00B3YLTY66",
        fund_name="SPDR MSCI World UCITS ETF",
        provider="State Street SPDR",
        domicile="IE",
        asset_class="Equity",
        geography="Developed Markets",
        strategy="Broad Market",
        benchmark="MSCI World Index",
        distribution_policy="ACC",
        ter=0.0012,
        research_role="Benchmark replication",
        research_rationale=(
            "Provides a second implementation of the MSCI World "
            "exposure for tracking-error and implementation analysis."
        ),
        listings=(
            Listing("LSE", "SWLD.L", "USD", "GBP"),
        ),
    ),

    ETF(
        isin="IE00B4K48X80",
        fund_name="iShares Core MSCI Europe UCITS ETF",
        provider="iShares",
        domicile="IE",
        asset_class="Equity",
        geography="Europe",
        strategy="Broad Market",
        benchmark="MSCI Europe Index",
        distribution_policy="ACC",
        ter=0.0012,
        research_role="European developed equities",
        research_rationale=(
            "Broad European equity exposure for regional allocation "
            "and relative-performance analysis."
        ),
        listings=(
            Listing("LSE", "IMEU.L", "EUR", "GBP"),
        ),
    ),

    ETF(
        isin="IE00B4K6B022",
        fund_name="iShares Core MSCI Pacific ex-Japan UCITS ETF",
        provider="iShares",
        domicile="IE",
        asset_class="Equity",
        geography="Pacific ex Japan",
        strategy="Broad Market",
        benchmark="MSCI Pacific ex Japan Index",
        distribution_policy="ACC",
        ter=0.0020,
        research_role="Pacific regional equities",
        research_rationale=(
            "Captures developed Pacific markets excluding Japan "
            "for regional diversification analysis."
        ),
        listings=(
            Listing("LSE", "CPXJ.L", "USD", "GBP"),
        ),
    ),

    ETF(
        isin="IE00B95PGT31",
        fund_name="Vanguard FTSE Japan UCITS ETF",
        provider="Vanguard",
        domicile="IE",
        asset_class="Equity",
        geography="Japan",
        strategy="Broad Market",
        benchmark="FTSE Japan Index",
        distribution_policy="ACC",
        ter=0.0015,
        research_role="Japanese equities",
        research_rationale=(
            "Dedicated developed-market exposure allowing Japan to "
            "be analysed independently from broader Asia allocations."
        ),
        listings=(
            Listing("LSE", "VJPN.L", "USD", "GBP"),
        ),
    ),

    ETF(
        isin="IE00B9F5YL18",
        fund_name="Vanguard FTSE Developed Asia Pacific ex Japan UCITS ETF",
        provider="Vanguard",
        domicile="IE",
        asset_class="Equity",
        geography="Asia Pacific",
        strategy="Regional",
        benchmark="FTSE Developed Asia Pacific ex Japan Index",
        distribution_policy="ACC",
        ter=0.0015,
        research_role="Developed Asia-Pacific equities",
        research_rationale=(
            "Provides developed Asia-Pacific exposure excluding Japan "
            "for regional and macroeconomic analysis."
        ),
        listings=(
            Listing("LSE", "VAPX.L", "USD", "GBP"),
        ),
    ),

    ETF(
        isin="IE00B53HP851",
        fund_name="iShares Core FTSE 100 UCITS ETF",
        provider="iShares",
        domicile="IE",
        asset_class="Equity",
        geography="United Kingdom",
        strategy="Large Cap",
        benchmark="FTSE 100 Index",
        distribution_policy="ACC",
        ter=0.0007,
        research_role="UK large-cap equities",
        research_rationale=(
            "Provides a liquid UK large-cap benchmark and a useful "
            "GBP-denominated comparison with global equities."
        ),
        listings=(
            Listing("LSE", "CUKX.L", "GBP", "GBP"),
        ),
    ),

    ETF(
        isin="IE00BFMXYP42",
        fund_name="Vanguard FTSE 100 UCITS ETF",
        provider="Vanguard",
        domicile="IE",
        asset_class="Equity",
        geography="United Kingdom",
        strategy="Large Cap",
        benchmark="FTSE 100 Index",
        distribution_policy="ACC",
        ter=0.0009,
        research_role="UK large-cap alternative",
        research_rationale=(
            "Alternative FTSE 100 implementation useful for studying "
            "tracking differences between providers."
        ),
        listings=(
            Listing("LSE", "VUKG.L", "GBP", "GBP"),
        ),
    ),

    ETF(
        isin="IE00BFMXVQ44",
        fund_name="Vanguard FTSE 250 UCITS ETF",
        provider="Vanguard",
        domicile="IE",
        asset_class="Equity",
        geography="United Kingdom",
        strategy="Mid Cap",
        benchmark="FTSE 250 Index",
        distribution_policy="ACC",
        ter=0.0010,
        research_role="UK mid-cap equities",
        research_rationale=(
            "Provides UK mid-cap exposure distinct from the FTSE 100 "
            "for size and domestic-economy analysis."
        ),
        listings=(
            Listing("LSE", "VMID.L", "GBP", "GBP"),
        ),
    ),

    ETF(
        isin="IE00B539F030",
        fund_name="iShares MSCI UK UCITS ETF",
        provider="iShares",
        domicile="IE",
        asset_class="Equity",
        geography="United Kingdom",
        strategy="Broad Market",
        benchmark="MSCI UK Index",
        distribution_policy="ACC",
        ter=0.0033,
        research_role="UK broad-market alternative",
        research_rationale=(
            "Provides an MSCI-based UK equity benchmark for "
            "cross-index comparison against FTSE products."
        ),
        listings=(
            Listing("LSE", "CSUK.L", "GBP", "GBP"),
        ),
    ),

    ETF(
        isin="IE00B7452L46",
        fund_name="SPDR FTSE UK All Share UCITS ETF",
        provider="State Street SPDR",
        domicile="IE",
        asset_class="Equity",
        geography="United Kingdom",
        strategy="Broad Market",
        benchmark="FTSE All-Share Index",
        distribution_policy="ACC",
        ter=0.0020,
        research_role="UK broad-market core",
        research_rationale=(
            "Broad UK market exposure covering large-, mid- and "
            "smaller-cap UK equities."
        ),
        listings=(
            Listing("LSE", "SPYF.L", "GBP", "GBP"),
        ),
    ),

    ETF(
        isin="IE00BKM4GZ66",
        fund_name="iShares Core MSCI Emerging Markets IMI UCITS ETF",
        provider="iShares",
        domicile="IE",
        asset_class="Equity",
        geography="Emerging Markets",
        strategy="Broad Market",
        benchmark="MSCI Emerging Markets Investable Market Index",
        distribution_policy="ACC",
        ter=0.0018,
        research_role="Emerging-market core",
        research_rationale=(
            "Broad emerging-market exposure including large-, mid- "
            "and small-cap companies."
        ),
        listings=(
            Listing("LSE", "EMIM.L", "USD", "GBP"),
        ),
    ),

    ETF(
        isin="IE00BK5BR733",
        fund_name="Vanguard FTSE Emerging Markets UCITS ETF",
        provider="Vanguard",
        domicile="IE",
        asset_class="Equity",
        geography="Emerging Markets",
        strategy="Broad Market",
        benchmark="FTSE Emerging Markets All Cap China A Inclusion Index",
        distribution_policy="ACC",
        ter=0.0017,
        research_role="Emerging-market alternative",
        research_rationale=(
            "Alternative emerging-market methodology useful for "
            "cross-provider and cross-index analysis."
        ),
        listings=(
            Listing("LSE", "VFEG.L", "USD", "GBP"),
        ),
    ),

    # =================================================================

    # UNITED STATES EQUITIES

    # =================================================================

    ETF(
        isin="IE00B5BMR087",
        fund_name="iShares Core S&P 500 UCITS ETF",
        provider="iShares",
        domicile="IE",
        asset_class="Equity",
        geography="United States",
        strategy="Large Cap",
        benchmark="S&P 500 Index",
        distribution_policy="ACC",
        ter=0.0007,
        research_role="US large-cap core",
        research_rationale=(
            "Highly liquid representation of US large-cap equity "
            "market risk."
        ),
        listings=(
            Listing("LSE", "CSPX.L", "USD", "GBP"),
        ),
    ),

    ETF(
        isin="IE00BFMXXD54",
        fund_name="Vanguard S&P 500 UCITS ETF",
        provider="Vanguard",
        domicile="IE",
        asset_class="Equity",
        geography="United States",
        strategy="Large Cap",
        benchmark="S&P 500 Index",
        distribution_policy="ACC",
        ter=0.0007,
        research_role="US large-cap alternative",
        research_rationale=(
            "Second implementation of S&P 500 exposure useful for "
            "implementation and tracking-error analysis."
        ),
        listings=(
            Listing("LSE", "VUAG.L", "USD", "GBP"),
        ),
    ),

    ETF(
        isin="LU1135865084",
        fund_name="Amundi S&P 500 II UCITS ETF",
        provider="Amundi",
        domicile="LU",
        asset_class="Equity",
        geography="United States",
        strategy="Large Cap",
        benchmark="S&P 500 Index",
        distribution_policy="ACC",
        ter=0.0005,
        research_role="Synthetic US large-cap exposure",
        research_rationale=(
            "Low-cost synthetic implementation useful for comparing "
            "physical and synthetic index replication."
        ),
        listings=(
            Listing("LSE", "SP5L.L", "USD", "GBP"),
        ),
    ),

    ETF(
        isin="IE00B53SZB19",
        fund_name="iShares NASDAQ 100 UCITS ETF",
        provider="iShares",
        domicile="IE",
        asset_class="Equity",
        geography="United States",
        strategy="Growth",
        benchmark="NASDAQ-100 Index",
        distribution_policy="ACC",
        ter=0.0030,
        research_role="US growth equities",
        research_rationale=(
            "Concentrated large-cap growth exposure with substantial "
            "technology sensitivity."
        ),
        listings=(
            Listing("LSE", "CNDX.L", "USD", "GBP"),
        ),
    ),

    ETF(
        isin="IE00B3WJKG14",
        fund_name="iShares S&P 500 Information Technology Sector UCITS ETF",
        provider="iShares",
        domicile="IE",
        asset_class="Equity",
        geography="United States",
        strategy="Sector",
        benchmark="S&P 500 Capped 35/20 Information Technology Index",
        distribution_policy="ACC",
        ter=0.0015,
        research_role="Technology sector",
        research_rationale=(
            "Sector-specific US technology exposure for factor and "
            "sector-rotation analysis."
        ),
        listings=(
            Listing("LSE", "IUIT.L", "USD", "GBP"),
        ),
    ),

    ETF(
        isin="IE00B4K6N531",
        fund_name="iShares S&P 500 Consumer Staples Sector UCITS ETF",
        provider="iShares",
        domicile="IE",
        asset_class="Equity",
        geography="United States",
        strategy="Sector",
        benchmark="S&P 500 Capped 35/20 Consumer Staples Index",
        distribution_policy="ACC",
        ter=0.0015,
        research_role="Defensive sector",
        research_rationale=(
            "Defensive US sector exposure useful for regime and "
            "cyclical-versus-defensive analysis."
        ),
        listings=(
            Listing("LSE", "IUCS.L", "USD", "GBP"),
        ),
    ),

    ETF(
        isin="IE00B4K6J769",
        fund_name="iShares S&P 500 Financials Sector UCITS ETF",
        provider="iShares",
        domicile="IE",
        asset_class="Equity",
        geography="United States",
        strategy="Sector",
        benchmark="S&P 500 Capped 35/20 Financials Index",
        distribution_policy="ACC",
        ter=0.0015,
        research_role="Financial sector",
        research_rationale=(
            "Financial-sector exposure useful for rates, credit and "
            "cyclical sensitivity analysis."
        ),
        listings=(
            Listing("LSE", "IUFS.L", "USD", "GBP"),
        ),
    ),

    ETF(
        isin="IE00B4K6J854",
        fund_name="iShares S&P 500 Materials Sector UCITS ETF",
        provider="iShares",
        domicile="IE",
        asset_class="Equity",
        geography="United States",
        strategy="Sector",
        benchmark="S&P 500 Capped 35/20 Materials Index",
        distribution_policy="ACC",
        ter=0.0015,
        research_role="Materials sector",
        research_rationale=(
            "Materials exposure adds sensitivity to industrial activity "
            "and commodity-linked equity performance."
        ),
        listings=(
            Listing("LSE", "IUMS.L", "USD", "GBP"),
        ),
    ),

    ETF(
        isin="IE00BLNMYC90",
        fund_name="Xtrackers S&P 500 Equal Weight UCITS ETF",
        provider="Xtrackers",
        domicile="IE",
        asset_class="Equity",
        geography="United States",
        strategy="Equal Weight",
        benchmark="S&P 500 Equal Weight Index",
        distribution_policy="ACC",
        ter=0.0015,
        research_role="US equal-weight factor",
        research_rationale=(
            "Equal-weight exposure provides a useful contrast to "
            "capitalisation-weighted S&P 500 exposure."
        ),
        listings=(
            Listing("LSE", "XDWE.L", "USD", "GBP"),
        ),
    ),

    ETF(
        isin="IE00B3YCGJ38",
        fund_name="SPDR S&P US Dividend Aristocrats UCITS ETF",
        provider="State Street SPDR",
        domicile="IE",
        asset_class="Equity",
        geography="United States",
        strategy="Dividend",
        benchmark="S&P High Yield Dividend Aristocrats Index",
        distribution_policy="ACC",
        ter=0.0035,
        research_role="US dividend factor",
        research_rationale=(
            "Dividend-focused US equity exposure for defensive and "
            "quality-oriented factor analysis."
        ),
        listings=(
            Listing("LSE", "USDV.L", "USD", "GBP"),
        ),
    ),

    ETF(
        isin="IE00B8GKDB10",
        fund_name="iShares Edge MSCI USA Quality Factor UCITS ETF",
        provider="iShares",
        domicile="IE",
        asset_class="Equity",
        geography="United States",
        strategy="Quality",
        benchmark="MSCI USA Sector Neutral Quality Index",
        distribution_policy="ACC",
        ter=0.0020,
        research_role="US quality factor",
        research_rationale=(
            "Systematic quality exposure for factor-performance and "
            "risk-adjusted-return analysis."
        ),
        listings=(
            Listing("LSE", "IUQA.L", "USD", "GBP"),
        ),
    ),

    # =================================================================

    # REGIONAL / EMERGING MARKET EQUITIES

    # =================================================================

    ETF(
        isin="IE00B0M62Q58",
        fund_name="iShares MSCI Japan UCITS ETF",
        provider="iShares",
        domicile="IE",
        asset_class="Equity",
        geography="Japan",
        strategy="Broad Market",
        benchmark="MSCI Japan Index",
        distribution_policy="ACC",
        ter=0.0050,
        research_role="Japan alternative benchmark",
        research_rationale=(
            "MSCI-based Japanese equity exposure for cross-index "
            "comparison with FTSE Japan."
        ),
        listings=(
            Listing("LSE", "SJPA.L", "USD", "GBP"),
        ),
    ),

    ETF(
        isin="IE00BHZRQZ17",
        fund_name="iShares MSCI China UCITS ETF",
        provider="iShares",
        domicile="IE",
        asset_class="Equity",
        geography="China",
        strategy="Country",
        benchmark="MSCI China Index",
        distribution_policy="ACC",
        ter=0.0040,
        research_role="China equities",
        research_rationale=(
            "Dedicated China exposure provides an important source of "
            "country-specific emerging-market risk."
        ),
        listings=(
            Listing("LSE", "ICHN.L", "USD", "GBP"),
        ),
    ),

    ETF(
        isin="IE00BQT3WG13",
        fund_name="iShares MSCI China A UCITS ETF",
        provider="iShares",
        domicile="IE",
        asset_class="Equity",
        geography="China",
        strategy="Country",
        benchmark="MSCI China A Inclusion Index",
        distribution_policy="ACC",
        ter=0.0040,
        research_role="China A-shares",
        research_rationale=(
            "Domestic Chinese equity exposure distinct from offshore "
            "China benchmarks."
        ),
        listings=(
            Listing("LSE", "CNYA.L", "USD", "GBP"),
        ),
    ),

    ETF(
        isin="IE00B5L8K969",
        fund_name="iShares MSCI India UCITS ETF",
        provider="iShares",
        domicile="IE",
        asset_class="Equity",
        geography="India",
        strategy="Country",
        benchmark="MSCI India Index",
        distribution_policy="ACC",
        ter=0.0065,
        research_role="India equities",
        research_rationale=(
            "Dedicated India exposure for emerging-market country "
            "dispersion and growth analysis."
        ),
        listings=(
            Listing("LSE", "IIND.L", "USD", "GBP"),
        ),
    ),

    ETF(
        isin="IE00B3VVMM84",
        fund_name="iShares MSCI South Korea UCITS ETF",
        provider="iShares",
        domicile="IE",
        asset_class="Equity",
        geography="South Korea",
        strategy="Country",
        benchmark="MSCI Korea 20/35 Index",
        distribution_policy="ACC",
        ter=0.0074,
        research_role="South Korea equities",
        research_rationale=(
            "Developed/emerging classification-sensitive Asian market "
            "with substantial semiconductor exposure."
        ),
        listings=(
            Listing("LSE", "IKOR.L", "USD", "GBP"),
        ),
    ),

    ETF(
        isin="IE00B4L5Y983",
        fund_name="iShares Core MSCI World UCITS ETF",
        provider="iShares",
        domicile="IE",
        asset_class="Equity",
        geography="Developed Markets",
        strategy="Broad Market",
        benchmark="MSCI World Index",
        distribution_policy="ACC",
        ter=0.0020,
        research_role="Global benchmark control",
        research_rationale=(
            "Reference portfolio for measuring regional and factor "
            "relative performance."
        ),
        listings=(
            Listing("LSE", "SWDA.L", "USD", "GBP"),
        ),
    ),

    ETF(
        isin="LU1681045370",
        fund_name="Amundi MSCI Emerging Markets Swap UCITS ETF",
        provider="Amundi",
        domicile="LU",
        asset_class="Equity",
        geography="Emerging Markets",
        strategy="Broad Market",
        benchmark="MSCI Emerging Markets Index",
        distribution_policy="ACC",
        ter=0.0020,
        research_role="Synthetic EM exposure",
        research_rationale=(
            "Synthetic emerging-market implementation useful for "
            "comparing replication methodologies."
        ),
        listings=(
            Listing("LSE", "AEEM.L", "USD", "GBP"),
        ),
    ),

    # =================================================================

    # FACTOR / SMART BETA EQUITIES

    # =================================================================

    ETF(
        isin="IE00BP3QZ601",
        fund_name="iShares Edge MSCI World Quality Factor UCITS ETF",
        provider="iShares",
        domicile="IE",
        asset_class="Equity",
        geography="Global Developed Markets",
        strategy="Quality",
        benchmark="MSCI World Sector Neutral Quality Index",
        distribution_policy="ACC",
        ter=0.0030,
        research_role="Global quality factor",
        research_rationale=(
            "Systematic quality exposure for factor attribution and "
            "risk-adjusted performance analysis."
        ),
        listings=(
            Listing("LSE", "IWQU.L", "USD", "GBP"),
        ),
    ),

    ETF(
        isin="IE00BP3QZ825",
        fund_name="iShares Edge MSCI World Momentum Factor UCITS ETF",
        provider="iShares",
        domicile="IE",
        asset_class="Equity",
        geography="Global Developed Markets",
        strategy="Momentum",
        benchmark="MSCI World Momentum Index",
        distribution_policy="ACC",
        ter=0.0030,
        research_role="Global momentum factor",
        research_rationale=(
            "Momentum exposure directly supports quantitative factor "
            "analysis and rolling-performance research."
        ),
        listings=(
            Listing("LSE", "IWMO.L", "USD", "GBP"),
        ),
    ),

    ETF(
        isin="IE00B8FHGS14",
        fund_name="iShares Edge MSCI World Minimum Volatility UCITS ETF",
        provider="iShares",
        domicile="IE",
        asset_class="Equity",
        geography="Global Developed Markets",
        strategy="Minimum Volatility",
        benchmark="MSCI World Minimum Volatility Index",
        distribution_policy="ACC",
        ter=0.0030,
        research_role="Global minimum-volatility factor",
        research_rationale=(
            "Defensive factor exposure for studying the relationship "
            "between volatility and realised returns."
        ),
        listings=(
            Listing("LSE", "IWSZ.L", "USD", "GBP"),
        ),
    ),

    ETF(
        isin="IE00BP3QZB59",
        fund_name="iShares Edge MSCI World Value Factor UCITS ETF",
        provider="iShares",
        domicile="IE",
        asset_class="Equity",
        geography="Global Developed Markets",
        strategy="Value",
        benchmark="MSCI World Enhanced Value Index",
        distribution_policy="ACC",
        ter=0.0030,
        research_role="Global value factor",
        research_rationale=(
            "Systematic value exposure for factor comparison against "
            "momentum and quality strategies."
        ),
        listings=(
            Listing("LSE", "IWVL.L", "USD", "GBP"),
        ),
    ),

    ETF(
        isin="IE00BP3QZP68",
        fund_name="iShares Edge MSCI World Size Factor UCITS ETF",
        provider="iShares",
        domicile="IE",
        asset_class="Equity",
        geography="Global Developed Markets",
        strategy="Size",
        benchmark="MSCI World Size Tilt Index",
        distribution_policy="ACC",
        ter=0.0030,
        research_role="Global size factor",
        research_rationale=(
            "Size exposure provides a systematic dimension for "
            "cross-sectional factor research."
        ),
        listings=(
            Listing("LSE", "IWFS.L", "USD", "GBP"),
        ),
    ),

    ETF(
        isin="IE00BYYR0B57",
        fund_name="SPDR MSCI World Small Cap UCITS ETF",
        provider="State Street SPDR",
        domicile="IE",
        asset_class="Equity",
        geography="Global Developed Markets",
        strategy="Small Cap",
        benchmark="MSCI World Small Cap Index",
        distribution_policy="ACC",
        ter=0.0045,
        research_role="Global small-cap factor",
        research_rationale=(
            "Small-cap exposure provides a distinct size-related return "
            "and risk profile."
        ),
        listings=(
            Listing("LSE", "WDSC.L", "USD", "GBP"),
        ),
    ),

    ETF(
        isin="IE00B6YX5D40",
        fund_name="iShares Edge MSCI Europe Quality Factor UCITS ETF",
        provider="iShares",
        domicile="IE",
        asset_class="Equity",
        geography="Europe",
        strategy="Quality",
        benchmark="MSCI Europe Sector Neutral Quality Index",
        distribution_policy="ACC",
        ter=0.0030,
        research_role="European quality factor",
        research_rationale=(
            "European quality exposure allows factor behaviour to be "
            "compared across geographic markets."
        ),
        listings=(
            Listing("LSE", "IEQU.L", "EUR", "GBP"),
        ),
    ),

    # =================================================================

    # SECTOR / INDUSTRY EQUITIES

    # =================================================================

    ETF(
        isin="IE00B4K6N778",
        fund_name="iShares S&P 500 Health Care Sector UCITS ETF",
        provider="iShares",
        domicile="IE",
        asset_class="Equity",
        geography="United States",
        strategy="Healthcare",
        benchmark="S&P 500 Capped 35/20 Health Care Index",
        distribution_policy="ACC",
        ter=0.0015,
        research_role="Healthcare sector",
        research_rationale=(
            "Sector exposure useful for defensive/cyclical regime "
            "analysis."
        ),
        listings=(
            Listing("LSE", "IUHC.L", "USD", "GBP"),
        ),
    ),

    ETF(
        isin="IE00B4K6D090",
        fund_name="iShares S&P 500 Energy Sector UCITS ETF",
        provider="iShares",
        domicile="IE",
        asset_class="Equity",
        geography="United States",
        strategy="Energy",
        benchmark="S&P 500 Capped 35/20 Energy Index",
        distribution_policy="ACC",
        ter=0.0015,
        research_role="Energy sector",
        research_rationale=(
            "Equity exposure with strong commodity sensitivity for "
            "cross-asset research."
        ),
        listings=(
            Listing("LSE", "IUES.L", "USD", "GBP"),
        ),
    ),

    ETF(
        isin="IE00B4K6C369",
        fund_name="iShares S&P 500 Industrials Sector UCITS ETF",
        provider="iShares",
        domicile="IE",
        asset_class="Equity",
        geography="United States",
        strategy="Industrials",
        benchmark="S&P 500 Capped 35/20 Industrials Index",
        distribution_policy="ACC",
        ter=0.0015,
        research_role="Industrial sector",
        research_rationale=(
            "Cyclical industrial exposure useful for macro and sector "
            "rotation analysis."
        ),
        listings=(
            Listing("LSE", "IUIS.L", "USD", "GBP"),
        ),
    ),

    ETF(
        isin="IE00B4K6N604",
        fund_name="iShares S&P 500 Utilities Sector UCITS ETF",
        provider="iShares",
        domicile="IE",
        asset_class="Equity",
        geography="United States",
        strategy="Utilities",
        benchmark="S&P 500 Capped 35/20 Utilities Index",
        distribution_policy="ACC",
        ter=0.0015,
        research_role="Defensive sector",
        research_rationale=(
            "Utilities provide a defensive equity exposure with useful "
            "interest-rate sensitivity."
        ),
        listings=(
            Listing("LSE", "IUUT.L", "USD", "GBP"),
        ),
    ),

    ETF(
        isin="IE00B4K6N448",
        fund_name="iShares S&P 500 Real Estate Sector UCITS ETF",
        provider="iShares",
        domicile="IE",
        asset_class="Equity",
        geography="United States",
        strategy="Real Estate",
        benchmark="S&P 500 Capped 35/20 Real Estate Index",
        distribution_policy="ACC",
        ter=0.0015,
        research_role="US real estate sector",
        research_rationale=(
            "Provides equity real-estate exposure with distinctive "
            "interest-rate and property-cycle sensitivity."
        ),
        listings=(
            Listing("LSE", "IUSP.L", "USD", "GBP"),
        ),
    ),

    ETF(
        isin="IE00B4K6N885",
        fund_name="iShares S&P 500 Communication Services Sector UCITS ETF",
        provider="iShares",
        domicile="IE",
        asset_class="Equity",
        geography="United States",
        strategy="Communication Services",
        benchmark="S&P 500 Capped 35/20 Communication Services Index",
        distribution_policy="ACC",
        ter=0.0015,
        research_role="Communication services sector",
        research_rationale=(
            "Provides exposure to communication and media businesses "
            "with distinctive growth characteristics."
        ),
        listings=(
            Listing("LSE", "IUCM.L", "USD", "GBP"),
        ),
    ),

    ETF(
        isin="IE00B4K6N935",
        fund_name="iShares S&P 500 Consumer Discretionary Sector UCITS ETF",
        provider="iShares",
        domicile="IE",
        asset_class="Equity",
        geography="United States",
        strategy="Consumer Discretionary",
        benchmark="S&P 500 Capped 35/20 Consumer Discretionary Index",
        distribution_policy="ACC",
        ter=0.0015,
        research_role="Consumer cyclical sector",
        research_rationale=(
            "Cyclical consumer exposure for economic-cycle and sector "
            "rotation research."
        ),
        listings=(
            Listing("LSE", "IUCD.L", "USD", "GBP"),
        ),
    ),

    ETF(
        isin="IE00B4K6N976",
        fund_name="iShares S&P 500 Consumer Staples Sector UCITS ETF",
        provider="iShares",
        domicile="IE",
        asset_class="Equity",
        geography="United States",
        strategy="Consumer Staples",
        benchmark="S&P 500 Capped 35/20 Consumer Staples Index",
        distribution_policy="ACC",
        ter=0.0015,
        research_role="Consumer defensive sector",
        research_rationale=(
            "Defensive consumer exposure useful for regime comparison."
        ),
        listings=(
            Listing("LSE", "IUCS.L", "USD", "GBP"),
        ),
    ),

    ETF(
        isin="IE00B4K6N984",
        fund_name="iShares S&P 500 Technology Sector UCITS ETF",
        provider="iShares",
        domicile="IE",
        asset_class="Equity",
        geography="United States",
        strategy="Technology",
        benchmark="S&P 500 Information Technology Index",
        distribution_policy="ACC",
        ter=0.0015,
        research_role="Technology sector",
        research_rationale=(
            "Concentrated technology exposure for sector momentum and "
            "growth analysis."
        ),
        listings=(
            Listing("LSE", "IUIT.L", "USD", "GBP"),
        ),
    ),

    # =================================================================

    # FIXED INCOME

    # =================================================================

    ETF(
        isin="IE00BG47K971",
        fund_name="Vanguard Global Aggregate Bond UCITS ETF GBP Hedged",
        provider="Vanguard",
        domicile="IE",
        asset_class="Fixed Income",
        geography="Global",
        strategy="Aggregate Bonds",
        benchmark="Bloomberg Global Aggregate Float Adjusted and Scaled GBP Hedged Index",
        distribution_policy="ACC",
        ter=0.0008,
        research_role="Global bond core",
        research_rationale=(
            "Broad investment-grade global bond exposure hedged to GBP, "
            "providing a core defensive asset."
        ),
        listings=(
            Listing("LSE", "VAGS.L", "GBP", "GBP"),
        ),
    ),

    ETF(
        isin="IE00BMX0B631",
        fund_name="Vanguard USD Treasury Bond UCITS ETF EUR Hedged",
        provider="Vanguard",
        domicile="IE",
        asset_class="Fixed Income",
        geography="United States",
        strategy="Government Bonds",
        benchmark="Bloomberg Global Aggregate US Treasury Float Adjusted EUR Hedged",
        distribution_policy="ACC",
        ter=0.0008,
        research_role="US government bonds",
        research_rationale=(
            "US sovereign exposure with EUR hedging for duration and "
            "safe-haven analysis."
        ),
        listings=(
            Listing("LSE", "VDTE.L", "EUR", "GBP"),
        ),
    ),

    ETF(
        isin="IE00BGYWFS63",
        fund_name="Vanguard USD Treasury Bond UCITS ETF",
        provider="Vanguard",
        domicile="IE",
        asset_class="Fixed Income",
        geography="United States",
        strategy="Government Bonds",
        benchmark="Bloomberg Global Aggregate US Treasury Float Adjusted Index",
        distribution_policy="ACC",
        ter=0.0005,
        research_role="US Treasury core",
        research_rationale=(
            "Broad US Treasury exposure for duration, rates and "
            "flight-to-quality analysis."
        ),
        listings=(
            Listing("LSE", "VDTA.L", "USD", "GBP"),
        ),
    ),

    ETF(
        isin="IE00B3VWN518",
        fund_name="iShares USD Treasury Bond 7-10yr UCITS ETF",
        provider="iShares",
        domicile="IE",
        asset_class="Fixed Income",
        geography="United States",
        strategy="Intermediate Duration",
        benchmark="ICE US Treasury 7-10 Year Index",
        distribution_policy="ACC",
        ter=0.0007,
        research_role="Intermediate duration",
        research_rationale=(
            "Defined-duration Treasury exposure useful for analysing "
            "interest-rate sensitivity."
        ),
        listings=(
            Listing("LSE", "CBU0.L", "USD", "GBP"),
        ),
    ),

    ETF(
        isin="IE00B4WXJJ64",
        fund_name="iShares USD Treasury Bond 20+yr UCITS ETF",
        provider="iShares",
        domicile="IE",
        asset_class="Fixed Income",
        geography="United States",
        strategy="Long Duration",
        benchmark="ICE US Treasury 20+ Year Index",
        distribution_policy="ACC",
        ter=0.0010,
        research_role="Long-duration government bonds",
        research_rationale=(
            "Long-duration Treasury exposure provides a strong interest- "
            "rate sensitivity factor."
        ),
        listings=(
            Listing("LSE", "IDTG.L", "USD", "GBP"),
        ),
    ),

    ETF(
        isin="IE00B3F81R35",
        fund_name="iShares Core Global Aggregate Bond UCITS ETF",
        provider="iShares",
        domicile="IE",
        asset_class="Fixed Income",
        geography="Global",
        strategy="Aggregate Bonds",
        benchmark="Bloomberg Global Aggregate Bond Index",
        distribution_policy="ACC",
        ter=0.0004,
        research_role="Global aggregate bond benchmark",
        research_rationale=(
            "Broad global investment-grade bond exposure for comparison "
            "against GBP-hedged bond portfolios."
        ),
        listings=(
            Listing("LSE", "AGGU.L", "USD", "GBP"),
        ),
    ),

    ETF(
        isin="IE00B9M6RS56",
        fund_name="iShares Core £ Corporate Bond UCITS ETF",
        provider="iShares",
        domicile="IE",
        asset_class="Fixed Income",
        geography="United Kingdom",
        strategy="Corporate Bonds",
        benchmark="Markit iBoxx GBP Liquid Corporates Large Cap Index",
        distribution_policy="ACC",
        ter=0.0020,
        research_role="UK investment-grade credit",
        research_rationale=(
            "GBP corporate credit exposure for analysing the relationship "
            "between rates and credit spreads."
        ),
        listings=(
            Listing("LSE", "SLXX.L", "GBP", "GBP"),
        ),
    ),

    ETF(
        isin="IE00B4L60045",
        fund_name="iShares $ Corporate Bond UCITS ETF",
        provider="iShares",
        domicile="IE",
        asset_class="Fixed Income",
        geography="United States",
        strategy="Corporate Bonds",
        benchmark="Markit iBoxx USD Liquid Investment Grade Index",
        distribution_policy="ACC",
        ter=0.0020,
        research_role="US investment-grade credit",
        research_rationale=(
            "USD investment-grade corporate exposure for credit-spread "
            "and duration analysis."
        ),
        listings=(
            Listing("LSE", "LQDE.L", "USD", "GBP"),
        ),
    ),

    ETF(
        isin="IE00B7J7TB45",
        fund_name="iShares Global Corporate Bond UCITS ETF",
        provider="iShares",
        domicile="IE",
        asset_class="Fixed Income",
        geography="Global",
        strategy="Corporate Bonds",
        benchmark="Bloomberg Global Corporate Bond Index",
        distribution_policy="ACC",
        ter=0.0020,
        research_role="Global investment-grade credit",
        research_rationale=(
            "Global corporate credit exposure for comparison with "
            "government and aggregate bond portfolios."
        ),
        listings=(
            Listing("LSE", "CORP.L", "USD", "GBP"),
        ),
    ),

    ETF(
        isin="IE00B3VWN393",
        fund_name="iShares J.P. Morgan $ EM Bond UCITS ETF",
        provider="iShares",
        domicile="IE",
        asset_class="Fixed Income",
        geography="Emerging Markets",
        strategy="Emerging-Market Bonds",
        benchmark="J.P. Morgan EMBI Global Core Index",
        distribution_policy="ACC",
        ter=0.0050,
        research_role="Emerging-market sovereign credit",
        research_rationale=(
            "Emerging-market hard-currency bond exposure for analysing "
            "credit and risk-premium behaviour."
        ),
        listings=(
            Listing("LSE", "SEMB.L", "USD", "GBP"),
        ),
    ),

    ETF(
        isin="IE00B3F81Y50",
        fund_name="iShares Global High Yield Corp Bond UCITS ETF",
        provider="iShares",
        domicile="IE",
        asset_class="Fixed Income",
        geography="Global",
        strategy="High Yield",
        benchmark="Markit iBoxx Global Developed Markets Liquid High Yield Index",
        distribution_policy="ACC",
        ter=0.0050,
        research_role="Global high-yield credit",
        research_rationale=(
            "Higher-risk credit exposure useful for studying risk premia, "
            "drawdowns and equity-credit relationships."
        ),
        listings=(
            Listing("LSE", "GHYS.L", "USD", "GBP"),
        ),
    ),

    ETF(
        isin="IE00B1FZS798",
        fund_name="iShares USD Treasury Bond 1-3yr UCITS ETF",
        provider="iShares",
        domicile="IE",
        asset_class="Fixed Income",
        geography="United States",
        strategy="Short Duration",
        benchmark="ICE US Treasury 1-3 Year Index",
        distribution_policy="ACC",
        ter=0.0007,
        research_role="Cash-like fixed income",
        research_rationale=(
            "Short-duration government exposure provides a low-risk "
            "reference series."
        ),
        listings=(
            Listing("LSE", "IBTS.L", "USD", "GBP"),
        ),
    ),

    # =================================================================

    # COMMODITIES / PRECIOUS METALS

    # =================================================================

    ETF(
        isin="IE00B4ND3602",
        fund_name="WisdomTree Physical Gold",
        provider="WisdomTree",
        domicile="JE",
        asset_class="Commodity",
        geography="Global",
        strategy="Precious Metals",
        benchmark="LBMA Gold Price",
        distribution_policy="ACC",
        ter=0.0039,
        research_role="Gold",
        research_rationale=(
            "Gold provides a non-equity, non-bond diversification asset "
            "and a useful macro-risk proxy."
        ),
        listings=(
            Listing("LSE", "PHAU.L", "USD", "GBP"),
        ),
    ),

    ETF(
        isin="JE00B4T3BW64",
        fund_name="WisdomTree Physical Silver",
        provider="WisdomTree",
        domicile="JE",
        asset_class="Commodity",
        geography="Global",
        strategy="Precious Metals",
        benchmark="LBMA Silver Price",
        distribution_policy="ACC",
        ter=0.0049,
        research_role="Silver",
        research_rationale=(
            "Silver provides precious-metal exposure with greater "
            "industrial-cycle sensitivity than gold."
        ),
        listings=(
            Listing("LSE", "PHAG.L", "USD", "GBP"),
        ),
    ),

    ETF(
        isin="IE00B53H0131",
        fund_name="WisdomTree Broad Commodities UCITS ETF",
        provider="WisdomTree",
        domicile="IE",
        asset_class="Commodity",
        geography="Global",
        strategy="Broad Commodities",
        benchmark="Bloomberg Commodity Index",
        distribution_policy="ACC",
        ter=0.0049,
        research_role="Broad commodity basket",
        research_rationale=(
            "Diversified commodity exposure for cross-asset and "
            "inflation-regime analysis."
        ),
        listings=(
            Listing("LSE", "WCOA.L", "USD", "GBP"),
        ),
    ),

    ETF(
        isin="GB00B15KXQ89",
        fund_name="WisdomTree Brent Crude Oil",
        provider="WisdomTree",
        domicile="JE",
        asset_class="Commodity",
        geography="Global",
        strategy="Energy Commodity",
        benchmark="Brent Crude Oil",
        distribution_policy="ACC",
        ter=0.0049,
        research_role="Oil",
        research_rationale=(
            "Crude oil exposure provides a direct macro and inflation "
            "sensitivity proxy."
        ),
        listings=(
            Listing("LSE", "BRNT.L", "USD", "GBP"),
        ),
    ),

    ETF(
        isin="GB00B15KXH13",
        fund_name="WisdomTree Copper",
        provider="WisdomTree",
        domicile="JE",
        asset_class="Commodity",
        geography="Global",
        strategy="Industrial Commodity",
        benchmark="Copper",
        distribution_policy="ACC",
        ter=0.0049,
        research_role="Copper",
        research_rationale=(
            "Copper provides a market-sensitive commodity exposure "
            "associated with global industrial activity."
        ),
        listings=(
            Listing("LSE", "COPA.L", "USD", "GBP"),
        ),
    ),

    # =================================================================

    # REITS / ALTERNATIVES

    # =================================================================

    ETF(
        isin="IE00B1FZS350",
        fund_name="iShares Developed Markets Property Yield UCITS ETF",
        provider="iShares",
        domicile="IE",
        asset_class="Equity",
        geography="Global Developed Markets",
        strategy="REIT",
        benchmark="FTSE EPRA/NAREIT Developed Dividend+ Index",
        distribution_policy="ACC",
        ter=0.0040,
        research_role="Global listed real estate",
        research_rationale=(
            "Global property exposure provides an equity-like asset "
            "with distinct interest-rate sensitivity."
        ),
        listings=(
            Listing("LSE", "IWDP.L", "USD", "GBP"),
        ),
    ),

    ETF(
        isin="IE00B5L01S80",
        fund_name="SPDR Dow Jones Global Real Estate UCITS ETF",
        provider="State Street SPDR",
        domicile="IE",
        asset_class="Equity",
        geography="Global",
        strategy="REIT",
        benchmark="Dow Jones Global Select Real Estate Securities Index",
        distribution_policy="ACC",
        ter=0.0040,
        research_role="Global real estate alternative",
        research_rationale=(
            "Alternative global property implementation for "
            "cross-provider analysis."
        ),
        listings=(
            Listing("LSE", "GLRE.L", "USD", "GBP"),
        ),
    ),

    ETF(
        isin="IE00B1FZS467",
        fund_name="iShares Global Infrastructure UCITS ETF",
        provider="iShares",
        domicile="IE",
        asset_class="Equity",
        geography="Global",
        strategy="Infrastructure",
        benchmark="FTSE Global Core Infrastructure 50/50 Index",
        distribution_policy="ACC",
        ter=0.0065,
        research_role="Global infrastructure",
        research_rationale=(
            "Infrastructure exposure adds an economically distinct "
            "real-asset-sensitive equity allocation."
        ),
        listings=(
            Listing("LSE", "INFR.L", "USD", "GBP"),
        ),
    ),

    ETF(
        isin="IE00BF4RFH31",
        fund_name="iShares MSCI World Small Cap UCITS ETF",
        provider="iShares",
        domicile="IE",
        asset_class="Equity",
        geography="Global Developed Markets",
        strategy="Small Cap",
        benchmark="MSCI World Small Cap Index",
        distribution_policy="ACC",
        ter=0.0035,
        research_role="Global small-cap equities",
        research_rationale=(
            "Small-cap exposure adds a systematic size dimension to "
            "the research universe."
        ),
        listings=(
            Listing("LSE", "IUSN.L", "USD", "GBP"),
        ),
    ),

    ETF(
        isin="IE00B6R52036",
        fund_name="iShares Gold Producers UCITS ETF",
        provider="iShares",
        domicile="IE",
        asset_class="Equity",
        geography="Global",
        strategy="Gold Miners",
        benchmark="S&P Commodity Producers Gold Index",
        distribution_policy="ACC",
        ter=0.0055,
        research_role="Gold-mining equities",
        research_rationale=(
            "Gold miners provide an equity-linked gold exposure with "
            "operational leverage to the commodity price."
        ),
        listings=(
            Listing("LSE", "IAUP.L", "USD", "GBP"),
        ),
    ),
)


# ---------------------------------------------------------------------
# Universe helpers
# ---------------------------------------------------------------------

def get_all_etfs() -> tuple[ETF, ...]:
    """Return the complete research universe."""
    return ETF_UNIVERSE


def get_etf_by_isin(isin: str) -> ETF:
    """Return an ETF by ISIN.

    Raises:
        ValueError: If the ISIN is not in the research universe.
    """

    for etf in ETF_UNIVERSE:
        if etf.isin == isin:
            return etf

    raise ValueError(f"ETF with ISIN {isin!r} not found.")


def get_primary_listings() -> tuple[Listing, ...]:
    """Return the primary Yahoo Finance listing for every ETF."""

    return tuple(
        listing
        for etf in ETF_UNIVERSE
        for listing in etf.listings
        if listing.is_primary
    )