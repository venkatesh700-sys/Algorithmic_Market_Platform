import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime, timedelta
import os
import urllib.request

# --- INITIAL GLOBAL LAYOUT CONFIGURATION ---
st.set_page_config(page_title="AI Agent Report Workspace", page_icon="📊", layout="wide")
st.title("📊 Quantitative AI Engine Performance & Analytics Center")
st.markdown("Detailed breakdown tracking automated paper investments, strategy gain percentages, and exit parameters.")

DB_FILE = "quant_trading_desk.db"

# --- REAL-TIME CLOUD DATABASE DISCOVERY INTERNET PROTOCOL ---
if not os.path.exists(DB_FILE):
    # Automatically pulls your repository tracking database over the web
    GITHUB_RAW_URL = "https://raw.githubusercontent.com/venkatesh700-sys/Algorithmic_Market_Platform/main/quant_trading_desk.db"
    try:
        urllib.request.urlretrieve(GITHUB_RAW_URL, DB_FILE)
    except Exception:
        st.error("⚠️ System Notice: Failed to pull raw cloud database records from GitHub.")

# --- CHECK FOR FILE AVAILABILITY ---
if not os.path.exists(DB_FILE) or os.stat(DB_FILE).st_size == 0:
    st.warning("⚠️ Execution database missing or unpopulated. Awaiting initial paper trading transaction logs.")
    
    # FIXED: Added valid sample quantities to the list below to eliminate the syntax error!
    st.info("💡 Loading baseline interface layout preview metrics simulation:")
    mock_data = {
    'date': [
        datetime.now() - timedelta(days=2),
        datetime.now() - timedelta(days=1),
        datetime.now()
    ],
    'ticker': ['RELIANCE.NS', 'TCS.NS', 'INFY.NS'],
    'strategy_type': ['INTRADAY', 'SWING', 'INTRADAY'],
    'entry_price': [2450.0, 3400.0, 1500.0],
    'exit_price': [2472.0, 3624.0, 1494.0],
    'quantity': [16, 11, 26],
    'status': ['WIN', 'WIN', 'LOSS'],
    'pnl': [352.0, 2464.0, -156.0]
}
    df_ledger = pd.DataFrame(mock_data)
else:
    # Safely connect and read from the SQLite database
    conn = sqlite3.connect(DB_FILE)
    df_ledger = pd.read_sql_query("SELECT * FROM trade_ledger", conn)
    conn.close()

# --- RUN ENGINE CALCULATION MATRIX ---
if not df_ledger.empty:
    df_ledger['date'] = pd.to_datetime(df_ledger['date'])
    
    # Timeframe calculation anchors
    today_date = pd.to_datetime(datetime.now().date())
    start_of_week = today_date - timedelta(days=today_date.weekday())
    start_of_month = today_date.replace(day=1)
    
    st.subheader("🗓️ Select Report Interval Scope")
    tab_day, tab_week, tab_month = st.tabs(["📋 Daily Summary Report", "📅 Weekly Performance Audit", "📊 Master Analytics"])
    
    def render_report_metrics(filtered_df, label_context):
        if filtered_df.empty:
            st.info(f"No trading activities logged inside the designated {label_context} profile window.")
            return
            
        total_trades = len(filtered_df)
        wins_df = filtered_df[filtered_df['status'] == 'WIN']
        losses_df = filtered_df[filtered_df['status'] == 'LOSS']
        
        wins_count = len(wins_df)
        win_rate = (wins_count / total_trades) * 100 if total_trades > 0 else 0.0
        
        # Calculate dynamic transaction parameters
        filtered_df['Total_Invested'] = filtered_df['entry_price'] * filtered_df['quantity']
        sum_total_invested = filtered_df['Total_Invested'].sum()
        
        net_profit_loss = filtered_df['pnl'].sum()
        overall_gain_pct = (net_profit_loss / sum_total_invested) * 100 if sum_total_invested > 0 else 0.0
        
        gross_p = wins_df['pnl'].sum()
        gross_l = abs(losses_df['pnl'].sum())
        profit_factor = gross_p / gross_l if gross_l > 0 else gross_p
        
        # --- CARD METRIC SCOREBOARDS DISPLAY ---
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        m_col1.metric(f"Total Invested ({label_context})", f"₹{sum_total_invested:,.2f}")
        m_col2.metric(f"Net Profit/Loss Return", f"₹{net_profit_loss:+,.2f}", f"{overall_gain_pct:+.2f}% Margin")
        m_col3.metric("System Accuracy Win Rate", f"{win_rate:.1f}%", f"{wins_count} Wins vs {total_trades - wins_count} Losses")
        m_col4.metric("Audited Profit Factor", f"{profit_factor:.2f}", "Minimum Target Requirement: >=2.0")
        
        st.markdown("---")
        
        # --- GRAPHICS CHART SECTIONS LAYOUT ---
        table_col, chart_col = st.columns(2)
        
        with table_col:
            st.subheader(f"🔍 Detailed Position Exit Registry ({label_context})")
            display_df = filtered_df.copy()
            display_df['Gain/Loss %'] = ((display_df['exit_price'] - display_df['entry_price']) / display_df['entry_price']) * 100
            
            st.dataframe(
                display_df[['date', 'ticker', 'strategy_type', 'entry_price', 'exit_price', 'quantity', 'Gain/Loss %', 'status', 'pnl']]
                .sort_values(by='date', ascending=False),
                use_container_width=True
            )
            
        with chart_col:
            st.subheader("🎯 Distribution Balance Outcomes")
            fig_status = px.bar(
                filtered_df.groupby('status').size().reset_index(name='Positions'),
                x='status', y='Positions', color='status',
                color_discrete_map={'WIN': '#00FFCC', 'LOSS': '#FF3366'},
                template="plotly_dark"
            )
            st.plotly_chart(fig_status, use_container_width=True, key=f"status_chart_{label_context}")

            
        # --- OPTIONAL DIAGNOSTICS FOR UNEXPECTED POSITION LOSSES ---
        if not losses_df.empty:
            with st.expander(f"⚠️ View Comprehensive Root-Cause Loss Analysis Report ({label_context})"):
                st.markdown("The following assets hit their protective risk stop boundaries. Review parameters to protect accuracy filters:")
                for idx, row in losses_df.iterrows():
                    loss_gain_pct = ((row['exit_price'] - row['entry_price']) / row['entry_price']) * 100
                    st.error(
                        f"• **{row['ticker']}** ({row['strategy_type']}) -> "
                        f"Entered at ₹{row['entry_price']}, hit Stop Loss Protection exit at ₹{row['exit_price']}. "
                        f"Position Loss: **{loss_gain_pct:.2f}%** | Capital Subtracted: **₹{abs(row['pnl']):,.2f}**"
                    )

    # --- INJECT DATA RANGE INTO RELEVANT DISPLAY CHANNELS ---
    with tab_day:
        df_day = df_ledger[df_ledger['date'].dt.date == today_date.date()]
        render_report_metrics(df_day, "Today")
        
    with tab_week:
        df_week = df_ledger[(df_ledger['date'] >= start_of_week) & (df_ledger['date'] <= today_date)]
        render_report_metrics(df_week, "This Week")
        
    with tab_month:
        df_month = df_ledger[(df_ledger['date'] >= start_of_month) & (df_ledger['date'] <= today_date)]
        render_report_metrics(df_month, "This Month")
