# dashboard.py
"""
Main Streamlit application for the CFC Recovery Insights Dashboard.
Provides two views: Individual Player Analysis and Team Match Readiness.
"""

import streamlit as st
import pandas as pd
import numpy as np # Import numpy
from datetime import datetime, timedelta
import plotly.graph_objects as go
from collections import namedtuple # For sidebar settings return

# Import from local modules
from theme import THEME, apply_theme_css, STATUS_COLORS
from data_processing import load_data, calculate_rolling_average, get_weekly_summary
from data_generator import generate_sample_data
from analysis import get_recommendations
from visualization import create_plotly_chart, create_weekly_summary_chart
from team_readiness import render_match_readiness_dashboard

# Page Configuration
st.set_page_config(
    page_title="CFC Recovery Insights",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "# CFC Recovery Insights Dashboard" # Updated version
    }
)

# Apply Custom CSS Theme
st.markdown(apply_theme_css(), unsafe_allow_html=True)

# Define a structure for sidebar settings for cleaner return value
SidebarSettings = namedtuple("SidebarSettings", [
    "dashboard_view", "data_source", "risk_threshold", "selected_player",
    "time_period_option", "show_rolling_avg", "rolling_window",
    "show_recommendations", "show_weekly_summary",
    "uploaded_file" # Add uploaded_file to the named tuple
])

# --- Sidebar Function ---
# Pass df_full for player list, but handle data loading based on uploader inside main
def setup_sidebar(df_for_player_list):
    """Configure the sidebar options and return user settings."""
    with st.sidebar:
        # 1. Logo
        st.image("https://upload.wikimedia.org/wikipedia/en/thumb/c/cc/Chelsea_FC.svg/800px-Chelsea_FC.svg.png", width=200)

        # 2. File Uploader --- MOVED HERE ---
        uploaded_file = st.file_uploader(
            "Upload Recovery CSV (Optional)",
            type=["csv"],
            help="Upload your own data (CSV format). Uses default/synthetic data if none provided."
        )
        st.markdown("---") # Separator after uploader

        # 3. Dashboard Controls Title
        st.markdown("## Dashboard Controls")

        # 4. Dashboard View Selection
        dashboard_view = st.radio(
            "Select View",
            options=["Individual Player", "Team Readiness"],
            index=0,
            horizontal=True,
            help="Choose between detailed analysis for one player or team overview for match readiness."
        )
        st.markdown("---")

        # 5. Risk Threshold
        risk_threshold = st.slider(
            "Recovery Risk Threshold",
            min_value=-0.8, max_value=0.2, value=-0.4, step=0.05,
            format="%.2f",
            help="Scores below this value are flagged as potential risk. Adjust based on team context."
        )
        st.markdown("---")

        # --- View Specific Settings ---
        if dashboard_view == "Individual Player":
            st.markdown("### Individual Player Settings")

            # Player Selection - Use the passed DataFrame for the list
            player_list = ["Select Player..."]
            if df_for_player_list is not None and not df_for_player_list.empty:
                 if 'player_name' in df_for_player_list.columns:
                    try:
                        player_list.extend(sorted(df_for_player_list["player_name"].unique()))
                    except Exception as e:
                        st.warning(f"Could not get player list: {e}")
                 else:
                     st.warning("Dataset missing 'player_name' column.")

            default_player_name = "Cole Palmer"
            default_player_index = player_list.index(default_player_name) if default_player_name in player_list else 0
            if len(player_list) > 1 and default_player_index == 0:
                default_player_index = 1

            selected_player = st.selectbox(
                "Select Player", player_list,
                index=default_player_index,
                 help="Choose the player to analyze."
            )

            time_period_option = st.selectbox(
                "Select Time Period",
                ["Last 7 days", "Last 14 days", "Last 30 days", "Last 90 days", "All Time"],
                index=2, help="Filter the data shown in charts and metrics for the selected player."
            )

            with st.expander("Display Options", expanded=False):
                show_rolling_avg = st.checkbox("Show Rolling Average", value=True)
                rolling_window = st.slider("Rolling Window (days)", 3, 14, 7, disabled=not show_rolling_avg)
                st.markdown("---")
                show_weekly_summary = st.checkbox("Show Weekly Summary Tab", value=True)
                show_recommendations = st.checkbox("Show Recovery Recommendations", value=True)

            st.markdown("""
            ---
           Tip: The EMBOSS score ranges from -1 to 1, where:\n
            - Scores above 0 indicate good recovery
            - Scores below 0 indicate fatigue
            - Scores below threshold require attention
            """)

            return SidebarSettings(
                dashboard_view=dashboard_view, data_source=None, # data_source will be loaded in main
                risk_threshold=risk_threshold,
                selected_player=selected_player if selected_player != "Select Player..." else None,
                time_period_option=time_period_option, show_rolling_avg=show_rolling_avg,
                rolling_window=rolling_window, show_recommendations=show_recommendations,
                show_weekly_summary=show_weekly_summary,
                uploaded_file=uploaded_file # Return the file object
            )

        else: # Team Readiness
            return SidebarSettings(
                dashboard_view=dashboard_view, data_source=None, risk_threshold=risk_threshold,
                selected_player=None, time_period_option=None, show_rolling_avg=None,
                rolling_window=None, show_recommendations=None, show_weekly_summary=None,
                uploaded_file=uploaded_file # Also return file object here
            )


