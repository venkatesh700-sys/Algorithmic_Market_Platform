import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime, timedelta
import os

# Page structural configuration layout
st.set_page_config(page_title="AI Agent Report Workspace", page_icon="📈", layout="wide")
st.title("📈 Performance Audit & Multi-Timeframe Analytics Center")
st.markdown("Detailed breakdown tracking automated paper investments, strategy gain percentages, and exit parameters.")

DB_FILE = "quant_trading_desk.db"

if not os.path.exists(DB_FILE):
    st.warning("⚠️ Execution database missing. Run your scanner scripts to generate initial paper logs.")
else:
    conn = sqlite3.connect(DB_FILE)
    df_ledger = pd.read_sql_query("SELECT * FROM trade_ledger", conn)
    conn.close()
    
    if df_ledger.empty:
        st.info("Ledger registry empty. Awaiting initial transaction executions.")
    else:
        # Enforce explicit datetime type tracking conversions
        df_ledger['date'] = pd.to_datetime(df_ledger['date'])
        
        # --- TIMEFRAME BOUNDARY DEFINITIONS ---
        today_date = pd.to_datetime(datetime.now().date())
        start_of_week = today_date - timedelta(days=today_date.weekday()) # Monday baseline anchor
        start_of_month = today_date.replace(day=1) # First day of ongoing month boundary
        
        # --- TAB SELECTION INTERFACE CONTROLS ---
        st.subheader("🗓️ Select Report Interval Scope")
        tab_day, tab_week, tab_month = st.tabs(["📋 Daily Summary Report", "📅 Weekly Performance Audit", "📊 Monthly Master Analytics"])
        
        def render_report_metrics(filtered_df, label_context):
            """Generates explicit mathematical stats breakdown blocks for each timeframe tier."""
            if filtered_df.empty:
                st.info(f"No trading activities logged inside the designated {label_context} profile window.")
                return
                
            total_trades = len(filtered_df)
            wins_df = filtered_df[filtered_df['status'] == 'WIN']
            losses_df = filtered_df[filtered_df['status'] == 'LOSS']
            
            wins_count = len(wins_df)
            win_rate = (wins_count / total_trades) * 100 if total_trades > 0 else 0.0
            
            # Detailed financial calculations matching metrics specifications
            # Investment value tracking allocation formula: entry * quantity
            filtered_df['Total_Invested'] = filtered_df['entry_price'] * filtered_df['quantity']
            sum_total_invested = filtered_df['Total_Invested'].sum()
            
            net_profit_loss = filtered_df['pnl'].sum()
            overall_gain_pct = (net_profit_loss / sum_total_invested) * 100 if sum_total_invested > 0 else 0.0
            
            # --- CARD SCOREBOARDS SCORING DISPLAY ---
            m_col1, m_col2, m_col3, m_col4 = st.columns(4)
            m_col1.metric(f"Total Invested ({label_context})", f"₹{sum_total_invested:,.2f}")
            m_col2.metric(f"Net Profit/Loss Return", f"₹{net_profit_loss:+,.2f}", f"{overall_gain_pct:+.2f}% Margin")
            m_col3.metric("System Accuracy Win Rate", f"{win_rate:.1f}%", f"{wins_count} Wins vs {total_trades - wins_count} Losses")
            
            # Profit Factor metric calculation formulation
            gross_p = wins_df['pnl'].sum()
            gross_l = abs(losses_df['pnl'].sum())
            profit_factor = gross_p / gross_l if gross_l > 0 else gross_p
            m_col4.metric("Audited Profit Factor", f"{profit_factor:.2f}", "Minimum Target Requirement: >=2.0")
            
            st.markdown("---")
            
            # --- BREAKDOWN TRACKING TABLES LAYOUT ---
            table_col, chart_col = st.columns([3, 2])
            
            with table_col:
                st.subheader(f"🔍 Detailed Position Exit Registry ({label_context})")
                display_df = filtered_df.copy()
                display_df['Gain/Loss %'] = ((display_df['exit_price'] - display_df['entry_price']) / display_df['entry_price']) * 100
                
                # Format clean visual structural tables output logs mapping parameters
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
                st.plotly_chart(fig_status, use_container_width=True)
                
            # --- SPECIFIC TARGET ACTION LOSS INVESTIGATION AUDITS ---
            if not losses_df.empty:
                with st.expander(f"⚠️ View Comprehensive Root-Cause Loss Analysis Report ({label_context})"):
                    st.markdown("The following assets hit their protective risk stop boundaries. Review entry features to protect accuracy filters:")
                    for idx, row in losses_df.iterrows():
                        loss_gain_pct = ((row['exit_price'] - row['entry_price']) / row['entry_price']) * 100
                        st.error(
                            f"• **{row['ticker']}** ({row['strategy_type']}) -> "
                            f"Entered at ₹{row['entry_price']}, hit Stop Loss Protection exit at ₹{row['exit_price']}. "
                            f"Position Loss: **{loss_gain_pct:.2f}%** | Capital Subtracted: **₹{abs(row['pnl']):,.2f}**"
                        )
                        
        # --- TAB CORE ROUTING INJECTIONS ---
        with tab_day:
            df_day = df_ledger[df_ledger['date'].dt.date == today_date.date()]
            render_report_metrics(df_day, "Today")
            
        with tab_week:
            df_week = df_ledger[(df_ledger['date'] >= start_of_week) & (df_ledger['date'] <= today_date)]
            render_report_metrics(df_week, "This Week")
            
        with tab_month:
            df_month = df_ledger[(df_ledger['date'] >= start_of_month) & (df_ledger['date'] <= today_date)]
            render_report_metrics(df_month, "This Month")
