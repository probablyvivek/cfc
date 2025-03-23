# dashboard.py
"""
Main dashboard application for the CFC Recovery Insights Dashboard.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go

# Import from modules
from theme import THEME, apply_theme_css
from data_processing import load_data, calculate_rolling_average, get_weekly_summary
from data_generator import generate_sample_data
from analysis import get_recommendations, analyze_workload_progression
from visualization import create_plotly_chart, create_weekly_summary_chart
from team_readiness import render_match_readiness_dashboard, PLAYER_POSITIONS

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
        
        # Dashboard view selection (new)
        dashboard_view = st.radio(
            "Select Dashboard View",
            options=["Individual Player", "Team Readiness"],
            index=0
        )
        
        # Data source section
        with st.expander("Data Source", expanded=False):
            st.write("Upload your recovery data or use the synthetic dataset to explore")
            uploaded_file = st.file_uploader("Upload Recovery CSV", type=["csv"])
            
            # Add a button to regenerate synthetic data
            if st.button("Regenerate Synthetic Data"):
                st.session_state['regenerate_data'] = True
            else:
                if 'regenerate_data' not in st.session_state:
                    st.session_state['regenerate_data'] = False
        
        # Load data first to get player list
        if 'regenerate_data' in st.session_state and st.session_state['regenerate_data']:
            df = generate_sample_data(24)  # Generate data for all 24 players
            st.session_state['regenerate_data'] = False
        else:
            df = load_data(uploaded_file)
        
        if df is None:
            st.error("Failed to load data. Please check your data source.")
            st.stop()
        
        # Common settings regardless of view
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
        
        # Individual player view settings
        if dashboard_view == "Individual Player":
            # Player selection filter
            st.markdown("### Player Selection")
            all_players = sorted(df["player_name"].unique())
            
            # Default to a key player
            default_player_idx = all_players.index("Cole Palmer") if "Cole Palmer" in all_players else 0
            
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
            
            # Chart options
            st.markdown("### Chart Options")
            show_rolling_avg = st.checkbox("Show Rolling Average", value=True)
            rolling_window = st.slider("Rolling Window (days)", 3, 14, 7) if show_rolling_avg else 7
            
            # Recommendations panel toggle
            show_recommendations = st.checkbox("Show Recommendations", value=True)
            
            # Weekly summary toggle
            show_weekly_summary = st.checkbox("Show Weekly Summary", value=True)
            
            # Workload analysis toggle
            show_workload_analysis = st.checkbox("Show Workload Analysis", value=True)
            
            # Helpful tooltip
            st.markdown("""
            ---
            **Tip:** The EMBOSS score ranges from -1 to 1, where:
            - Scores above 0 indicate good recovery
            - Scores below 0 indicate fatigue
            - Scores below threshold require attention
            """)
            
            return dashboard_view, df, df_player, option, risk_threshold, show_rolling_avg, rolling_window, show_recommendations, show_weekly_summary, show_workload_analysis
        
        # Team readiness view settings
        else:
            # No additional settings needed for team view
            # Pass empty values for individual player settings
            return dashboard_view, df, None, None, risk_threshold, None, None, None, None, None

# === Dashboard Header ===
def render_header(dashboard_view, selected_player=None):
    if dashboard_view == "Individual Player":
        st.markdown(f"""
        <div class="dashboard-header">
            <h1 class="dashboard-title">CFC Recovery Insights Dashboard</h1>
            <div class="user-info">
                <b>{datetime.now().strftime("%A, %d %B %Y")}</b><br>
                Physiotherapist/Workload Specialist View | Viewing: <b>{selected_player}</b>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="dashboard-header">
            <h1 class="dashboard-title">CFC Team Readiness Dashboard</h1>
            <div class="user-info">
                <b>{datetime.now().strftime("%A, %d %B %Y")}</b><br>
                Physiotherapist/Workload Specialist View | <b>Match Day Preparation</b>
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

