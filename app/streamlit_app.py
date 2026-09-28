"""
streamlit_app.py

Enhanced Interactive Streamlit dashboard for ETF fund analysis:
- Integrates with the complete ETF universe from src/finance_analytics/universe/etfs.py
- Provides rich filtering by provider, geography, asset class, strategy, etc.
- Reads prices from PostgreSQL (`finance_db`)
- Computes returns, rolling metrics, VaR/CVaR, drawdowns, regressions
- Shows holdings analysis if a holdings table exists
- Universe-wide analytics and comparisons
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta
import statsmodels.api as sm
from dotenv import load_dotenv
import os
import sys

# Import analytics module
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))
from finance_analytics.analytics import (
    simple_returns, cumulative_returns,
    rolling_volatility, max_drawdown, rolling_drawdown,
    value_at_risk, conditional_value_at_risk, sharpe_ratio, sortino_ratio,
    beta, alpha, correlation, historical_volatility
)
from finance_analytics.analytics.utils import annualize_return

# Import ETF universe
from finance_analytics.universe import get_all_etfs, ETF, Listing

# ---------------------------
# CONFIG - update if needed
# ---------------------------
# Load environment variables from .env file
load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Get ETF universe
@st.cache_data
def get_etf_universe():
    """Get the complete ETF universe with metadata."""
    return get_all_etfs()

ETF_UNIVERSE = get_etf_universe()

# Helper functions for universe processing
def get_etf_dataframe():
    """Convert ETF universe to a DataFrame for easy filtering and display."""
    etf_data = []
    for etf in ETF_UNIVERSE:
        # Get primary listing
        primary_listing = None
        for listing in etf.listings:
            if listing.is_primary:
                primary_listing = listing
                break

        # If no primary listing, use first listing
        if primary_listing is None and etf.listings:
            primary_listing = etf.listings[0]

        etf_data.append({
            'isin': etf.isin,
            'fund_name': etf.fund_name,
            'provider': etf.provider,
            'domicile': etf.domicile,
            'asset_class': etf.asset_class,
            'geography': etf.geography,
            'strategy': etf.strategy,
            'benchmark': etf.benchmark,
            'distribution_policy': etf.distribution_policy,
            'ter': etf.ter,
            'research_role': etf.research_role,
            'research_rationale': etf.research_rationale,
            'yahoo_ticker': primary_listing.yahoo_ticker if primary_listing else None,
            'exchange': primary_listing.exchange if primary_listing else None,
            'trading_currency': primary_listing.trading_currency if primary_listing else None,
            'listing_currency': primary_listing.listing_currency if primary_listing else None,
            'is_primary': primary_listing.is_primary if primary_listing else False
        })

    return pd.DataFrame(etf_data)

def get_available_tickers():
    """Get list of available Yahoo Finance tickers from the universe."""
    etf_df = get_etf_dataframe()
    # Filter out any None tickers and return unique, sorted list
    tickers = etf_df['yahoo_ticker'].dropna().unique()
    return sorted([t.strip().upper() for t in tickers if t])

# ---------------------------
# HELPERS
# ---------------------------

@st.cache_resource
def get_engine():
    return create_engine(DATABASE_URL)

@st.cache_data(ttl=300)
def load_prices(start_date=None, end_date=None, tickers=None):
    engine = get_engine()
    if tickers is None:
        tickers = get_available_tickers()

    sql = """
    SELECT date, ticker, close
    FROM prices
    WHERE ticker IN :tickers
      AND date >= :start_date
      AND date <= :end_date
    ORDER BY date ASC;
    """
    # ensure date strings
    if isinstance(start_date, (pd.Timestamp, datetime)):
        start_date = start_date.strftime("%Y-%m-%d")
    if isinstance(end_date, (pd.Timestamp, datetime)):
        end_date = end_date.strftime("%Y-%m-%d")
    with engine.connect() as conn:
        df = pd.read_sql(text(sql), conn, params={"tickers": tuple(tickers), "start_date": start_date, "end_date": end_date})
    df["date"] = pd.to_datetime(df["date"]).dt.date
    return df

@st.cache_data(ttl=300)
def table_exists(table_name):
    engine = get_engine()
    q = text("""
        SELECT EXISTS (
            SELECT 1 FROM information_schema.tables
            WHERE table_schema='public' AND table_name = :tbl
        );
    """)
    with engine.connect() as conn:
        return bool(conn.execute(q, {"tbl": table_name}).scalar())

@st.cache_data(ttl=300)
def load_holdings(table_name="holdings"):
    engine = get_engine()
    q = text(f"SELECT * FROM {table_name} ORDER BY date, ticker;")
    with engine.connect() as conn:
        return pd.read_sql(q, conn)


def detect_column(columns, possible_names):
    """Detect column name from a list of possible names (case-insensitive)."""
    return next((c for c in columns if c.lower() in possible_names), None)


# Financial calculations using the analytics module
def compute_returns(df):
    """
    Compute returns using the analytics module.
    Expects columns: date, ticker, close
    Returns: df with daily_return column, monthly returns dataframe
    """
    df = df.sort_values(["ticker", "date"]).copy()

    # Calculate simple returns for each ticker
    df["daily_return"] = df.groupby("ticker")["close"].transform(
        lambda x: simple_returns(x)
    )

    # Calculate monthly returns (period-end)
    df["month"] = pd.to_datetime(df["date"]).values.astype('datetime64[M]')
    monthly = df.groupby(["ticker", "month"])["close"].last().groupby(level=0).pct_change().reset_index(name="monthly_return")

    # Calculate cumulative return starting at 1
    df["cumulative_return"] = df.groupby("ticker")["daily_return"].transform(
        lambda x: cumulative_returns(x)
    )

    return df, monthly


def rolling_metrics(df, window_days=30):
    """
    Compute rolling metrics using the analytics module.
    df must have daily_return column
    """
    out = df.copy()

    # Calculate rolling volatility
    out["rolling_vol"] = df.groupby("ticker")["daily_return"].transform(
        lambda x: rolling_volatility(x, window=window_days)
    )

    # Calculate rolling Sharpe ratio (assume rf = 0)
    out["rolling_sharpe"] = df.groupby("ticker")["daily_return"].transform(
        lambda x: sharpe_ratio(x, risk_free_rate=0.0, periods_per_year=252)
    )

    # Note: rolling correlation is handled externally as before
    return out


def max_drawdown_from_cumulative(cumulative_series):
    """
    Calculate max drawdown from cumulative returns series using analytics module.
    """
    return max_drawdown(cumulative_series)


def rolling_drawdown_from_returns(returns_series, window_days=252):
    """
    Calculate rolling drawdown from returns series using analytics module.
    """
    return rolling_drawdown(returns_series, window=window_days)


def compute_var_cvar(returns, alpha=0.05):
    """
    Compute Value at Risk and Conditional Value at Risk using analytics module.
    """
    var = value_at_risk(returns, confidence_level=1-alpha)
    cvar = conditional_value_at_risk(returns, confidence_level=1-alpha)
    return var, cvar


def annual_volatility_from_returns(df):
    """
    Compute annualized volatility on a yearly basis using analytics module.
    Expects df with daily_return column
    """
    tmp = df.copy()
    tmp["year"] = pd.to_datetime(tmp["date"]).dt.year
    # Group by ticker and year, calculate annualized volatility for each group
    vols = tmp.groupby(["ticker", "year"])["daily_return"].apply(
        lambda x: rolling_volatility(x, window=len(x)) if len(x) > 1 else np.nan
    ).reset_index()
    vols.columns = ["ticker", "year", "rolling_vol"]
    # The rolling_vol with window=len(x) gives us the standard deviation of the period
    # To get annualized volatility, we need to multiply by sqrt(252) if these are daily returns
    vols["annual_vol"] = vols["rolling_vol"] * np.sqrt(252)
    return vols[["ticker", "year", "annual_vol"]]


# Simple regression: y ~ x (OLS) - keeping original for compatibility with summary() display
def simple_beta_alpha(y_returns, x_returns):
    """
    Perform OLS regression using statsmodels (kept for summary() compatibility).
    For beta/alpha values, use the analytics module directly.
    """
    # align indexes
    df = pd.concat([y_returns, x_returns], axis=1).dropna()
    if df.shape[0] < 10:
        return None
    X = sm.add_constant(df.iloc[:,1])
    y = df.iloc[:,0]
    model = sm.OLS(y, X).fit()
    return model

# ---------------------------
# STREAMLIT LAYOUT
# ---------------------------
st.set_page_config(layout="wide", page_title="ETF Performance & Holdings Analyzer")

st.title("ETF Performance & Holdings Analyzer")
st.markdown("Interactive dashboard for comprehensive ETF analysis using the defined research universe.")

# Sidebar controls
st.sidebar.header("Controls")
today = datetime.today().date()
default_start = today - timedelta(days=365*5)  # 5 years default
start_date = st.sidebar.date_input("Start date", default_start)
end_date = st.sidebar.date_input("End date", today)

# ETF Universe Selection Section
st.sidebar.header("ETF Universe Selection")

# Get ETF dataframe for filtering
etf_df = get_etf_dataframe()
available_tickers = get_available_tickers()

# Selection mode
selection_mode = st.sidebar.radio(
    "Selection Method",
    ["Universe Browser", "Manual Ticker Entry", "Preset Views"],
    index=0
)

selected_tickers = []

if selection_mode == "Universe Browser":
    # Filter controls
    col1, col2 = st.sidebar.columns(2)

    with col1:
        # Provider filter
        providers = ['All'] + sorted(etf_df['provider'].unique().tolist())
        selected_provider = st.selectbox("Provider", providers, index=0)

        # Geography filter
        geographies = ['All'] + sorted(etf_df['geography'].unique().tolist())
        selected_geography = st.selectbox("Geography", geographies, index=0)

        # Asset Class filter
        asset_classes = ['All'] + sorted(etf_df['asset_class'].unique().tolist())
        selected_asset_class = st.selectbox("Asset Class", asset_classes, index=0)

    with col2:
        # Strategy filter
        strategies = ['All'] + sorted(etf_df['strategy'].unique().tolist())
        selected_strategy = st.selectbox("Strategy", strategies, index=0)

        # Research Role filter
        research_roles = ['All'] + sorted(etf_df['research_role'].unique().tolist())
        selected_research_role = st.selectbox("Research Role", research_roles, index=0)

        # TER range
        ter_min, ter_max = float(etf_df['ter'].min()), float(etf_df['ter'].max())
        ter_range = st.slider(
            "TER Range (%)",
            min_value=ter_min*100,
            max_value=ter_max*100,
            value=(ter_min*100, ter_max*100),
            step=0.01
        )
        ter_range = (ter_range[0]/100, ter_range[1]/100)  # Convert back to decimal

    # Apply filters
    filtered_df = etf_df.copy()

    if selected_provider != 'All':
        filtered_df = filtered_df[filtered_df['provider'] == selected_provider]
    if selected_geography != 'All':
        filtered_df = filtered_df[filtered_df['geography'] == selected_geography]
    if selected_asset_class != 'All':
        filtered_df = filtered_df[filtered_df['asset_class'] == selected_asset_class]
    if selected_strategy != 'All':
        filtered_df = filtered_df[filtered_df['strategy'] == selected_strategy]
    if selected_research_role != 'All':
        filtered_df = filtered_df[filtered_df['research_role'] == selected_research_role]

    # TER filter
    filtered_df = filtered_df[
        (filtered_df['ter'] >= ter_range[0]) &
        (filtered_df['ter'] <= ter_range[1])
    ]

    # Remove entries without valid tickers
    filtered_df = filtered_df.dropna(subset=['yahoo_ticker'])

    # Display filtered ETFs
    st.sidebar.subheader(f"Filtered ETFs ({len(filtered_df)})")

    # Show ETFs in expandable sections by category
    if len(filtered_df) > 0:
        # Group by a meaningful category for display
        group_by = st.sidebar.selectbox(
            "Group by",
            ["Provider", "Geography", "Asset Class", "Strategy", "Research Role"],
            index=0
        )

        group_map = {
            "Provider": "provider",
            "Geography": "geography",
            "Asset Class": "asset_class",
            "Strategy": "strategy",
            "Research Role": "research_role"
        }

        group_column = group_map[group_by]

        for group_name, group_data in filtered_df.groupby(group_column):
            with st.sidebar.expander(f"{group_name} ({len(group_data)} ETFs)"):
                # Create a selection checkbox for each ETF in the group
                for _, etf in group_data.iterrows():
                    ticker = etf['yahoo_ticker'].strip().upper()
                    fund_name = etf['fund_name']
                    # Truncate long fund names for display
                    display_name = fund_name[:50] + "..." if len(fund_name) > 50 else fund_name

                    if st.checkbox(f"{ticker}: {display_name}", value=False, key=f"etf_{etf['isin']}"):
                        selected_tickers.append(ticker)
    else:
        st.sidebar.info("No ETFs match the current filters.")

elif selection_mode == "Manual Ticker Entry":
    # Manual ticker entry with universe validation
    st.sidebar.subheader("Manual Ticker Entry")
    manual_input = st.sidebar.text_input(
        "Enter tickers (comma-separated)",
        value="SPY,QQQ",
        help="Enter Yahoo Finance tickers (e.g., SPY, QQQ, VWRP.L)"
    )

    if manual_input:
        manual_tickers = [t.strip().upper() for t in manual_input.split(",") if t.strip()]
        # Validate against universe
        valid_tickers = [t for t in manual_tickers if t in available_tickers]
        invalid_tickers = [t for t in manual_tickers if t not in available_tickers]

        if valid_tickers:
            selected_tickers = valid_tickers
            st.sidebar.success(f"Valid tickers: {', '.join(valid_tickers)}")
        if invalid_tickers:
            st.sidebar.warning(f"Invalid tickers (not in universe): {', '.join(invalid_tickers)}")

    # Show universe stats
    st.sidebar.info(f"Universe contains {len(available_tickers)} ETFs")

else:  # Preset Views
    st.sidebar.subheader("Preset Views")

    preset_views = {
        "Global Equity Core": [
            "VWRP.L",   # Vanguard FTSE All-World
            "SWDA.L",   # iShares Core MSCI World
            "VHVG.L",   # Vanguard FTSE Developed World
            "EMIM.L",   # iShares Core MSCI Emerging Markets IMI
        ],
        "US Equity Focus": [
            "CSPX.L",   # iShares Core S&P 500
            "VUAG.L",   # Vanguard S&P 500
            "SP5L.L",   # Amundi S&P 500 II
            "CNDX.L",   # iShares NASDAQ 100
            "IUIT.L",   # iShares S&P 500 IT Sector
        ],
        "Factor ETFs": [
            "IUQA.L",   # iShares Edge MSCI USA Quality
            "IWQU.L",   # iShares Edge MSCI World Quality
            "IWMO.L",   # iShares Edge MSCI World Momentum
            "IWVL.L",   # iShares Edge MSCI World Value
            "IWFS.L",   # iShares Edge MSCI World Size
            "IWSZ.L",   # iShares Edge MSCI World Min Vol
        ],
        "Fixed Income": [
            "VAGS.L",   # Vanguard Global Aggregate Bond GBP Hedged
            "VDTA.L",   # Vanguard USD Treasury Bond UCITS ETF
            "AGGU.L",   # iShares Core Global Aggregate Bond
            "SLXX.L",   # iShares Core £ Corporate Bond
            "LQDE.L",   # iShares $ Corporate Bond
        ],
        "Commodities": [
            "PHAU.L",   # WisdomTree Physical Gold
            "PHAG.L",   # WisdomTree Physical Silver
            "WCOA.L",   # WisdomTree Broad Commodities
            "BRNT.L",   # WisdomTree Brent Crude Oil
            "COPA.L",   # WisdomTree Copper
        ]
    }

    selected_preset = st.sidebar.selectbox(
        "Choose a preset view",
        ["Custom"] + list(preset_views.keys()),
        index=0
    )

    if selected_preset != "Custom":
        selected_tickers = preset_views[selected_preset]
        st.sidebar.success(f"Selected {selected_preset}: {', '.join(selected_tickers)}")

        # Show details about selected ETFs
        with st.sidebar.expander("View ETF Details"):
            preset_etf_df = etf_df[etf_df['yahoo_ticker'].isin(selected_tickers)]
            for _, etf in preset_etf_df.iterrows():
                st.write(f"**{etf['yahoo_ticker']}**: {etf['fund_name']} ({etf['provider']})")
    else:
        # Allow manual selection from preset-based filtering
        st.sidebar.write("Or build custom selection:")
        # Quick add buttons for popular categories
        if st.sidebar.button("Add Global Core"):
            global_core = ["VWRP.L", "SWDA.L", "VHVG.L", "EMIM.L"]
            selected_tickers.extend([t for t in global_core if t in available_tickers and t not in selected_tickers])
        if st.sidebar.button("Add US Equity"):
            us_equity = ["CSPX.L", "VUAG.L", "CNDX.L"]
            selected_tickers.extend([t for t in us_equity if t in available_tickers and t not in selected_tickers])
        if st.sidebar.button("Add Factors"):
            factors = ["IUQA.L", "IWQU.L", "IWMO.L", "IWVL.L"]
            selected_tickers.extend([t for t in factors if t in available_tickers and t not in selected_tickers])

# Remove duplicates and ensure we have tickers
selected_tickers = list(dict.fromkeys(selected_tickers))  # Preserves order while removing duplicates

# Fallback to environment variable or defaults if no selection made
if not selected_tickers:
    # Try environment variable first
    tickers_env = os.getenv("ETF_TICKERS", "SPY,QQQ")
    env_tickers = [ticker.strip().upper() for ticker in tickers_env.split(",") if ticker.strip()]
    # Validate environment tickers against universe
    valid_env_tickers = [t for t in env_tickers if t in available_tickers]
    if valid_env_tickers:
        selected_tickers = valid_env_tickers
    else:
        # Final fallback to first few available tickers
        selected_tickers = available_tickers[:min(5, len(available_tickers))]

# For regression and correlation, allow selecting two tickers
if len(selected_tickers) >= 2:
    reg_tick1, reg_tick2 = st.sidebar.selectbox(
        "Select first ticker for regression/correlation",
        options=selected_tickers,
        index=0
    ), st.sidebar.selectbox(
        "Select second ticker for regression/correlation",
        options=selected_tickers,
        index=1 if len(selected_tickers) > 1 else 0
    )
    # Ensure we don't select the same ticker twice
    if reg_tick1 == reg_tick2 and len(selected_tickers) > 1:
        # If same ticker selected, try to pick a different one for the second
        available_others = [t for t in selected_tickers if t != reg_tick1]
        if available_others:
            reg_tick2 = available_others[0]
else:
    reg_tick1, reg_tick2 = None, None

rolling_windows = st.sidebar.multiselect("Rolling windows (days)", [30, 90, 252], default=[30, 90, 252])
var_level = st.sidebar.slider("VaR confidence (percent)", min_value=90, max_value=99, value=95, step=1)

st.sidebar.markdown("---")
st.sidebar.markdown("**Notes:** Rolling vol converted to annualised (sqrt(252)). Sharpe uses rf≈0 for demo purposes.")

# Universe Statistics
st.sidebar.header("Universe Statistics")
st.sidebar.metric("Total ETFs in Universe", len(etf_df))
st.sidebar.metric("ETFs with Data Available", len([t for t in available_tickers if t in selected_tickers]))
st.sidebar.metric("Selected ETFs", len(selected_tickers))

# Load price data
with st.spinner("Loading price data..."):
    df = load_prices(start_date, end_date, tickers=selected_tickers)

if df.empty:
    st.warning("No price data found for the selected tickers / dates.")
    st.stop()

df, monthly = compute_returns(df)

# Main Dashboard
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Overview",
    "Returns & Risk",
    "Rolling Analysis",
    "Relationships",
    "Holdings"
])

# Tab 1: Overview
with tab1:
    st.header("ETF Universe Overview")

    # Universe statistics and selected ETFs info
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Selected ETFs Details")
        if selected_tickers:
            selected_etf_df = etf_df[etf_df['yahoo_ticker'].isin(selected_tickers)]
            if not selected_etf_df.empty:
                # Display key information
                display_df = selected_etf_df[['yahoo_ticker', 'fund_name', 'provider', 'geography', 'asset_class', 'strategy', 'ter']].copy()
                display_df['ter'] = display_df['ter'].apply(lambda x: f"{x*100:.2f}%")
                display_df.columns = ['Ticker', 'Fund Name', 'Provider', 'Geography', 'Asset Class', 'Strategy', 'TER']
                st.dataframe(display_df, use_container_width=True, hide_index=True)
            else:
                st.info("No detailed information available for selected ETFs.")
        else:
            st.info("No ETFs selected.")

    with col2:
        st.subheader("Selection Summary")
        if selected_tickers:
            st.metric("Number of Selected ETFs", len(selected_tickers))

            # Show allocation by category
            if selected_tickers:
                selected_etf_df = etf_df[etf_df['yahoo_ticker'].isin(selected_tickers)]
                if not selected_etf_df.empty:
                    # Geography distribution
                    geo_dist = selected_etf_df['geography'].value_counts()
                    fig_geo = px.pie(
                        values=geo_dist.values,
                        names=geo_dist.index,
                        title="Selected ETFs by Geography"
                    )
                    st.plotly_chart(fig_geo, use_container_width=True)

                    # Asset class distribution
                    asset_dist = selected_etf_df['asset_class'].value_counts()
                    fig_asset = px.pie(
                        values=asset_dist.values,
                        names=asset_dist.index,
                        title="Selected ETFs by Asset Class"
                    )
                    st.plotly_chart(fig_asset, use_container_width=True)
        else:
            st.info("No ETFs selected.")

    st.markdown("---")

    # Cumulative returns chart
    st.subheader("Cumulative Returns")
    if len(selected_tickers) > 0:
        fig = go.Figure()
        for t in selected_tickers:
            tmp = df[df["ticker"] == t]
            if not tmp.empty:
                fig.add_trace(go.Scatter(x=tmp["date"], y=tmp["cumulative_return"], mode="lines", name=t))
        fig.update_layout(
            yaxis_title="Growth of $1",
            xaxis_title="Date",
            legend_title="Ticker",
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Select ETFs to view cumulative returns.")

# Tab 2: Returns & Risk
with tab2:
    st.header("Returns Analysis & Risk Metrics")

    if len(selected_tickers) > 0:
        # Returns distribution and VaR/CVaR
        st.subheader(f"Returns distribution and VaR/CVaR (historical, {var_level}% confidence)")

        # Calculate metrics for all selected ETFs
        returns_data = []
        for t in selected_tickers:
            returns = df[df["ticker"] == t]["daily_return"].dropna()
            if len(returns) > 0:
                var, cvar = compute_var_cvar(returns, alpha=(1 - var_level/100))
                returns_data.append({
                    'Ticker': t,
                    'Mean Daily Return': returns.mean(),
                    'Std Dev Daily': returns.std(),
                    'VaR (%)': var,
                    'CVaR (%)': cvar,
                    'Skewness': returns.skew(),
                    'Kurtosis': returns.kurtosis()
                })

        if returns_data:
            metrics_df = pd.DataFrame(returns_data)
            # Format percentages
            display_metrics = metrics_df.copy()
            for col in ['Mean Daily Return', 'Std Dev Daily', 'VaR (%)', 'CVaR (%)']:
                display_metrics[col] = display_metrics[col].apply(lambda x: f"{x*100:.2f}%")
            for col in ['Skewness', 'Kurtosis']:
                display_metrics[col] = display_metrics[col].apply(lambda x: f"{x:.2f}")

            st.dataframe(display_metrics, use_container_width=True, hide_index=True)

            # Individual ETF distributions
            cols = st.columns(min(3, len(selected_tickers)))  # Max 3 columns
            for i, t in enumerate(selected_tickers):
                with cols[i % len(cols)]:
                    returns = df[df["ticker"] == t]["daily_return"].dropna()
                    if len(returns) > 0:
                        var, cvar = compute_var_cvar(returns, alpha=(1 - var_level/100))

                        # Metrics
                        st.metric(
                            label=f"{t} VaR ({var_level}%)",
                            value=f"{var*100:.2f}%"
                        )
                        st.metric(
                            label=f"{t} CVaR ({var_level}%)",
                            value=f"{cvar*100:.2f}%"
                        )

                        # Histogram
                        fig_hist = px.histogram(
                            returns,
                            nbins=50,
                            title=f"{t} Daily Returns Distribution"
                        )
                        fig_hist.add_vline(
                            x=var,
                            line_dash="dash",
                            annotation_text=f"VaR {var_level}%: {var*100:.2f}%",
                            annotation_position="top left"
                        )
                        fig_hist.add_vline(
                            x=cvar,
                            line_dash="dot",
                            annotation_text=f"CVaR {var_level}%: {cvar*100:.2f}%",
                            annotation_position="top right"
                        )
                        st.plotly_chart(fig_hist, use_container_width=True)
        else:
            st.info("Insufficient data for returns analysis.")
    else:
        st.info("Select ETFs to view returns and risk metrics.")

    st.markdown("---")

    # Yearly volatility and drawdowns
    st.subheader("Yearly Volatility and Max Drawdown")
    if len(selected_tickers) > 0:
        av = annual_volatility_from_returns(df)
        if not av.empty:
            st.dataframe(
                av.sort_values(["ticker","year"], ascending=[True, False]).reset_index(drop=True),
                use_container_width=True,
                hide_index=True
            )

            # Compute max drawdowns per year
            df_temp = df.copy()
            df_temp["cum_return_index"] = df_temp.groupby("ticker")["cumulative_return"].apply(lambda x: x)
            df_temp["year"] = pd.to_datetime(df_temp["date"]).dt.year
            mdd_rows = []
            for (t, yr), group in df_temp.groupby(["ticker","year"]):
                series = group.set_index("date")["cum_return_index"]
                peak = series.cummax()
                dd = (series/peak - 1)
                mdd = dd.min()
                mdd_rows.append({"ticker": t, "year": yr, "max_drawdown": mdd})
            mdd_df = pd.DataFrame(mdd_rows)

            if not mdd_df.empty:
                st.subheader("Maximum Drawdown by Year")
                st.dataframe(
                    mdd_df.sort_values(["ticker","year"], ascending=[True, False]).reset_index(drop=True),
                    use_container_width=True,
                    hide_index=True
                )
        else:
            st.info("Insufficient data for yearly analysis.")
    else:
        st.info("Select ETFs to view yearly analysis.")

# Tab 3: Rolling Analysis
with tab3:
    st.header("Rolling Analysis")

    if len(selected_tickers) > 0 and len(rolling_windows) > 0:
        for win in rolling_windows:
            st.markdown(f"**Rolling Metrics ({win}-day window)**")

            # Calculate rolling metrics
            r = rolling_metrics(df, window_days=win)

            # Volatility chart
            fig_vol = go.Figure()
            for t in selected_tickers:
                tmp = r[r["ticker"] == t]
                if not tmp.empty:
                    fig_vol.add_trace(go.Scatter(
                        x=tmp["date"],
                        y=tmp["rolling_vol"],
                        name=f"{t} Vol ({win}d)",
                        mode='lines'
                    ))
            fig_vol.update_layout(
                yaxis_title="Annualised Volatility",
                xaxis_title="Date",
                legend_title="Ticker",
                hovermode='x unified'
            )
            st.plotly_chart(fig_vol, use_container_width=True)

            # Sharpe ratio chart
            fig_sharpe = go.Figure()
            for t in selected_tickers:
                tmp = r[r["ticker"] == t]
                if not tmp.empty:
                    fig_sharpe.add_trace(go.Scatter(
                        x=tmp["date"],
                        y=tmp["rolling_sharpe"],
                        name=f"{t} Sharpe ({win}d)",
                        mode='lines'
                    ))
            fig_sharpe.update_layout(
                yaxis_title="Rolling Sharpe (rf≈0)",
                xaxis_title="Date",
                legend_title="Ticker",
                hovermode='x unified'
            )
            st.plotly_chart(fig_sharpe, use_container_width=True)

            # Rolling drawdown (if window >= 60 days)
            if win >= 60:
                st.markdown(f"**Rolling Drawdown ({win}-day window)**")
                fig_dd = go.Figure()
                for t in selected_tickers:
                    returns = df[df["ticker"] == t]["daily_return"].dropna()
                    if len(returns) > win:
                        rolling_dd = rolling_drawdown_from_returns(returns, window_days=win)
                        # Create a temporary dataframe for plotting
                        dd_dates = df[df["ticker"] == t]["date"].iloc[win-1:][:len(rolling_dd)]
                        if len(dd_dates) == len(rolling_dd):
                            fig_dd.add_trace(go.Scatter(
                                x=dd_dates,
                                y=rolling_dd,
                                name=f"{t} DD ({win}d)",
                                mode='lines'
                            ))
                if fig_dd.data:  # Only show if we have data
                    fig_dd.update_layout(
                        yaxis_title="Rolling Drawdown",
                        xaxis_title="Date",
                        legend_title="Ticker",
                        hovermode='x unified'
                    )
                    st.plotly_chart(fig_dd, use_container_width=True)
                else:
                    st.info(f"Insufficient data for {win}-day rolling drawdown calculation.")

            st.markdown("---")
    else:
        st.info("Select ETFs and rolling windows to view rolling analysis.")

# Tab 4: Relationships
with tab4:
    st.header("ETF Relationships Analysis")

    if len(selected_tickers) >= 2 and reg_tick1 is not None and reg_tick2 is not None:
        st.subheader(f"Rolling Correlation between {reg_tick1} and {reg_tick2}")
        pivot = df.pivot(index="date", columns="ticker", values="daily_return").dropna()

        # Check if both selected tickers have data
        if reg_tick1 in pivot.columns and reg_tick2 in pivot.columns:
            for win in rolling_windows:
                # Compute rolling correlation directly
                rolling_corr = pivot[reg_tick1].rolling(win).corr(pivot[reg_tick2])
                # Remove NaN values for cleaner display
                rolling_corr_clean = rolling_corr.dropna()

                if len(rolling_corr_clean) > 0:
                    fig = go.Figure(data=go.Scatter(
                        x=rolling_corr_clean.index,
                        y=rolling_corr_clean.values,
                        name=f"{reg_tick1}-{reg_tick2} corr {win}d",
                        mode='lines'
                    ))
                    fig.update_layout(
                        yaxis_title="Correlation",
                        xaxis_title="Date",
                        hovermode='x unified'
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    # Show correlation statistics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Average Correlation", f"{rolling_corr_clean.mean():.3f}")
                    with col2:
                        st.metric("Correlation Std Dev", f"{rolling_corr_clean.std():.3f}")
                    with col3:
                        st.metric("Min/Max Correlation", f"{rolling_corr_clean.min():.3f} / {rolling_corr_clean.max():.3f}")
                else:
                    st.warning(f"Insufficient overlapping data for {win}-day rolling correlation.")
        else:
            st.warning(f"Insufficient data for {reg_tick1} and/or {reg_tick2}. Please check if data is available for these tickers.")
    else:
        st.info("Select at least two tickers to view rolling correlation.")

    st.markdown("---")

    # Correlation matrix
    st.subheader("Correlation Matrix (Full Period)")
    if len(selected_tickers) >= 2:
        pivot = df.pivot(index="date", columns="ticker", values="daily_return").dropna()
        # Ensure we only use tickers that have data
        available_in_data = [t for t in selected_tickers if t in pivot.columns]
        if len(available_in_data) >= 2:
            corr_matrix = pivot[available_in_data].corr()

            fig_corr = px.imshow(
                corr_matrix,
                text_auto=True,
                aspect="auto",
                title="ETF Correlation Matrix",
                color_continuous_scale="RdBu_r",
                zmin=-1, zmax=1
            )
            st.plotly_chart(fig_corr, use_container_width=True)
        else:
            st.info("Insufficient data with overlapping dates for correlation matrix.")
    else:
        st.info("Select at least two tickers to view correlation matrix.")

    st.markdown("---")

    # Regression analysis
    st.subheader("Simple Linear Regressions (Beta & Alpha)")
    if len(selected_tickers) >= 2 and reg_tick1 is not None and reg_tick2 is not None:
        # align returns by date
        ret_pivot = df.pivot(index="date", columns="ticker", values="daily_return").dropna()

        # Check if both selected tickers have data
        if reg_tick1 in ret_pivot.columns and reg_tick2 in ret_pivot.columns:
            # regression: reg_tick2 ~ reg_tick1 (so beta of reg_tick2 vs reg_tick1)
            model_2_on_1 = simple_beta_alpha(ret_pivot[reg_tick2], ret_pivot[reg_tick1])
            model_1_on_2 = simple_beta_alpha(ret_pivot[reg_tick1], ret_pivot[reg_tick2])

            if model_2_on_1 is not None:
                st.markdown(f"**Regression: {reg_tick2} ~ {reg_tick1}**")
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.write(model_2_on_1.summary())
                with col2:
                    # Extract key metrics
                    alpha_2_on_1 = model_2_on_1.params.iloc[0] if len(model_2_on_1.params) > 0 else None
                    beta_2_on_1 = model_2_on_1.params.iloc[1] if len(model_2_on_1.params) > 1 else None
                    r_squared = model_2_on_1.rsquared if hasattr(model_2_on_1, 'rsquared') else None

                    if alpha_2_on_1 is not None:
                        st.metric("Alpha (Intercept)", f"{alpha_2_on_1*252*100:.2f}% annualized")
                    if beta_2_on_1 is not None:
                        st.metric("Beta (Slope)", f"{beta_2_on_1:.3f}")
                    if r_squared is not None:
                        st.metric("R-Squared", f"{r_squared:.3f}")

                # Scatter plot with regression line
                df_sc = ret_pivot.reset_index()
                fig = px.scatter(
                    x=df_sc[reg_tick1],
                    y=df_sc[reg_tick2],
                    labels={"x": f"{reg_tick1} daily return", "y": f"{reg_tick2} daily return"},
                    title=f"{reg_tick2} vs {reg_tick1} Daily Returns"
                )
                # add regression line
                if model_2_on_1 is not None and len(model_2_on_1.params) >= 2:
                    params = model_2_on_1.params
                    xs = np.linspace(df_sc[reg_tick1].min(), df_sc[reg_tick1].max(), 100)
                    ys = params[0] + params[1] * xs
                    fig.add_traces(go.Scatter(x=xs, y=ys, mode="lines", name="OLS fit", line=dict(width=2)))
                st.plotly_chart(fig, use_container_width=True)

            if model_1_on_2 is not None:
                st.markdown(f"**Regression: {reg_tick1} ~ {reg_tick2}**")
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.write(model_1_on_2.summary())
                with col2:
                    # Extract key metrics
                    alpha_1_on_2 = model_1_on_2.params.iloc[0] if len(model_1_on_2.params) > 0 else None
                    beta_1_on_2 = model_1_on_2.params.iloc[1] if len(model_1_on_2.params) > 1 else None
                    r_squared = model_1_on_2.rsquared if hasattr(model_1_on_2, 'rsquared') else None

                    if alpha_1_on_2 is not None:
                        st.metric("Alpha (Intercept)", f"{alpha_1_on_2*252*100:.2f}% annualized")
                    if beta_1_on_2 is not None:
                        st.metric("Beta (Slope)", f"{beta_1_on_2:.3f}")
                    if r_squared is not None:
                        st.metric("R-Squared", f"{r_squared:.3f}")
        else:
            st.warning(f"Insufficient data for {reg_tick1} and/or {reg_tick2}. Please check if data is available for these tickers.")
    else:
        st.info("Select at least two tickers to run the simple regressions.")

# Tab 5: Holdings
with tab5:
    st.header("Holdings Analysis")

    holdings_table_names = ["holdings", "etf_holdings", "fund_holdings"]
    found = None
    for tbl in holdings_table_names:
        if table_exists(tbl):
            found = tbl
            break

    if found:
        st.success(f"Found holdings table: {found}. Running holdings analysis...")
        holdings = load_holdings(found)
        st.write("Sample holdings rows:")
        st.dataframe(holdings.head())

        # expected columns (best effort)
        # try to infer common columns: date, fund_ticker or ticker, holding_ticker (symbol), weight, sector
        date_col = detect_column(holdings.columns, ("date", "as_of", "snapshot_date"))
        fund_col = detect_column(holdings.columns, ("fund", "ticker", "etf"))
        holding_col = detect_column(holdings.columns, ("holding_ticker", "holding", "symbol", "secid"))
        weight_col = detect_column(holdings.columns, ("weight", "weight_pct", "weight_percent", "pct"))
        sector_col = detect_column(holdings.columns, ("sector", "industry"))

        st.write("Detected columns:", {"date_col": date_col, "fund_col": fund_col, "holding_col": holding_col, "weight_col": weight_col, "sector_col": sector_col})

        # Filter holdings to only show selected ETFs if applicable
        if fund_col and selected_tickers:
            # Check if any of the selected ETFs are in the holdings data
            holdings_funds = holdings[fund_col].dropna().unique() if fund_col in holdings.columns else []
            matching_holdings = [t for t in selected_tickers if t in holdings_funds]
            if matching_holdings:
                st.info(f"Showing holdings for: {', '.join(matching_holdings)}")
                # Filter holdings data
                holdings = holdings[holdings[fund_col].isin(matching_holdings)]
            elif len(holdings_funds) > 0:
                st.info(f"Selected ETFs not found in holdings data. Available funds in holdings: {', '.join(holdings_funds[:10])}{'...' if len(holdings_funds) > 10 else ''}")
            else:
                st.warning("No fund ticker column detected or no holdings data available.")

        # example: latest holdings snapshot
        if date_col:
            latest_date = holdings[date_col].max()
            latest = holdings[holdings[date_col] == latest_date]
        else:
            latest = holdings.copy()

        # Top holdings by weight
        if holding_col and weight_col:
            top10 = latest.groupby(holding_col)[weight_col].sum().sort_values(ascending=False).head(10).reset_index()
            st.markdown("**Top 10 Holdings (by weight)**")
            st.dataframe(top10)

            # concentration of top 10
            top10_sum = top10[weight_col].sum()
            st.metric("Top 10 Concentration (weight sum)", f"{top10_sum:.2%}")

        # sector breakdown
        if sector_col and weight_col:
            sector = latest.groupby(sector_col)[weight_col].sum().sort_values(ascending=False).reset_index()
            fig = px.bar(sector, x=sector_col, y=weight_col, title="Sector Weight Breakdown")
            st.plotly_chart(fig, use_container_width=True)

            # Show sector concentration
            top5_sectors = sector.head(5)
            st.subheader("Top 5 Sectors by Weight")
            st.dataframe(top5_sectors, use_container_width=True, hide_index=True)
        else:
            st.info("Sector or weight column not detected for breakdown analysis.")

        # Holding count over time
        if date_col and holding_col:
            st.subheader("Number of Unique Holdings Over Time")
            holdings_date_col = holdings[date_col].dropna()
            if len(holdings_date_col) > 0:
                holdings_over_time = holdings.groupby(date_col)[holding_col].nunique().reset_index()
                holdings_over_time.columns = ['Date', 'Unique Holdings']

                fig_holdings = px.line(
                    holdings_over_time,
                    x='Date',
                    y='Unique Holdings',
                    title="Number of Unique Holdings Over Time"
                )
                st.plotly_chart(fig_holdings, use_container_width=True)
    else:
        st.info("No holdings table found in the database. If you'd like holdings analysis, add a `holdings` or `etf_holdings` table with columns (date, ticker, holding_ticker, weight, sector) and refresh.")

# Footer
st.markdown("---")
st.markdown("""
**How this helps you:** This Streamlit dashboard demonstrates end-to-end analytics:
- **Universe Integration**: Leverages the complete ETF research universe with rich metadata
- **Smart Filtering**: Filter ETFs by provider, geography, asset class, strategy, and more
- **Comprehensive Analysis**: Returns, risk metrics (VaR/CVaR), rolling analytics, correlations, and regressions
- **Professional Presentation**: Publication-ready visualizations and formatted metrics
- **Holdings Analysis**: When available, examine portfolio composition and concentration

*Use this app during interviews or deploy it to show an interactive demo of quantitative finance skills.*
""")