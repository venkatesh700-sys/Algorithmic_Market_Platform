import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import os

st.set_page_config(page_title="AI Agent Metrics Workspace", page_icon="⚡", layout="wide")
st.title("⚡ Quantitative AI Engine Performance & Paper Portfolio Dashboard")
st.markdown("Automated metrics auditing tracking Indian Stock Market strategies.")

DB_FILE = "quant_trading_desk.db"

if not os.path.exists(DB_FILE):
    st.warning("⚠️ Database registry unpopulated. Run `python main_agent.py` to seed execution data records.")
else:
    conn = sqlite3.connect(DB_FILE)
    df_ledger = pd.read_sql_query("SELECT * FROM trade_ledger", conn)
    df_portfolio = pd.read_sql_query("SELECT * FROM portfolio", conn)
    conn.close()
    
    if df_ledger.empty:
        st.info("No active trades recorded. Waiting for upcoming market open trigger events.")
    else:
        # Calculate system performance analytics indicators
        total_trades = len(df_ledger)
        wins = len(df_ledger[df_ledger['status'] == 'WIN'])
        win_rate = (wins / total_trades) * 100 if total_trades > 0 else 0.0
        
        gross_profit = df_ledger[df_ledger['pnl'] > 0]['pnl'].sum()
        gross_loss = abs(df_ledger[df_ledger['pnl'] < 0]['pnl'].sum())
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else gross_profit
        
        # Calculate Sharpe Profile and returns stability metrics
        net_returns_vector = df_ledger['pnl'].values
        sharpe_ratio = (net_returns_vector.mean() / net_returns_vector.std() * (252**0.5)) if net_returns_vector.std() > 0 else 0.0
        
        df_ledger['Cumulative_PnL'] = df_ledger['pnl'].cumsum()
        df_ledger['Wallet_Equity'] = 40000.0 + df_ledger['Cumulative_PnL']
        ending_balance = df_ledger['Wallet_Equity'].iloc[-1]
        
        # --- SCREEN TOP EXECUTIVE METRICS SCOREBOARD ---
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Simulated Account Balance", f"₹{ending_balance:,.2f}", f"₹{df_ledger['Cumulative_PnL'].iloc[-1]:+,.2f}")
        col2.metric("System Win Rate Metric", f"{win_rate:.2f}%", "Target: >=85%", delta_color="normal" if win_rate >= 85 else "inverse")
        col3.metric("Audited Profit Factor Score", f"{profit_factor:.2f}", "Target: >=2.0", delta_color="normal" if profit_factor >= 2.0 else "inverse")
        col4.metric("Risk-Adjusted Sharpe Ratio", f"{sharpe_ratio:.2f}", "Institutional Grade Platform")
        
        st.markdown("---")
        
        # --- DATA VISUALIZATION AREA CHARTS ---
        chart_col, data_col = st.columns([2, 1])
        
        with chart_col:
            st.subheader("📈 Real-Time Platform Equity Compounding Curve")
            fig = px.line(df_ledger, x=df_ledger.index, y="Wallet_Equity", markers=True,
                          labels={"index": "Chronological Trades Array Order", "Wallet_Equity": "Simulated Portfolio Equity (INR)"},
                          color_discrete_sequence=["#FF007F"])
            fig.update_layout(template="plotly_dark", hovermode="x unified")
            st.plotly_chart(fig, use_container_width=True)
            
        with data_col:
            st.subheader("📊 Sector Selection Distribution Density")
            # Create a mock helper sector column array mapping for visual clarity
            df_ledger['Sector'] = ['Banking' if 'BANK' in t or 'SBIN' in t else 'Technology' if 'TCS' in t or 'INFY' in t else 'Energy' for t in df_ledger['ticker']]
            fig_pie = px.pie(df_ledger, names='Sector', values='pnl', hole=0.4, title="PnL Sector Contribution Weights", template="plotly_dark")
            st.plotly_chart(fig_pie, use_container_width=True)
            
        st.markdown("---")
        st.subheader("🗂️ Live Operational Paper Trading Ledger System Audit Trail")
        st.dataframe(df_ledger.sort_index(ascending=False), use_container_width=True)