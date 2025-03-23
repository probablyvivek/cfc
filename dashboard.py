# dashboard.py
"""
Main dashboard application for the CFC Recovery Insights Dashboard.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Import from the refactored modules
from theme import THEME, apply_theme_css
from data_processing import load_data, calculate_rolling_average, get_weekly_summary
from data_generator import generate_sample_data
from analysis import get_recommendations
from visualization import create_plotly_chart, create_weekly_summary_chart

# === Page Setup ===
st.set_page_config(
    page_title="CFC Recovery Insights Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply CSS styling
st.markdown(apply_theme_css(), unsafe_allow_html=True)

# === Sidebar ===
def setup_sidebar():
    with st.sidebar:
        st.image("https://upload.wikimedia.org/wikipedia/en/thumb/c/cc/Chelsea_FC.svg/800px-Chelsea_FC.svg.png", width=80)
        st.markdown("## Dashboard Settings")
        
        # Data source section
        with st.expander("Data Source", expanded=False):
            st.write("Upload your recovery data or use the synthetic dataset to explore")
            uploaded_file = st.file_uploader("Upload Recovery CSV", type=["csv"])
        
        # Load data first to get player list
        df = load_data(uploaded_file)
        
        if df is None:
            st.error("Failed to load data. Please check your data source.")
            st.stop()
        
        # Player selection filter
        st.markdown("### Player Selection")
        all_players = sorted(df["player_name"].unique())
        
        # Default to the first player in the list
        default_player_idx = 0
        
        selected_player = st.selectbox(
            "Select Player",
            all_players,
            index=default_player_idx
        )
        
        # Filter data for selected player
        df_player = df[df["player_name"] == selected_player]
        
        # Time period filter
        st.markdown("### Time Period")
        option = st.selectbox(
            "Time period filter", 
            ["Last 7 days", "Last 14 days", "Last 30 days", "Last 90 days", "All"],
            index=2,
            label_visibility="collapsed"
        )
        
        # Risk threshold with more detailed slider
        st.markdown("### Risk Threshold")
        risk_threshold = st.slider(
            "Score below this value indicates risk", 
            min_value=-1.0, 
            max_value=0.0, 
            value=-0.4, 
            step=0.05,
            format="%.2f"
        )
        
        # Chart options
        st.markdown("### Chart Options")
        show_rolling_avg = st.checkbox("Show Rolling Average", value=True)
        rolling_window = st.slider("Rolling Window (days)", 3, 14, 7) if show_rolling_avg else 7
        
        # Recommendations panel toggle
        show_recommendations = st.checkbox("Show Recommendations", value=True)
        
        # Weekly summary toggle
        show_weekly_summary = st.checkbox("Show Weekly Summary", value=True)
        
        # Helpful tooltip
        st.markdown("""
        ---
        **Tip:** The EMBOSS score ranges from -1 to 1, where:
        - Scores above 0 indicate good recovery
        - Scores below 0 indicate fatigue
        - Scores below threshold require attention
        """)
        
        return df_player, option, risk_threshold, show_rolling_avg, rolling_window, show_recommendations, show_weekly_summary

# === Dashboard Header ===
def render_header(selected_player):
    st.markdown(f"""
    <div class="dashboard-header">
        <h1 class="dashboard-title">CFC Recovery Insights Dashboard</h1>
        <div class="user-info">
            <b>{datetime.now().strftime("%A, %d %B %Y")}</b><br>
            Manager: <b>Enzo</b> | Viewing: <b>{selected_player}</b>
        </div>
    </div>
    """, unsafe_allow_html=True)

# === Metrics Row ===
def render_metrics(filtered_df, risk_threshold):
    avg = filtered_df["emboss_baseline_score"].mean()
    recent_avg = filtered_df.tail(5)["emboss_baseline_score"].mean()
    below = (filtered_df["emboss_baseline_score"] < risk_threshold).sum()
    percent = (below / len(filtered_df)) * 100 if len(filtered_df) > 0 else 0
    trend = recent_avg - avg
    trend_icon = "↗️" if trend > 0 else "↘️" if trend < 0 else "→"

    # Display metrics in enhanced cards
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Average Score</div>
            <div class="metric-value">{avg:.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Recent Avg (5 days)</div>
            <div class="metric-value">{recent_avg:.2f} {trend_icon}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Days Below Threshold</div>
            <div class="metric-value">{below}</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Risk Percentage</div>
            <div class="metric-value">{percent:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    
    return below

# In dashboard.py
def render_status_box(filtered_df, risk_threshold):
    # Get recommendations from the analysis module
    recent_data = filtered_df.tail(7)  # Last 7 days
    recommendations = get_recommendations(recent_data, risk_threshold)
    
    status_color = THEME['ACCENT'] if recommendations['status'] == 'high_risk' else (THEME['WARNING'] if recommendations['status'] == 'moderate_risk' else THEME['SUCCESS'])
    status_text = recommendations['title']

    st.markdown(f"""
    <div class="status-box" style="background-color:{status_color}20; border-left:5px solid {status_color}">
        <div class="status-icon">{status_text.split(':')[0]}</div>
        <div>
            <h3 style="margin:0; color:{status_color};">{status_text.split(':')[1]}</h3>
        </div>
    </div>
    """, unsafe_allow_html=True)

# === Main Chart Area ===
def render_chart_area(filtered_df, risk_threshold, show_rolling_avg, rolling_window, weekly_summary_data, show_weekly_summary):
    st.markdown('<div class="chart-area">', unsafe_allow_html=True)
    
    # Chart Tabs
    chart_tab, weekly_tab = st.tabs(["Recovery Trend", "Weekly Summary"])
    
    with chart_tab:
        # Create and display the plotly chart
        fig = create_plotly_chart(
            filtered_df, 
            risk_threshold, 
            show_rolling_avg,
            rolling_window
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Chart description
        st.markdown("""
        This chart shows your daily EMBOSS recovery scores over time. Points below the risk threshold are highlighted in red. 
        The rolling average (blue line) helps identify overall trends in your recovery status.
        """)
    
    with weekly_tab:
        if show_weekly_summary and len(weekly_summary_data) > 0:
            weekly_chart = create_weekly_summary_chart(weekly_summary_data)
            st.plotly_chart(weekly_chart, use_container_width=True)
            
            st.markdown("""
            The weekly summary provides an overview of your recovery patterns by week. 
            Bars show the average score with error bars indicating min/max range. 
            The red line tracks the number of risk days per week.
            """)
        else:
            st.info("Weekly summary view is disabled or insufficient data for weekly view.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# === Recommendations Panel ===
def render_recommendations(filtered_df, risk_threshold, show_recommendations):
    if show_recommendations:
        # Get recommendations based on recent data
        recent_data = filtered_df.tail(7)  # Last 7 days
        recommendations = get_recommendations(recent_data, risk_threshold)
        status_color = THEME['ACCENT'] if recommendations['status'] == 'high_risk' else (THEME['WARNING'] if recommendations['status'] == 'moderate_risk' else THEME['SUCCESS'])
        
        # Display recommendations panel
        st.markdown(f"""
        <div class="recommendation-panel" style="border-left-color: {status_color}">
            <h3 style="color: {status_color}; margin-top: 0;">{recommendations['title']}</h3>
            <p><b>Analysis:</b> Based on your recent recovery scores, with 
            {recommendations['metrics']['below_threshold']} days below threshold and an average of 
            {recommendations['metrics']['recent_avg']:.2f}.</p>
            <h4>Recommendations:</h4>
            <ul>
                {"".join([f"<li>{rec}</li>" for rec in recommendations['recommendations']])}
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # Add a data insights section
        st.markdown("""
        <div class="recommendation-panel" style="border-left-color: #A3CEF1; margin-top: 20px;">
            <h3 style="color: #1A2B4C; margin-top: 0;">Data Insights</h3>
            <ul>
        """, unsafe_allow_html=True)
        
        # Calculate some insights
        insights = []
        
        # Insight 1: Best/worst days
        if len(filtered_df) >= 7:
            best_day = filtered_df.loc[filtered_df['emboss_baseline_score'].idxmax()]
            worst_day = filtered_df.loc[filtered_df['emboss_baseline_score'].idxmin()]
            insights.append(f"Your best recovery day was {best_day['date'].strftime('%A, %d %b')} with a score of {best_day['emboss_baseline_score']:.2f}")
            insights.append(f"Your worst recovery day was {worst_day['date'].strftime('%A, %d %b')} with a score of {worst_day['emboss_baseline_score']:.2f}")
        
        # Insight 2: Recovery pattern
        avg = filtered_df["emboss_baseline_score"].mean()
        recent_avg = filtered_df.tail(5)["emboss_baseline_score"].mean()
        trend = recent_avg - avg
        if trend > 0.1:
            insights.append(f"Your recovery trend is <b style='color:{THEME['SUCCESS']}'>improving</b> with a {trend:.2f} increase in recent average")
        elif trend < -0.1:
            insights.append(f"Your recovery trend is <b style='color:{THEME['ACCENT']}'>declining</b> with a {abs(trend):.2f} decrease in recent average")
        else:
            insights.append(f"Your recovery trend is <b>stable</b> with minimal changes in recent average")
        
        # Insight 3: Recovery consistency
        std_dev = filtered_df['emboss_baseline_score'].std()
        if std_dev < 0.2:
            insights.append(f"Your recovery scores show high consistency (std dev: {std_dev:.2f})")
        elif std_dev > 0.4:
            insights.append(f"Your recovery scores show high variability (std dev: {std_dev:.2f}), indicating potential recovery issues")
        
        # Display insights
        st.markdown("".join([f"<li>{insight}</li>" for insight in insights]) + """
            </ul>
        </div>
        """, unsafe_allow_html=True)