# === Status Box ===
def render_status_box(filtered_df, risk_threshold):
    # Get recommendations from the analysis module
    recent_data = filtered_df.tail(7)  # Last 7 days
    recommendations = get_recommendations(recent_data, risk_threshold)
    
    status_color = THEME['ACCENT'] if recommendations['status'] == 'high_risk' else (THEME['WARNING'] if recommendations['status'] == 'moderate_risk' else THEME['SUCCESS'])
    
    # Extract the emoji and the rest of the title
    if ":" in recommendations['title']:
        emoji_part = recommendations['title'].split(':')[0] + ":"
        text_part = recommendations['title'].split(':', 1)[1].strip()
    else:
        emoji_part = ""
        text_part = recommendations['title']

    st.markdown(f"""
    <div class="status-box" style="background-color:{status_color}20; border-left:5px solid {status_color}">
        <div class="status-icon">{emoji_part}</div>
        <div>
            <h3 style="margin:0; color:{status_color};">{text_part}</h3>
        </div>
    </div>
    """, unsafe_allow_html=True)

# === Main Chart Area ===
def render_chart_area(filtered_df, risk_threshold, show_rolling_avg, rolling_window, weekly_summary_data, show_weekly_summary, player_name="Unknown Player"):
    st.markdown('<div class="chart-area">', unsafe_allow_html=True)
    
    # Chart Tabs
    chart_tab, weekly_tab = st.tabs(["Recovery Trend", "Weekly Summary"])
    
    with chart_tab:
        # Create and display the plotly chart
        fig = create_plotly_chart(
            filtered_df, 
            risk_threshold, 
            show_rolling_avg,
            rolling_window,
            player_name
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Chart description
        st.markdown("""
        This chart shows daily EMBOSS recovery scores over time. Points below the risk threshold are highlighted in red. 
        The rolling average (blue line) helps identify overall trends in recovery status.
        """)
    
    with weekly_tab:
        if show_weekly_summary and len(weekly_summary_data) > 0:
            weekly_chart = create_weekly_summary_chart(weekly_summary_data)
            st.plotly_chart(weekly_chart, use_container_width=True)
            
            st.markdown("""
            The weekly summary provides an overview of recovery patterns by week. 
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
            <p><b>Analysis:</b> Based on recent recovery scores, with 
            {recommendations['metrics']['below_threshold']} days below threshold and an average of 
            {recommendations['metrics']['recent_avg']:.2f}.</p>
        """, unsafe_allow_html=True)
        
        # Add trend and variability if available in the metrics
        if 'trend' in recommendations['metrics'] and 'variability' in recommendations['metrics']:
            st.markdown(f"""
            <p>
                <b>Recovery Trend:</b> {recommendations['metrics']['trend']:.2f} 
                ({("Improving" if recommendations['metrics']['trend'] > 0 else "Declining") if abs(recommendations['metrics']['trend']) > 0.05 else "Stable"})
                <br>
                <b>Recovery Stability:</b> {recommendations['metrics']['variability']:.2f}
                ({("Unstable" if recommendations['metrics']['variability'] > 0.3 else "Moderately stable") if recommendations['metrics']['variability'] > 0.2 else "Stable"})
            </p>
            """, unsafe_allow_html=True)
            
        st.markdown(f"""
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
            insights.append(f"Best recovery day was {best_day['date'].strftime('%A, %d %b')} with a score of {best_day['emboss_baseline_score']:.2f}")
            insights.append(f"Worst recovery day was {worst_day['date'].strftime('%A, %d %b')} with a score of {worst_day['emboss_baseline_score']:.2f}")
        
        # Insight 2: Recovery pattern
        avg = filtered_df["emboss_baseline_score"].mean()
        recent_avg = filtered_df.tail(5)["emboss_baseline_score"].mean()
        trend = recent_avg - avg
        if trend > 0.1:
            insights.append(f"Recovery trend is <b style='color:{THEME['SUCCESS']}'>improving</b> with a {trend:.2f} increase in recent average")
        elif trend < -0.1:
            insights.append(f"Recovery trend is <b style='color:{THEME['ACCENT']}'>declining</b> with a {abs(trend):.2f} decrease in recent average")
        else:
            insights.append(f"Recovery trend is <b>stable</b> with minimal changes in recent average")
        
        # Insight 3: Recovery consistency
        std_dev = filtered_df['emboss_baseline_score'].std()
        if std_dev < 0.2:
            insights.append(f"Recovery scores show high consistency (std dev: {std_dev:.2f})")
        elif std_dev > 0.4:
            insights.append(f"Recovery scores show high variability (std dev: {std_dev:.2f}), indicating potential recovery issues")
        
        # Display insights
        st.markdown("".join([f"<li>{insight}</li>" for insight in insights]) + """
            </ul>
        </div>
        """, unsafe_allow_html=True)

# === Workload Analysis Panel ===
def render_workload_analysis(df_player, filtered_df, risk_threshold):
    # Get complete player data for acute:chronic calculation (need at least 4 weeks)
    # Current week data (last 7 days)
    current_week_data = filtered_df.tail(7)
    
    # Calculate workload analysis
    workload_analysis = analyze_workload_progression(df_player, current_week_data, risk_threshold)
    
    # Set color based on status
    if workload_analysis['status'] == 'high_spike':
        status_color = THEME['ACCENT']
    elif workload_analysis['status'] == 'detraining_risk':
        status_color = THEME['WARNING']
    else:
        status_color = THEME['SUCCESS']
    
    # Display the workload analysis panel
    st.markdown(f"""
    <div class="recommendation-panel" style="border-left-color: {status_color}">
        <h3 style="color: {status_color}; margin-top: 0;">{workload_analysis['title']}</h3>
    """, unsafe_allow_html=True)
    
    # Only show ACWR metrics if we have sufficient data
    if workload_analysis['status'] != 'insufficient_data':
        st.markdown(f"""
        <p>
            <b>Acute:Chronic Workload Ratio:</b> {workload_analysis.get('acwr', 0):.2f}
            <br><b>Week-to-Week Change:</b> {workload_analysis.get('week_change', 0):.2f}
        </p>
        """, unsafe_allow_html=True)
        
        # Create a simple chart showing acute vs chronic load
        if len(df_player) >= 28:  # Only if we have enough data for 4 weeks
            # Calculate weekly averages for recent weeks
            recent_weeks = []
            for i in range(4):
                if len(df_player) >= (i+1)*7:
                    start_idx = len(df_player) - (i+1)*7
                    end_idx = len(df_player) - i*7 if i > 0 else len(df_player)
                    week_data = df_player.iloc[start_idx:end_idx]
                    week_avg = week_data['emboss_baseline_score'].mean()
                    recent_weeks.append(week_avg)
            
            recent_weeks.reverse()  # Order from oldest to newest
            
            # Create chart
            fig = go.Figure()
            
            # Add bar chart for weekly averages with better colors
            fig.add_trace(go.Bar(
                x=['Week -3', 'Week -2', 'Week -1', 'Current'],
                y=recent_weeks,
                name='Weekly Load',
                marker_color=[THEME['SECONDARY'], THEME['SECONDARY'], 
                              THEME['SECONDARY'], THEME['PRIMARY']],
                marker_line_color='rgba(0,0,0,0.3)',
                marker_line_width=1,
                opacity=0.85
            ))
            
            # Add chronic load line with better styling
            if len(recent_weeks) == 4:
                chronic_load = sum(recent_weeks[:3]) / 3
                fig.add_trace(go.Scatter(
                    x=['Week -3', 'Week -2', 'Week -1', 'Current'],
                    y=[chronic_load, chronic_load, chronic_load, chronic_load],
                    mode='lines',
                    name='Chronic Load (3-week avg)',
                    line=dict(color=THEME['TEXT'], width=2, dash='dash')
                ))
                
                # Add shaded area for the safe zone (±10% of chronic load)
                upper_safe = min(1, chronic_load + 0.1)
                lower_safe = max(-1, chronic_load - 0.1)
                
                x_values = ['Week -3', 'Week -2', 'Week -1', 'Current', 
                            'Current', 'Week -1', 'Week -2', 'Week -3']
                y_values = [upper_safe, upper_safe, upper_safe, upper_safe,
                            lower_safe, lower_safe, lower_safe, lower_safe]
                
                fig.add_trace(go.Scatter(
                    x=x_values,
                    y=y_values,
                    fill='toself',
                    fillcolor='rgba(42, 157, 143, 0.1)',
                    line=dict(width=0),
                    name='Safe Zone (±10%)',
                    hoverinfo='skip'
                ))
            
            # Update layout with better styling
            fig.update_layout(
                title={
                    'text': "Acute vs Chronic Workload",
                    'y': 0.95,
                    'x': 0.5,
                    'xanchor': 'center',
                    'yanchor': 'top',
                    'font': dict(size=18, color=THEME['PRIMARY'])
                },
                height=250,
                margin=dict(l=20, r=20, t=40, b=30),
                yaxis_title="EMBOSS Score Avg",
                yaxis=dict(
                    range=[-1, 1],  # Match the scale of EMBOSS scores
                    showgrid=True,
                    gridcolor='rgba(220, 220, 220, 0.8)',
                    zeroline=True,
                    zerolinecolor='rgba(0, 0, 0, 0.2)'
                ),
                xaxis=dict(
                    showgrid=False,
                    tickangle=-0
                ),
                showlegend=True,
                legend=dict(
                    orientation="h", 
                    yanchor="top", 
                    y=-0.15, 
                    xanchor="center", 
                    x=0.5
                ),
                plot_bgcolor='white',
                hovermode='x unified'
            )
            
            # Add annotation for the ACWR value
            acwr_value = workload_analysis.get('acwr', 0)
            acwr_color = "red" if acwr_value > 1.3 else ("orange" if acwr_value > 1.1 else "green")
            
            fig.add_annotation(
                x="Current",
                y=recent_weeks[3] + 0.05,
                text=f"ACWR: {acwr_value:.2f}",
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor=acwr_color,
                font=dict(size=12, color=acwr_color, family="Arial, sans-serif"),
                bordercolor=acwr_color,
                borderwidth=1,
                borderpad=4,
                bgcolor="white",
                opacity=0.8
            )
            
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.markdown("<p><i>Collecting baseline data for workload analysis. At least 4 weeks of data required.</i></p>", unsafe_allow_html=True)
    
    # Show recommendations
    st.markdown("<h4>Workload Recommendations:</h4><ul>", unsafe_allow_html=True)
    for rec in workload_analysis['recommendations']:
        st.markdown(f"<li>{rec}</li>", unsafe_allow_html=True)
    st.markdown("</ul></div>", unsafe_allow_html=True)

# === Footer ===
def render_footer():
    st.markdown("""
    <div class="dashboard-footer">
        <p>CFC Recovery Insights Dashboard | Version 2.0 | Developed by Performance Science Team</p>
    </div>
    """, unsafe_allow_html=True)

# === Main Function ===
def main():
    # Setup sidebar and get parameters
    results = setup_sidebar()
    dashboard_view = results[0]
    all_player_data = results[1]
    
    if dashboard_view == "Individual Player":
        # Unpack individual player view settings
        _, _, df_player, option, risk_threshold, show_rolling_avg, rolling_window, show_recommendations, show_weekly_summary, show_workload_analysis = results
        
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
        
        # Get player name for display
        player_name = df_player["player_name"].iloc[0] if len(df_player) > 0 else "Unknown Player"
        
        # Render individual player dashboard
        render_header(dashboard_view, player_name)
        
        # Render metrics
        render_metrics(filtered_df, risk_threshold)
        
        # Render status box
        render_status_box(filtered_df, risk_threshold)
        
        # Create main content columns
        left_col, right_col = st.columns([2, 1])
        
        with left_col:
            # Render chart area
            render_chart_area(filtered_df, risk_threshold, show_rolling_avg, rolling_window, 
                            weekly_summary_data, show_weekly_summary, player_name)
        
        with right_col:
            if show_recommendations:
                render_recommendations(filtered_df, risk_threshold, show_recommendations)
            else:
                st.info("Recovery recommendations are disabled")
        
        # Add some spacing
        st.markdown("<br>", unsafe_allow_html=True)
        
        if show_workload_analysis:
            render_workload_analysis(df_player, filtered_df, risk_threshold)
        else:
            st.info("Workload analysis is disabled")
    
    else:
        # Team readiness view
        _, _, _, _, risk_threshold, _, _, _, _, _ = results
        
        # Render team readiness dashboard
        render_header(dashboard_view)
        
        # Render team readiness content
        render_match_readiness_dashboard(all_player_data, risk_threshold)
    
    # Render footer
    render_footer()

if __name__ == "__main__":
    main()