# --- Data Loading Section ---
@st.cache_data(ttl=600)
def get_data(uploaded_file_obj):
    """Loads data based on the uploaded file object, using cache."""
    # Pass the file object directly to load_data
    df = load_data(uploaded_file_obj)
    return df


# --- UI Rendering Functions ---
def render_header(view, player=None):
    """Renders the main dashboard header."""
    if view == "Individual Player":
        title = "Player Recovery Analysis"
        subtitle = f"Viewing: <b>{player}</b>" if player else "No Player Selected"
    else:
        title = "Team Match Readiness"
        subtitle = "Squad Planning Overview"
    st.markdown(f"""
    <div class="dashboard-header">
        <h1 class="dashboard-title">{title}</h1>
        <div class="user-info">
            <b>{datetime.now().strftime("%A, %d %B %Y")}</b><br>
            {subtitle}
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_metrics(df_filtered, risk_thresh):
    """Renders the key metric cards."""
    if df_filtered.empty:
        avg_score = np.nan; recent_avg = np.nan; days_below_threshold = 0
        risk_percent = 0; recent_days_count = 0; trend_icon = ""
    else:
        avg_score = df_filtered["emboss_baseline_score"].mean()
        recent_days_count = min(5, len(df_filtered))
        recent_avg = df_filtered.tail(recent_days_count)["emboss_baseline_score"].mean() if recent_days_count > 0 else np.nan
        days_below_threshold = (df_filtered["emboss_baseline_score"] < risk_thresh).sum()
        total_days = len(df_filtered)
        risk_percent = (days_below_threshold / total_days) * 100 if total_days > 0 else 0
        trend_val = np.nan
        if not np.isnan(recent_avg) and not np.isnan(avg_score): trend_val = recent_avg - avg_score
        trend_icon = ""
        if not np.isnan(trend_val):
            if trend_val > 0.05: trend_icon = "▲"
            elif trend_val < -0.05: trend_icon = "▼"
            else: trend_icon = "▬"
    avg_score_str = f"{avg_score:.2f}" if pd.notna(avg_score) else "N/A"
    recent_avg_str = f"{recent_avg:.2f}" if pd.notna(recent_avg) else "N/A"
    days_below_threshold_str = f"{days_below_threshold}"
    risk_percent_str = f"{risk_percent:.1f}%"
    col1, col2, col3, col4 = st.columns(4, gap="medium")
    with col1: st.markdown(f'<div class="metric-card"><div class="metric-label">Avg Score (Period)</div><div class="metric-value">{avg_score_str}</div></div>', unsafe_allow_html=True)
    with col2: st.markdown(f'<div class="metric-card"><div class="metric-label">Recent Avg ({recent_days_count}d)</div><div class="metric-value">{recent_avg_str} <span>{trend_icon}</span></div></div>', unsafe_allow_html=True)
    with col3: st.markdown(f'<div class="metric-card"><div class="metric-label">Days Below Threshold</div><div class="metric-value">{days_below_threshold_str}</div></div>', unsafe_allow_html=True)
    with col4: st.markdown(f'<div class="metric-card"><div class="metric-label">Risk Percentage</div><div class="metric-value">{risk_percent_str}</div></div>', unsafe_allow_html=True)
    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
    return days_below_threshold

def render_status_box(df_filtered, risk_thresh):
    """Displays the overall status summary box."""
    recent_data = df_filtered.sort_values('date').tail(7)
    recommendations_info = get_recommendations(recent_data, risk_thresh)
    status = recommendations_info['status']; title = recommendations_info['title']
    status_class = status; emoji, text = title.split(" ", 1) if " " in title else ("", title)
    st.markdown(f'<div class="status-box {status_class}"><div class="status-icon">{emoji}</div><div><h3>{text}</h3><small>Based on the last {min(7, len(recent_data))} days.</small></div></div>', unsafe_allow_html=True)

def render_chart_area(df_filtered, risk_thresh, show_roll_avg, roll_window, weekly_summary_df, show_weekly_tab, player):
    """Renders the main chart area."""
    st.markdown("<div class='content-block chart-area'>", unsafe_allow_html=True)
    tabs_to_show = ["Recovery Trend"]
    if show_weekly_tab and weekly_summary_df is not None and not weekly_summary_df.empty: tabs_to_show.append("Weekly Summary")
    if not tabs_to_show:
         st.info("No chart data to display."); st.markdown("</div>", unsafe_allow_html=True); return
    chart_tabs = st.tabs(tabs_to_show)
    with chart_tabs[0]:
        fig_trend = create_plotly_chart(df_filtered, risk_thresh, show_roll_avg, roll_window, player)
        st.plotly_chart(fig_trend, use_container_width=True, config={'displayModeBar': False})
    if len(chart_tabs) > 1:
        with chart_tabs[1]:
            if weekly_summary_df is not None and not weekly_summary_df.empty:
                fig_weekly = create_weekly_summary_chart(weekly_summary_df)
                st.plotly_chart(fig_weekly, use_container_width=True, config={'displayModeBar': False})
            else: st.info("Weekly summary data not available.")
    st.markdown("</div>", unsafe_allow_html=True)

def calculate_data_insights(df_filtered):
    """Calculates additional insights."""
    insights = []; n = len(df_filtered)
    if n < 3: return insights
    try:
        scores = pd.to_numeric(df_filtered['emboss_baseline_score'], errors='coerce')
        valid_scores = scores.dropna(); n_valid = len(valid_scores)
        if n_valid < 3: return insights
        df_valid = df_filtered.loc[valid_scores.index]
        if n_valid >= 3:
            best_day_idx = valid_scores.idxmax(); worst_day_idx = valid_scores.idxmin()
            best_day = df_valid.loc[best_day_idx]; worst_day = df_valid.loc[worst_day_idx]
            insights.append(f"Best day: {best_day['date'].strftime('%a, %d %b')} ({best_day['emboss_baseline_score']:.2f})")
            insights.append(f"Worst day: {worst_day['date'].strftime('%a, %d %b')} ({worst_day['emboss_baseline_score']:.2f})")
        if n_valid >= 3:
            recent_scores = df_valid.tail(min(5, n_valid))['emboss_baseline_score']
            recent_avg = recent_scores.mean(); overall_avg = valid_scores.mean()
            trend_diff = recent_avg - overall_avg
            if not np.isnan(trend_diff):
                if trend_diff > 0.07: trend_desc = f"<span style='color:{THEME['SUCCESS']}'>Improving</span>"
                elif trend_diff < -0.07: trend_desc = f"<span style='color:{THEME['ACCENT']}'>Declining</span>"
                else: trend_desc = "Stable"
                insights.append(f"Recent trend: {trend_desc} (Last {len(recent_scores)}d vs Period Avg: {trend_diff:+.2f})")
            else: insights.append("Recent trend: Not available")
        else: insights.append("Recent trend: Insufficient data")
        std_dev = valid_scores.std()
        if pd.notna(std_dev) and n_valid > 1:
            if std_dev < 0.15: consistency = "Very Consistent"
            elif std_dev < 0.25: consistency = "Consistent"
            elif std_dev < 0.35: consistency = "Variable"
            else: consistency = "Highly Variable"
            insights.append(f"Consistency: {consistency} (Std Dev: {std_dev:.2f})")
        else: insights.append("Consistency: Insufficient data")
    except Exception as e: st.error(f"Error calculating insights: {e}"); insights.append("Could not calculate some insights.")
    return insights

def render_recommendations_panel(df_filtered, risk_thresh):
    """Renders the recommendations and insights panel."""
    st.markdown("<div class='content-block info-panel'>", unsafe_allow_html=True)
    st.markdown("<h4 class='info-panel-title'>Analysis & Recommendations</h4>", unsafe_allow_html=True)
    st.markdown("<div class='info-panel-content'>", unsafe_allow_html=True)
    recent_data = df_filtered.sort_values('date').tail(7)
    rec_info = get_recommendations(recent_data, risk_thresh); status_class = rec_info['status']
    st.markdown(f"<h3 class='{status_class}'>{rec_info['title']}</h3>", unsafe_allow_html=True)
    metrics = rec_info['metrics']
    avg_str = f"{metrics['recent_avg']:.2f}" if pd.notna(metrics['recent_avg']) else "N/A"
    min_str = f"{metrics['recent_min']:.2f}" if pd.notna(metrics['recent_min']) else "N/A"
    trend_str = f"{metrics['trend']:+.2f}" if pd.notna(metrics['trend']) else "N/A"
    var_str = f"{metrics['variability']:.2f}" if pd.notna(metrics['variability']) else "N/A"
    st.markdown(f"<p class='analysis-text'><b>Analysis (Last {min(7, len(recent_data))} Days):</b> Avg: {avg_str} | Min: {min_str} | Risk Days: {metrics['below_threshold']} | Trend: {trend_str} | Variability: {var_str}</p>", unsafe_allow_html=True)
    st.markdown("<h4>Recommendations</h4>", unsafe_allow_html=True)
    if rec_info['recommendations']: st.markdown(f"<ul>{''.join([f'<li>{rec}</li>' for rec in rec_info['recommendations']])}</ul>", unsafe_allow_html=True)
    else: st.markdown("<p>No specific recommendations available.</p>", unsafe_allow_html=True)
    insights = calculate_data_insights(df_filtered)
    if insights:
        st.markdown("<hr class='insights-separator'>", unsafe_allow_html=True)
        st.markdown("<h4>Data Insights (Selected Period)</h4>", unsafe_allow_html=True)
        st.markdown(f"<ul>{''.join([f'<li>{insight}</li>' for insight in insights])}</ul>", unsafe_allow_html=True)
    st.markdown("<small><i>Note: General recommendations. Adapt based on context.</i></small>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True) # Close info-panel-content
    st.markdown("</div>", unsafe_allow_html=True) # Close info-panel

def render_footer():
    """Renders the dashboard footer."""
    st.markdown('<div class="dashboard-footer">CFC Recovery Insights Dashboard | Created by: Vivek Tiwari</div>', unsafe_allow_html=True)


# --- Main Application Logic ---

def filter_data_by_period(df_player, period_option):
    """Filters player data based on the selected time period option."""
    if df_player is None or df_player.empty: return pd.DataFrame()
    df_player = df_player.copy()
    df_player['date'] = pd.to_datetime(df_player['date'], errors='coerce')
    df_player.dropna(subset=['date'], inplace=True)
    if df_player.empty: return pd.DataFrame()
    df_player = df_player.sort_values("date")
    end_date = df_player["date"].max()
    if period_option == "All Time": start_date = df_player["date"].min()
    elif period_option == "Last 7 days": start_date = end_date - timedelta(days=6)
    elif period_option == "Last 14 days": start_date = end_date - timedelta(days=13)
    elif period_option == "Last 30 days": start_date = end_date - timedelta(days=29)
    elif period_option == "Last 90 days": start_date = end_date - timedelta(days=89)
    else: start_date = end_date - timedelta(days=29)
    if not df_player.empty:
        start_date = max(start_date, df_player["date"].min())
        filtered_df = df_player[(df_player["date"] >= start_date) & (df_player["date"] <= end_date)]
        return filtered_df
    else: return pd.DataFrame()


def render_individual_player_view(settings, df_full):
    """Renders the structured, compact view for the selected individual player."""
    render_header(settings.dashboard_view, settings.selected_player)
    if not settings.selected_player:
        st.info("Please select a player from the sidebar to view their analysis.")
        return
    if 'player_name' not in df_full.columns:
         st.error("Dataframe is missing the 'player_name' column.")
         return
    df_player_full = df_full[df_full["player_name"] == settings.selected_player]
    if df_player_full.empty:
        st.warning(f"No data found for player: {settings.selected_player}")
        df_filtered = pd.DataFrame()
    else: df_filtered = filter_data_by_period(df_player_full, settings.time_period_option)
    weekly_summary_data = None
    if settings.show_weekly_summary: weekly_summary_data = get_weekly_summary(df_filtered, settings.risk_threshold)
    
    # Render the top metric cards
    render_metrics(df_filtered, settings.risk_threshold)
    
    left_col, right_col = st.columns([3, 2], gap="medium")
    with left_col:
        render_chart_area(df_filtered, settings.risk_threshold, settings.show_rolling_avg,
                          settings.rolling_window, weekly_summary_data, settings.show_weekly_summary,
                          settings.selected_player)
    with right_col:
        if settings.show_recommendations: render_recommendations_panel(df_filtered, settings.risk_threshold)
        else:
             st.markdown("<div class='content-block info-panel'><h4 class='info-panel-title'>Analysis & Recommendations</h4><div class='info-panel-content'><p>Recovery recommendations panel is hidden via sidebar options.</p></div></div>", unsafe_allow_html=True) # Simplified placeholder

# --- App Execution ---
def main():
    """Main function to run the Streamlit app."""
    # --- Initial Data Load Attempt ---
    initial_df = None
    try:
        initial_df = pd.read_csv("cleaned_data/cleaned_CFC_Recovery_Status_Data.csv")
        initial_df["date"] = pd.to_datetime(initial_df["date"], errors='coerce')
    except FileNotFoundError:
        initial_df = generate_sample_data()
    except Exception as e:
         st.sidebar.error(f"Error loading default data: {e}")
         initial_df = generate_sample_data()

    if initial_df is None or initial_df.empty:
         st.sidebar.error("Could not load or generate initial data.")
         st.error("Fatal Error: Could not load or generate any data to proceed.")
         st.stop()

    # --- Setup Sidebar (passes initial_df for player list) ---
    settings = setup_sidebar(initial_df)

    # --- Load Data Based on Upload ---
    df_display = get_data(settings.uploaded_file) # This uses the cache

    # --- Critical Check: Ensure display data is a DataFrame ---
    if df_display is None or df_display.empty:
        st.error("❌ Data loading or generation failed after sidebar setup. Dashboard cannot proceed.")
        st.stop()
    if not isinstance(df_display, pd.DataFrame):
        st.error(f"❌ Loaded data is not a DataFrame (Type: {type(df_display)}). Cannot proceed.")
        st.stop()

    # --- Render Content ---
    if settings.dashboard_view == "Individual Player":
        render_individual_player_view(settings, df_display)
    else: # Team Readiness View
        render_header(settings.dashboard_view)
        if all(col in df_display.columns for col in ['player_name', 'date', 'emboss_baseline_score']):
             render_match_readiness_dashboard(df_display, settings.risk_threshold)
        else:
            st.error("Required columns ('player_name', 'date', 'emboss_baseline_score') missing from data for Team Readiness view.")

    render_footer()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error("An unexpected error occurred in the main execution:")
        st.exception(e)