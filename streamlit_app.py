"""
streamlit_app.py

Interactive Streamlit dashboard for ETF fund analysis:
- Reads prices from PostgreSQL (`finance_db`)
- Computes returns, rolling metrics, VaR/CVaR, drawdowns, regressions
- Shows holdings analysis if a holdings table exists
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

TICKERS = ["SPY", "QQQ"]

# ---------------------------
# HELPERS
# ---------------------------

@st.cache_resource
def get_engine():
    return create_engine(DATABASE_URL)

@st.cache_data(ttl=300)
def load_prices(start_date=None, end_date=None, tickers=TICKERS):
    engine = get_engine()
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

# Financial calculations
def compute_returns(df):
    # expects columns: date, ticker, close
    df = df.sort_values(["ticker", "date"]).copy()
    df["daily_return"] = df.groupby("ticker")["close"].pct_change()
    # monthly returns (period-end)
    df["month"] = pd.to_datetime(df["date"]).values.astype('datetime64[M]')
    monthly = df.groupby(["ticker", "month"])["close"].last().groupby(level=0).pct_change().reset_index(name="monthly_return")
    # cumulative return starting at 1
    df["cumulative_return"] = df.groupby("ticker")["daily_return"].transform(lambda x: (1 + x).cumprod().fillna(1))
    return df, monthly

def rolling_metrics(df, window_days=30):
    # df must have daily_return
    out = df.copy()
    out["rolling_vol"] = out.groupby("ticker")["daily_return"].rolling(window_days, min_periods=5).std().reset_index(0,drop=True) * np.sqrt(252)
    # rolling Sharpe (assume rf = 0)
    out["rolling_sharpe"] = out.groupby("ticker")["daily_return"].rolling(window_days, min_periods=5).apply(lambda x: (x.mean() / x.std() * np.sqrt(252)) if x.std() != 0 else np.nan).reset_index(0,drop=True)
    # rolling correlation between tickers — produce pivoted series externally
    return out

def max_drawdown(series):
    # series is cumulative return or price
    cummax = series.cummax()
    drawdown = series / cummax - 1
    return drawdown.min()

def rolling_drawdown(df, window_days=252):
    out = df.copy()
    # compute rolling max drawdown on cumulative returns
    def rd(x):
        s = (1 + x).cumprod()
        return (s / s.cummax() - 1).min()
    out["rolling_dd"] = out.groupby("ticker")["daily_return"].rolling(window_days, min_periods=5).apply(lambda x: (1 + x).cumprod().div((1 + x).cumprod().cummax()).min()).reset_index(0,drop=True)
    return out

def compute_var_cvar(returns, alpha=0.05):
    # historical VaR and CVaR
    var = np.percentile(returns.dropna(), alpha*100)
    cvar = returns[returns <= var].mean()
    return var, cvar

def annual_volatility(df):
    # returns daily_return; compute year-by-year vol
    tmp = df.copy()
    tmp["year"] = pd.to_datetime(tmp["date"]).dt.year
    vols = tmp.groupby(["ticker", "year"])["daily_return"].std().reset_index()
    vols["annual_vol"] = vols["daily_return"] * np.sqrt(252)
    return vols[["ticker","year","annual_vol"]]

# Simple regression: y ~ x (OLS)
def simple_beta_alpha(y_returns, x_returns):
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
st.markdown("Interactive dashboard: SPY vs QQQ — returns, risk metrics, regressions, VaR/CVaR, holdings (if available).")

# Sidebar controls
st.sidebar.header("Controls")
today = datetime.today().date()
default_start = today - timedelta(days=365*5)  # 5 years default
start_date = st.sidebar.date_input("Start date", default_start)
end_date = st.sidebar.date_input("End date", today)
selected_tickers = st.sidebar.multiselect("Tickers", TICKERS, default=TICKERS)
rolling_windows = st.sidebar.multiselect("Rolling windows (days)", [30, 90, 252], default=[30, 90, 252])
var_level = st.sidebar.slider("VaR confidence (percent)", min_value=90, max_value=99, value=95, step=1)

st.sidebar.markdown("---")
st.sidebar.markdown("**Notes:** Rolling vol converted to annualised (sqrt(252)). Sharpe uses rf≈0 for demo purposes.")

# Load price data
with st.spinner("Loading price data..."):
    df = load_prices(start_date, end_date, tickers=selected_tickers)

if df.empty:
    st.warning("No price data found for the selected tickers / dates.")
    st.stop()

df, monthly = compute_returns(df)

# Top row: cumulative returns chart
st.subheader("Cumulative Returns")
fig = go.Figure()
for t in selected_tickers:
    tmp = df[df["ticker"] == t]
    fig.add_trace(go.Scatter(x=tmp["date"], y=tmp["cumulative_return"], mode="lines", name=t))
fig.update_layout(yaxis_title="Growth of $1", xaxis_title="Date", legend_title="Ticker")
st.plotly_chart(fig, use_container_width=True)

# Daily returns distribution & VaR/CVaR
st.subheader(f"Returns distribution and VaR/CVaR (historical, {var_level}% confidence)")
cols = st.columns(len(selected_tickers))
for i, t in enumerate(selected_tickers):
    with cols[i]:
        returns = df[df["ticker"] == t]["daily_return"].dropna()
        var, cvar = compute_var_cvar(returns, alpha=(1 - var_level/100))
        st.metric(label=f"{t} VaR ({var_level}%)", value=f"{var:.4%}", delta=None)
        st.metric(label=f"{t} CVaR ({var_level}%)", value=f"{cvar:.4%}", delta=None)
        fig_hist = px.histogram(returns, nbins=60, title=f"{t} daily returns")
        fig_hist.add_vline(x=var, line_dash="dash", annotation_text=f"VaR {var_level}%: {var:.2%}", annotation_position="top left")
        st.plotly_chart(fig_hist, use_container_width=True)

# Rolling metrics (vol & Sharpe)
st.subheader("Rolling Metrics (volatility, Sharpe ratio)")
for win in rolling_windows:
    st.markdown(f"**Window: {win} days**")
    r = rolling_metrics(df, window_days=win)
    fig = go.Figure()
    for t in selected_tickers:
        tmp = r[r["ticker"] == t]
        fig.add_trace(go.Scatter(x=tmp["date"], y=tmp["rolling_vol"], name=f"{t} vol ({win}d)"))
    fig.update_layout(yaxis_title="Annualised Volatility", xaxis_title="Date")
    st.plotly_chart(fig, use_container_width=True)

    fig2 = go.Figure()
    for t in selected_tickers:
        tmp = r[r["ticker"] == t]
        fig2.add_trace(go.Scatter(x=tmp["date"], y=tmp["rolling_sharpe"], name=f"{t} Sharpe ({win}d)"))
    fig2.update_layout(yaxis_title="Rolling Sharpe (rf≈0)", xaxis_title="Date")
    st.plotly_chart(fig2, use_container_width=True)

# Rolling correlation between tickers (if >1 ticker selected)
if len(selected_tickers) > 1:
    st.subheader("Rolling Correlation between selected tickers")
    pivot = df.pivot(index="date", columns="ticker", values="daily_return").dropna()
    for win in rolling_windows:
        corr = pivot[selected_tickers].rolling(win).corr().unstack().iloc[:, :, :]
        # We extract correlation between the two tickers
        t0, t1 = selected_tickers[0], selected_tickers[1]
        series = pivot[selected_tickers].rolling(win).corr().dropna()
        # simpler: compute rolling corr directly
        rolling_corr = pivot[selected_tickers[0]].rolling(win).corr(pivot[selected_tickers[1]])
        fig = go.Figure(data=go.Scatter(x=rolling_corr.index, y=rolling_corr.values, name=f"{t0}-{t1} corr {win}d"))
        fig.update_layout(yaxis_title="Correlation", xaxis_title="Date")
        st.plotly_chart(fig, use_container_width=True)

# Yearly volatility & max drawdowns
st.subheader("Yearly volatility and max drawdown")
av = annual_volatility(df)
st.dataframe(av.sort_values(["ticker","year"], ascending=[True, False]).reset_index(drop=True))

# Compute max drawdowns per year
df["cum_return_index"] = df.groupby("ticker")["cumulative_return"].apply(lambda x: x)  # already done
df["year"] = pd.to_datetime(df["date"]).dt.year
mdd_rows = []
for (t, yr), group in df.groupby(["ticker","year"]):
    # for each year compute peak-to-trough
    series = group.set_index("date")["cum_return_index"]
    peak = series.cummax()
    dd = (series/peak - 1)
    mdd = dd.min()
    mdd_rows.append({"ticker": t, "year": yr, "max_drawdown": mdd})
mdd_df = pd.DataFrame(mdd_rows)
st.dataframe(mdd_df.sort_values(["ticker","year"], ascending=[True, False]).reset_index(drop=True))

# Regression: each ETF on the other
st.subheader("Simple linear regressions between ETFs (beta & alpha)")
if len(selected_tickers) > 1:
    t0, t1 = selected_tickers[0], selected_tickers[1]
    # align returns by date
    ret_pivot = df.pivot(index="date", columns="ticker", values="daily_return").dropna()
    # regression: t1 ~ t0 (so beta of t1 vs t0)
    model_1_on_0 = simple_beta_alpha(ret_pivot[t1], ret_pivot[t0])
    model_0_on_1 = simple_beta_alpha(ret_pivot[t0], ret_pivot[t1])
    if model_1_on_0 is not None:
        st.markdown(f"**Regression: {t1} ~ {t0}**")
        st.write(model_1_on_0.summary())
        # scatter + fit
        df_sc = ret_pivot.reset_index()
        fig = px.scatter(x=df_sc[t0], y=df_sc[t1], labels={"x": f"{t0} daily return", "y": f"{t1} daily return"}, title=f"{t1} vs {t0} daily returns")
        # add regression line
        params = model_1_on_0.params
        xs = np.linspace(df_sc[t0].min(), df_sc[t0].max(), 100)
        ys = params[0] + params[1] * xs
        fig.add_traces(go.Scatter(x=xs, y=ys, mode="lines", name="OLS fit"))
        st.plotly_chart(fig, use_container_width=True)
    if model_0_on_1 is not None:
        st.markdown(f"**Regression: {t0} ~ {t1}**")
        st.write(model_0_on_1.summary())
else:
    st.info("Select two tickers to run the simple regressions.")

# Holdings analysis (conditional)
st.subheader("Holdings analysis (if holdings table found)")
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
    cols = [c.lower() for c in holdings.columns]
    # standardize names
    date_col = next((c for c in holdings.columns if c.lower() in ("date", "as_of", "snapshot_date")), None)
    fund_col = next((c for c in holdings.columns if c.lower() in ("fund", "ticker", "etf")), None)
    holding_col = next((c for c in holdings.columns if c.lower() in ("holding_ticker", "holding", "symbol", "secid")), None)
    weight_col = next((c for c in holdings.columns if c.lower() in ("weight", "weight_pct", "weight_percent", "pct")), None)
    sector_col = next((c for c in holdings.columns if c.lower() in ("sector", "industry")), None)

    st.write("Detected columns:", {"date_col": date_col, "fund_col": fund_col, "holding_col": holding_col, "weight_col": weight_col, "sector_col": sector_col})

    # example: latest holdings snapshot
    if date_col:
        latest_date = holdings[date_col].max()
        latest = holdings[holdings[date_col] == latest_date]
    else:
        latest = holdings.copy()

    # Top holdings by weight
    if holding_col and weight_col:
        top10 = latest.groupby(holding_col)[weight_col].sum().sort_values(ascending=False).head(10).reset_index()
        st.markdown("**Top 10 holdings (by weight)**")
        st.dataframe(top10)

        # concentration of top 10
        top10_sum = top10[weight_col].sum()
        st.metric("Top 10 concentration (weight sum)", f"{top10_sum:.2%}")

    # sector breakdown
    if sector_col and weight_col:
        sector = latest.groupby(sector_col)[weight_col].sum().sort_values(ascending=False).reset_index()
        fig = px.bar(sector, x=sector_col, y=weight_col, title="Sector weight breakdown")
        st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No holdings table found in the database. If you'd like holdings analysis, add a `holdings` or `etf_holdings` table with columns (date, ticker, holding_ticker, weight, sector) and refresh.")

# Footer / guidance
st.markdown("---")
st.markdown("**How this helps you:** this Streamlit dashboard demonstrates end-to-end analytics: data extraction from PostgreSQL, time-series analysis (returns, volatility, drawdown), risk measures (VaR/CVaR), simple factor regressions, and holdings-level inspection. Use this app during interviews or deploy it to show an interactive demo.")