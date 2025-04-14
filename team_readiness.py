# team_readiness.py
"""
Functions for assessing team and individual player readiness for matches,
calculating readiness scores, recommending starting lineups and bench options,
and visualizing team readiness with an enhanced UI.
Excludes players without a defined position.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
import streamlit as st
from theme import THEME, STATUS_COLORS # Import STATUS_COLORS mapping
from data_generator import SYNTHETIC_PLAYERS # Import player list for positions
import matplotlib.colors # Import for hex_to_rgb conversion

# Player position mapping (can also be loaded from a file)
PLAYER_POSITIONS = SYNTHETIC_PLAYERS # Use the map from generator

# --- Helper Functions ---
def _get_player_position(player_name):
    return PLAYER_POSITIONS.get(player_name, None)

def player_is_available(player_readiness_info):
    # Considers 'optimal' and 'ready' as fully available for starting contention
    # 'limited' and 'bench' are available but likely restricted
    return player_readiness_info.get("status") in ["optimal", "ready", "limited", "bench"]

# --- FIX: Helper function to convert hex to rgba ---
def hex_to_rgba(hex_color, alpha=0.1):
    """Converts a hex color string to an rgba string."""
    try:
        rgb = matplotlib.colors.hex2color(hex_color)
        return f'rgba({int(rgb[0]*255)}, {int(rgb[1]*255)}, {int(rgb[2]*255)}, {alpha})'
    except ValueError:
        # Fallback for invalid hex codes (e.g., from 'unknown' status)
        return 'rgba(108, 117, 125, 0.1)' # Default light grey with alpha

# --- Core Logic (calculate_player_readiness, get_squad_recommendations remain the same) ---
def calculate_player_readiness(player_data, risk_threshold):
    """
    Calculates a readiness score (0-100) and status for a single player
    based on the last 7 days of EMBOSS data.
    Factors in: latest score, recent average, trend, variability, risk days.
    Also determines potential max minutes.
    """
    player_name = player_data["player_name"].iloc[0] if not player_data.empty else "Unknown"
    position = _get_player_position(player_name)

    # Default values for insufficient data
    default_readiness = {
        "player_name": player_name, "readiness_score": 0, "recent_avg": np.nan,
        "risk_days": 0, "trend": 0, "variability": np.nan,
        "recommendation": "Insufficient Data", "status": "unknown",
        "position": position, "max_minutes": 0
    }

    if player_data is None or len(player_data) < 3: # Need at least 3 days for some basic assessment
        if player_data is not None and not player_data.empty:
             # Ensure score is numeric before calculating mean/sum
             scores = pd.to_numeric(player_data["emboss_baseline_score"], errors='coerce')
             default_readiness["recent_avg"] = scores.mean() # Will be NaN if all coerce
             default_readiness["risk_days"] = (scores < risk_threshold).sum()
        return default_readiness

    # Use last 7 days, or fewer if less data available
    recent_data = player_data.sort_values('date').tail(7).copy() # Use copy to avoid SettingWithCopyWarning

    # Ensure score is numeric
    recent_data['emboss_baseline_score'] = pd.to_numeric(recent_data['emboss_baseline_score'], errors='coerce')
    recent_data.dropna(subset=['emboss_baseline_score'], inplace=True) # Drop rows where score is not numeric

    n_days = len(recent_data)
    if n_days < 3: # Check again after dropping NaNs
         # Recalculate default if necessary after dropna
         if not recent_data.empty:
              default_readiness["recent_avg"] = recent_data["emboss_baseline_score"].mean()
              default_readiness["risk_days"] = (recent_data["emboss_baseline_score"] < risk_threshold).sum()
         return default_readiness


    # Calculate metrics
    latest_score = recent_data["emboss_baseline_score"].iloc[-1]
    recent_avg = recent_data["emboss_baseline_score"].mean()
    risk_days = (recent_data["emboss_baseline_score"] < risk_threshold).sum()

    trend = 0
    if n_days >= 4:
        first_half_avg = recent_data.iloc[:n_days//2]["emboss_baseline_score"].mean()
        second_half_avg = recent_data.iloc[n_days//2:]["emboss_baseline_score"].mean()
        if pd.notna(first_half_avg) and pd.notna(second_half_avg):
             trend = second_half_avg - first_half_avg
    elif n_days == 3: # Simple trend for 3 days
        trend = recent_data["emboss_baseline_score"].iloc[-1] - recent_data["emboss_baseline_score"].iloc[0]

    variability = recent_data["emboss_baseline_score"].std() if n_days > 1 else 0
    variability = variability if pd.notna(variability) else 0 # Handle NaN std dev for single point

    # --- Readiness Score Calculation (Weighted Factors) ---
    latest_weight = 0.40; avg_weight = 0.30; trend_weight = 0.15
    variability_penalty_factor = 40; risk_day_penalty = 6
    normalized_latest = (latest_score + 1) / 2
    normalized_avg = (recent_avg + 1) / 2
    normalized_trend = np.clip(trend + 0.5, 0, 1) # Map trend range [-0.5, 0.5] -> [0, 1] approx

    readiness_score = (latest_weight * normalized_latest * 100 + avg_weight * normalized_avg * 100 + trend_weight * normalized_trend * 100)
    variability_penalty = min(variability * variability_penalty_factor, 25)
    readiness_score -= variability_penalty; readiness_score -= risk_days * risk_day_penalty
    readiness_score = np.clip(readiness_score, 0, 100)

    # --- Determine Status and Recommendation based on Score ---
    if readiness_score >= 80: recommendation, status, max_minutes = "Start Candidate", "optimal", 90
    elif readiness_score >= 65: recommendation, status, max_minutes = "Available to Start", "ready", 90
    elif readiness_score >= 50: recommendation, status, max_minutes = "Limited Minutes (Max 60-70)", "limited", 60
    elif readiness_score >= 35: recommendation, status, max_minutes = "Bench Option (Max 30-45)", "bench", 30
    else: recommendation, status, max_minutes = "Rest / Unavailable", "rest", 0

    return {"player_name": player_name, "readiness_score": readiness_score, "recent_avg": recent_avg, "risk_days": risk_days, "trend": trend, "variability": variability, "recommendation": recommendation, "status": status, "position": position, "max_minutes": max_minutes}

def get_squad_recommendations(all_player_data, risk_threshold):
    # ... (This function remains the same as the previous version) ...
    if all_player_data is None or all_player_data.empty:
        return {"starting_xi": [], "bench": [], "unavailable": [], "positions_covered_on_bench": {}, "improving_count": 0, "declining_count": 0, "status_counts": {}}

    player_groups = all_player_data.groupby("player_name")
    player_readiness = []
    for _, group in player_groups:
        player_readiness.append(calculate_player_readiness(group, risk_threshold))

    # Filter for selectable players (must have a position and not be 'Rest')
    valid_positions = {'GK', 'DEF', 'MID', 'FWD'}
    selectable_players = [
        p for p in player_readiness
        if player_is_available(p) and p.get("position") in valid_positions
    ]
    # Identify players excluded from selection (Rest status, unknown status, no position)
    excluded_players = [
        p for p in player_readiness
        if not (player_is_available(p) and p.get("position") in valid_positions)
    ]

    # Sort selectable players by readiness score (highest first)
    selectable_players.sort(key=lambda x: x["readiness_score"], reverse=True)

    # --- Squad Selection Logic ---
    target_counts = {"GK": 1, "DEF": 4, "MID": 3, "FWD": 3}
    starting_xi = []
    bench = []
    remaining_selectable = selectable_players.copy()

    # 1. Fill positional quotas for starting XI
    for position, target_num in target_counts.items():
        selected_count = 0
        players_in_pos = [p for p in remaining_selectable if p["position"] == position]
        players_in_pos.sort(key=lambda x: x["readiness_score"], reverse=True)
        for player in players_in_pos:
            if selected_count < target_num:
                starting_xi.append(player)
                remaining_selectable.remove(player)
                selected_count += 1
            else:
                break

    # 2. Fill remaining XI spots (up to 11)
    while len(starting_xi) < 11 and remaining_selectable:
        starting_xi.append(remaining_selectable.pop(0))

    # 3. Fill bench spots (up to 7)
    while len(bench) < 7 and remaining_selectable:
        bench.append(remaining_selectable.pop(0))

    # 4. Any players left are added to unavailable
    excluded_players.extend(remaining_selectable)

    # Sort final lists for display
    position_order = {"GK": 0, "DEF": 1, "MID": 2, "FWD": 3}
    starting_xi.sort(key=lambda x: (position_order.get(x["position"], 99), -x["readiness_score"]))
    bench.sort(key=lambda x: (-x["readiness_score"]))
    excluded_players.sort(key=lambda x: x["readiness_score"], reverse=True)

    # Calculate summary stats
    positions_on_bench = {p["position"] for p in bench if p.get("position")}
    positions_covered = {pos: pos in positions_on_bench for pos in valid_positions}
    improving_count = sum(1 for p in player_readiness if p.get("trend", 0) > 0.05 and p.get("status") != "unknown")
    declining_count = sum(1 for p in player_readiness if p.get("trend", 0) < -0.05 and p.get("status") != "unknown")
    status_counts = {status: 0 for status in STATUS_COLORS.keys()}
    all_considered_players = starting_xi + bench + excluded_players
    for p in all_considered_players:
        status = p.get("status", "unknown")
        status_counts[status] = status_counts.get(status, 0) + 1

    return {"starting_xi": starting_xi, "bench": bench, "unavailable": excluded_players, "positions_covered_on_bench": positions_covered, "improving_count": improving_count, "declining_count": declining_count, "status_counts": status_counts}


# --- Visualization ---
def create_team_readiness_chart(player_readiness_data):
    """
    Creates a horizontal bar chart showing readiness scores for all players.
    """
    if not player_readiness_data:
        fig = go.Figure()
        fig.add_annotation(text="No player readiness data to display.", showarrow=False)
        return fig

    sorted_data = sorted(player_readiness_data, key=lambda x: x["readiness_score"])

    player_labels = []; hover_texts = []
    for p in sorted_data:
        pos_str = f"({p.get('position', 'N/A')})" if p.get('position') else ""
        player_labels.append(f"{p['player_name']} {pos_str}".strip())
        pos_display = p.get('position', 'N/A')
        status_display = p.get('status', 'unknown').replace("_", " ").capitalize()
        if p.get('status') == 'unknown' and pos_display == 'N/A': status_display = "Excluded (Missing Position/Data)"
        elif p.get('status') == 'unknown': status_display = "Insufficient Data"
        hover_texts.append(f"<b>{p['player_name']}</b> ({pos_display})<br>Readiness: {p['readiness_score']:.1f}% ({status_display})<br>Recommendation: {p.get('recommendation', 'N/A')}<br>Recent Avg: {p.get('recent_avg', 0):.2f}, Trend: {p.get('trend', 0):+.2f}<br>Risk Days (last 7): {p.get('risk_days', 0)}, Variability: {p.get('variability', 0):.2f}")

    readiness_scores = [p["readiness_score"] for p in sorted_data]
    colors = [STATUS_COLORS.get(p.get("status", "unknown"), THEME['TEXT_LIGHT']) for p in sorted_data]

    fig = go.Figure()
    fig.add_trace(go.Bar(y=player_labels, x=readiness_scores, orientation='h', marker=dict(color=colors, line=dict(color='rgba(0,0,0,0.1)', width=0.5)), text=[f"{score:.0f}%" for score in readiness_scores], textposition='outside', hoverinfo='text', hovertext=hover_texts))

    # Define readiness zones
    # --- FIX: Use hex_to_rgba for fillcolor ---
    zone_alpha = 0.12 # Define alpha for zones
    readiness_zones = [
        {"min": 0, "max": 35, "color": hex_to_rgba(STATUS_COLORS['rest'], zone_alpha), "label": "Rest"},
        {"min": 35, "max": 50, "color": hex_to_rgba(STATUS_COLORS['bench'], zone_alpha), "label": "Bench"},
        {"min": 50, "max": 65, "color": hex_to_rgba(STATUS_COLORS['limited'], zone_alpha), "label": "Limited"},
        {"min": 65, "max": 80, "color": hex_to_rgba(STATUS_COLORS['ready'], zone_alpha), "label": "Ready"},
        {"min": 80, "max": 105, "color": hex_to_rgba(STATUS_COLORS['optimal'], zone_alpha), "label": "Optimal"}
    ]
    # --- END FIX ---

    shapes = []; annotations = []; num_players = len(player_labels)
    for zone in readiness_zones:
        shapes.append(go.layout.Shape(type="rect", xref="x", yref="paper", x0=zone["min"], x1=zone["max"], y0=0, y1=1, fillcolor=zone["color"], line_width=0, layer="below"))
        annotations.append(go.layout.Annotation(x=(zone["min"] + zone["max"]) / 2, y=1.02, xref="x", yref="paper", text=zone["label"], showarrow=False, font=dict(size=9, color="grey"), opacity=0.9))

    fig.update_layout(title="Team Readiness Overview", title_x=0.05, xaxis=dict(title="Calculated Readiness Score (%)", range=[0, 105], showgrid=True, gridcolor='rgba(220,220,220,0.5)'), yaxis=dict(title=None, showticklabels=True, tickfont=dict(size=10)), height=max(400, num_players * 23), margin=dict(l=150, r=40, t=80, b=50), template="plotly_white", plot_bgcolor=THEME['CARD'], paper_bgcolor=THEME['CARD'], shapes=shapes, annotations=annotations, hoverlabel=dict(bgcolor="white", font_size=12))
    return fig


# --- Player Card Renderer (_render_player_card_v2 remains the same) ---
def _render_player_card_v2(player, card_context='bench'):
    """
    Helper function to render the new enhanced HTML player card.
    Displays Position for 'starting' context, Status Badge otherwise.
    """
    readiness = player.get("readiness_score", 0)
    player_name = player.get("player_name", "N/A")
    status = player.get("status", "unknown")
    trend = player.get("trend", 0)
    position = player.get("position", "N/A")

    # Determine Trend Icon
    if trend > 0.05: trend_icon = "▲" # Improving
    elif trend < -0.05: trend_icon = "▼" # Declining
    else: trend_icon = "▬" # Stable

    # Decide tag content based on context
    status_text = status.replace("_", " ").capitalize()
    if card_context == 'starting':
        tag_content = f'<span class="player-tag player-position-text">{position}</span>'
    else:
        tag_content = f'<span class="player-tag player-status-badge">{status_text}</span>'

    status_class = status # CSS class based on actual status for coloring score/border

    # Tooltip adjustments
    tooltip_status_display = status_text
    if status == 'unknown' and position == 'N/A' and card_context == 'unavailable':
         tooltip_status_display = "Excluded (Missing Position/Data)"
    elif status == 'unknown' and card_context == 'unavailable':
         tooltip_status_display = "Insufficient Data"


    tooltip = (
        f"Position: {position}\n"
        f"Status: {tooltip_status_display}\n"
        f"Recommendation: {player.get('recommendation', 'N/A')}\n"
        f"Max Mins: {player.get('max_minutes', 'N/A')}\n"
        f"Readiness Score: {readiness:.1f}%\n"
        f"Recent Avg: {player.get('recent_avg', 0):.2f}\n"
        f"Trend: {trend:+.2f} ({trend_icon})\n"
        f"Variability: {player.get('variability', 0):.2f}\n"
        f"Risk Days (last 7): {player.get('risk_days', 0)}"
        )

    return f"""
    <div class="player-card-v2 {status_class}" title="{tooltip}">
        <div class="player-info">
            <span class="player-name">{player_name}</span>
            {tag_content}
        </div>
        <div class="player-readiness">
            <span class="readiness-score">{readiness:.0f}%</span>
            <span class="trend-icon">{trend_icon}</span>
        </div>
    </div>
    """

# --- Main Rendering Function (render_match_readiness_dashboard remains the same) ---
def render_match_readiness_dashboard(all_player_data, risk_threshold):
    """
    Render the overhauled Match Readiness dashboard view in Streamlit.
    Features summary stats, positional XI layout, tabs for bench/unavailable,
    and the overview chart.
    """
    # Sidebar Info (Expander)
    with st.sidebar:
         with st.expander("📊 How Readiness is Calculated", expanded=False):
            st.markdown("""
            Combines multiple factors from the **last 7 days**:
            - **Latest Score** (Weight: ~40%)
            - **Recent Average** (Weight: ~30%)
            - **Score Trend** (Weight: ~15%)
            - **Variability Penalty** (Higher inconsistency reduces score)
            - **Risk Day Penalty** (Days below threshold reduce score)
            """)
         with st.expander("🚦 Readiness Categories", expanded=False):
            st.markdown("""
            - **Optimal (80+)**: Start Candidate (90 min)
            - **Ready (65-79)**: Available to Start (90 min)
            - **Limited (50-64)**: Reduced Mins (~60 min)
            - **Bench (35-49)**: Bench Option (~30 min)
            - **Rest (<35)**: Rest / Unavailable (0 min)
            """)
         st.info("Squad selection prioritizes readiness within defined positions (GK, DEF, MID, FWD). Players without a position or with 'Rest'/'Unknown' status are excluded from XI/Bench contention.")

    # --- Main Dashboard Area ---
    st.markdown("## Match Day Squad Planner")
    st.caption(f"Assessment based on data up to {all_player_data['date'].max().strftime('%d %b %Y')} | Risk Threshold: {risk_threshold:.2f}")

    squad_recommendations = get_squad_recommendations(all_player_data, risk_threshold)

    # --- 1. Top Summary Metrics ---
    st.markdown("#### Squad Readiness Summary")
    xi = squad_recommendations["starting_xi"]
    bench = squad_recommendations["bench"]
    unavailable = squad_recommendations["unavailable"]
    status_counts = squad_recommendations["status_counts"]
    total_players = len(xi) + len(bench) + len(unavailable)
    available_count = len(xi) + len(bench)
    xi_avg = np.mean([p["readiness_score"] for p in xi]) if xi else 0

    cols_summary = st.columns(6)
    with cols_summary[0]: st.markdown(f'<div class="summary-box"><div class="summary-box-label">Total Evaluated</div><div class="summary-box-value">{total_players}</div></div>', unsafe_allow_html=True)
    with cols_summary[1]: st.markdown(f'<div class="summary-box"><div class="summary-box-label">Available Players</div><div class="summary-box-value">{available_count}</div></div>', unsafe_allow_html=True)
    with cols_summary[2]: st.markdown(f'<div class="summary-box"><div class="summary-box-label">XI Avg Readiness</div><div class="summary-box-value">{xi_avg:.0f}<span class="unit" style="font-size:0.6em; color: {THEME["TEXT_LIGHT"]};">%</span></div></div>', unsafe_allow_html=True) # Added unit span
    status_order = ["optimal", "ready", "limited", "bench", "rest", "unknown"]
    status_cols_map = {0:3, 1:4, 2:5}
    for i, status in enumerate(status_order):
         count = status_counts.get(status, 0)
         col_index = status_cols_map.get(i)
         if col_index is not None:
             with cols_summary[col_index]: st.markdown(f'<div class="summary-box {status}"><div class="summary-box-label">{status.replace("_"," ").capitalize()}</div><div class="summary-box-value">{count}</div></div>', unsafe_allow_html=True)
    st.markdown("<hr style='margin: 15px 0 25px 0;'>", unsafe_allow_html=True)

    # --- 2. Recommended Starting XI ---
    st.markdown("#### Recommended Starting XI")
    xi_positions = {"GK": [], "DEF": [], "MID": [], "FWD": []}
    for player in xi:
        pos = player.get("position")
        if pos in xi_positions: xi_positions[pos].append(player)
    col_widths = [1.5, 3, 2.5, 3]; cols_xi = st.columns(col_widths, gap="medium")
    pos_map = {"GK": 0, "DEF": 1, "MID": 2, "FWD": 3}
    for pos_name, col_index in pos_map.items():
        with cols_xi[col_index]:
            st.markdown(f"<h5 style='margin-bottom: 8px; text-transform: uppercase; color: {THEME['TEXT_LIGHT']}; font-size: 0.9em; letter-spacing: 0.5px;'>{pos_name}</h5>", unsafe_allow_html=True) # Styled position title
            players_in_pos = sorted(xi_positions.get(pos_name, []), key=lambda p: p['readiness_score'], reverse=True)
            if players_in_pos:
                for player in players_in_pos: st.markdown(_render_player_card_v2(player, card_context='starting'), unsafe_allow_html=True)
            else: st.caption("(None selected)")
    st.markdown("<hr style='margin: 25px 0;'>", unsafe_allow_html=True)

    # --- 3. Bench & Unavailable in Tabs ---
    st.markdown("#### Substitutes & Unavailable Players")
    tab1_title = f"Bench ({len(bench)})"; tab2_title = f"Unavailable / Not Selected ({len(unavailable)})"
    tab1, tab2 = st.tabs([tab1_title, tab2_title])
    with tab1: # Bench Tab
        if bench:
            num_bench_cols = 4; bench_cols = st.columns(num_bench_cols)
            for i, player in enumerate(bench):
                with bench_cols[i % num_bench_cols]: st.markdown(_render_player_card_v2(player, card_context='bench'), unsafe_allow_html=True)
        else: st.info("No players recommended for the bench.")
    with tab2: # Unavailable Tab
        if unavailable:
             st.caption("Includes players for rest, insufficient data, missing position, or not selected due to lower readiness.")
             num_unav_cols = 4; unav_cols = st.columns(num_unav_cols)
             for i, player in enumerate(unavailable):
                 with unav_cols[i % num_unav_cols]: st.markdown(_render_player_card_v2(player, card_context='unavailable'), unsafe_allow_html=True)
        else: st.success("All evaluated players are available and included in XI or Bench.")

    # --- 4. Team Readiness Overview Chart ---
    st.markdown("<hr style='margin: 30px 0 15px 0;'>", unsafe_allow_html=True)
    st.markdown("#### Full Squad Readiness Chart")
    all_players_list = xi + bench + unavailable
    if all_players_list:
        chart_data = sorted(all_players_list, key=lambda x: x['readiness_score'], reverse=False)
        readiness_chart = create_team_readiness_chart(chart_data)
        st.plotly_chart(readiness_chart, use_container_width=True)
        st.caption("Horizontal bar chart showing calculated readiness for all evaluated players. Colors indicate status.")
    else: st.warning("No player data found.")