# === Footer ===
def render_footer():
    st.markdown("""
    <div class="dashboard-footer">
        <p>CFC Recovery Insights Dashboard | Version 2.0 | Developed with ♥ by Vivek Tiwari</p>
    </div>
    """, unsafe_allow_html=True)

# === Main Function ===
def main():
    # Setup sidebar and get parameters
    df_player, option, risk_threshold, show_rolling_avg, rolling_window, show_recommendations, show_weekly_summary = setup_sidebar()
    
    # Filter data based on selected time period
    end_date = df_player["date"].max()
    if option == "All":
        start_date = df_player["date"].min()
    elif option == "Last 7 days":
        start_date = end_date - timedelta(days=7)
    elif option == "Last 14 days":
        start_date = end_date - timedelta(days=14)
    elif option == "Last 30 days":
        start_date = end_date - timedelta(days=30)
    elif option == "Last 90 days":
        start_date = end_date - timedelta(days=90)

    filtered_df = df_player[(df_player["date"] >= start_date) & (df_player["date"] <= end_date)]
    
    # Calculate weekly summary data
    weekly_summary_data = get_weekly_summary(filtered_df, risk_threshold)
    
    # Render header
    render_header(df_player["player_name"].iloc[0] if len(df_player) > 0 else "Unknown Player")
    
    # Render metrics
    below = render_metrics(filtered_df, risk_threshold)
    
    # Render status box
    render_status_box(filtered_df, risk_threshold)
    
    # Create main content columns
    left_col, right_col = st.columns([2, 1])
    
    with left_col:
        # Render chart area
        render_chart_area(filtered_df, risk_threshold, show_rolling_avg, rolling_window, weekly_summary_data, show_weekly_summary)
    
    with right_col:
        # Render recommendations panel
        render_recommendations(filtered_df, risk_threshold, show_recommendations)
    
    # Render footer
    render_footer()

if __name__ == "__main__":
    main()