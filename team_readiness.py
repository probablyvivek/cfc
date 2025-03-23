"""
Functions for assessing team readiness and generating match-day squad recommendations.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from theme import THEME

# Player position mapping for team selection
PLAYER_POSITIONS = {
    "Robert Sanchez":"GK", 
    "Filip Jörgensen":"GK",
    "Reece James": "DEF",
    "Malo Gusto": "DEF",
    "Wesley Fofana": "DEF",
    "Trevoh Chalobah": "DEF",
    "Levi Colwill": "DEF",
    "Benoit Badiashile": "DEF",
    "Marc Cucurella": "DEF",
    "Josh Acheampong": "DEF",
    "Enzo Fernandez": "MID",
    "Moises Caicedo": "MID",
    "Romeo Lavia": "MID",
    "Kiernan Dewsbury-Hall": "MID",
    "Cole Palmer": "FWD",
    "Noni Madueke": "FWD",
    "Pedro Neto": "FWD",
    "Tyrique George": "FWD",
    "Nicolas Jackson": "FWD",
    "Christopher Nkunku": "FWD"
}

# Helper function to check if a player is available for selection
def player_is_available(player):
    """
    Check if a player is available for selection based on readiness or status
    
    Parameters:
    player (dict): Player data dictionary
    
    Returns:
    bool: True if player is available, False otherwise
    """
    # If max_minutes is available, use it
    if "max_minutes" in player:
        return player["max_minutes"] > 0
    
    # Otherwise use status
    if "status" in player:
        return player["status"] != "rest"
    
    # Fallback to readiness score
    return player["readiness_score"] >= 30  # Same threshold as "bench" status

def calculate_player_readiness(player_data, risk_threshold, match_date=None):
    """
    Calculate player's match readiness based on recent recovery data
    
    Parameters:
    player_data (DataFrame): Player's recovery data
    risk_threshold (float): Threshold for risk determination
    match_date (datetime): The date of upcoming match, defaults to tomorrow
    
    Returns:
    dict: Player readiness metrics and recommendation
    """
    if match_date is None:
        # Default to tomorrow as match day
        match_date = datetime.now().date() + timedelta(days=1)
    elif isinstance(match_date, str):
        match_date = datetime.strptime(match_date, "%Y-%m-%d").date()
    
    # Get most recent 7 days of data
    recent_data = player_data.tail(7)
    
    if len(recent_data) == 0:
        return {
            "player_name": player_data["player_name"].iloc[0] if len(player_data) > 0 else "Unknown",
            "readiness_score": 0,
            "recent_avg": 0,
            "risk_days": 0,
            "trend": 0,
            "recommendation": "Insufficient Data",
            "status": "unknown",
            "max_minutes": 0,
            "position": PLAYER_POSITIONS.get(player_data["player_name"].iloc[0] if len(player_data) > 0 else "Unknown", "Unassigned")
        }
    
    # Calculate key metrics
    recent_avg = recent_data["emboss_baseline_score"].mean()
    latest_score = recent_data["emboss_baseline_score"].iloc[-1]
    risk_days = (recent_data["emboss_baseline_score"] < risk_threshold).sum()
    
    # Calculate trend (first half vs second half of recent days)
    if len(recent_data) >= 4:
        first_half = recent_data.iloc[:len(recent_data)//2]["emboss_baseline_score"].mean()
        second_half = recent_data.iloc[len(recent_data)//2:]["emboss_baseline_score"].mean()
        trend = second_half - first_half
    else:
        trend = 0
    
    # Calculate variability (as a physiological marker of recovery instability)
    variability = recent_data["emboss_baseline_score"].std() if len(recent_data) > 1 else 0
    
    # Calculate weighted readiness score (0-100)
    latest_weight = 0.4
    avg_weight = 0.3
    trend_weight = 0.2
    variability_penalty = 0.1
    
    # Normalize scores from [-1,1] to [0,1]
    normalized_latest = (latest_score + 1) / 2
    normalized_avg = (recent_avg + 1) / 2
    normalized_trend = (trend + 1) / 2 if trend > -1 else 0
    
    # Risk days penalty (each risk day reduces score, more recent days have stronger impact)
    risk_penalty = 0
    for i, row in recent_data.iterrows():
        days_ago = (recent_data.iloc[-1]["date"].date() - row["date"].date()).days
        if row["emboss_baseline_score"] < risk_threshold:
            # Exponential decay - more recent risk days have stronger impact
            risk_penalty += 0.1 * (0.7 ** days_ago)
    
    # Variability penalty (high variability indicates inconsistent recovery)
    variability_factor = min(1, variability * 2)  # Cap at 1
    
    # Calculate final readiness score (0-100 scale)
    readiness_score = (
        latest_weight * normalized_latest +
        avg_weight * normalized_avg +
        trend_weight * normalized_trend
    ) * 100
    
    # Apply penalties
    readiness_score = max(0, readiness_score - (risk_penalty * 20) - (variability_factor * 10))
    
    # Determine recommendation and max minutes
    if readiness_score >= 75:
        recommendation = "Full Training & Match"
        status = "optimal"
        max_minutes = 90
    elif readiness_score >= 60:
        recommendation = "Full Match"
        status = "ready"
        max_minutes = 90
    elif readiness_score >= 45:
        recommendation = "Limited Minutes (60-70)"
        status = "limited"
        max_minutes = 60
    elif readiness_score >= 30:
        recommendation = "Bench Option"
        status = "bench"
        max_minutes = 30
    else:
        recommendation = "Rest/Recovery"
        status = "rest"
        max_minutes = 0
    
    # Get player name safely
    player_name = player_data["player_name"].iloc[0]
    
    return {
        "player_name": player_name,
        "readiness_score": readiness_score,
        "recent_avg": recent_avg,
        "risk_days": risk_days,
        "trend": trend,
        "recommendation": recommendation,
        "status": status,
        "position": PLAYER_POSITIONS.get(player_name, "Unassigned"),
        "max_minutes": max_minutes
    }

def get_squad_recommendations(all_player_data, risk_threshold, match_date=None):
    """
    Generate recommended starting lineup based on player readiness
    
    Parameters:
    all_player_data (DataFrame): Recovery data for all players
    risk_threshold (float): Threshold for determining risk
    match_date (datetime): Date of the upcoming match
    
    Returns:
    dict: Recommended lineup with starting XI and bench options
    """
    # Group data by player
    player_groups = all_player_data.groupby("player_name")
    
    # Calculate readiness for each player
    player_readiness = []
    for player_name, group in player_groups:
        readiness = calculate_player_readiness(group, risk_threshold, match_date)
        player_readiness.append(readiness)
    
    # Sort by readiness score (descending)
    player_readiness.sort(key=lambda x: x["readiness_score"], reverse=True)
    
    # Group players by position
    position_groups = {"GK": [], "DEF": [], "MID": [], "FWD": [], "Unassigned": []}
    
    for player in player_readiness:
        position = player["position"]
        # Make sure position is one of our known categories
        if position not in position_groups:
            # If position is unknown, categorize as "Unassigned"
            position = "Unassigned"
            player["position"] = position
        
        position_groups[position].append(player)
    
    # Start with the best goalkeeper
    starting_xi = []
    bench = []
    
    # Add goalkeeper
    if position_groups["GK"]:
        starting_xi.append(position_groups["GK"][0])
        # Any other GKs go to bench
        for gk in position_groups["GK"][1:]:
            if len(bench) < 7 and player_is_available(gk):
                bench.append(gk)
    
    # Select 4 defenders with highest readiness
    defender_count = min(4, len(position_groups["DEF"]))
    for defender in position_groups["DEF"][:defender_count]:
        if player_is_available(defender):
            starting_xi.append(defender)
    
    # Add other defenders to bench
    for defender in position_groups["DEF"][defender_count:]:
        if len(bench) < 7 and player_is_available(defender):
            bench.append(defender)
    
    # Select 3-4 midfielders with highest readiness
    mid_count = min(4, len(position_groups["MID"]))
    for midfielder in position_groups["MID"][:mid_count]:
        if player_is_available(midfielder):
            starting_xi.append(midfielder)
    
    # Add other midfielders to bench
    for midfielder in position_groups["MID"][mid_count:]:
        if len(bench) < 7 and player_is_available(midfielder):
            bench.append(midfielder)
    
    # Select 2-3 forwards with highest readiness
    # If we don't have enough starting XI players yet, add more forwards
    fwd_count = min(3, len(position_groups["FWD"]))
    for forward in position_groups["FWD"][:fwd_count]:
        if player_is_available(forward):
            starting_xi.append(forward)
    
    # Add other forwards to bench
    for forward in position_groups["FWD"][fwd_count:]:
        if len(bench) < 7 and player_is_available(forward):
            bench.append(forward)
    
    # Handle unassigned players based on readiness
    # First add to starting XI if needed
    unassigned_index = 0
    while len(starting_xi) < 11 and unassigned_index < len(position_groups["Unassigned"]):
        player = position_groups["Unassigned"][unassigned_index]
        if player_is_available(player):
            starting_xi.append(player)
        unassigned_index += 1
    
    # Then add to bench if needed
    while len(bench) < 7 and unassigned_index < len(position_groups["Unassigned"]):
        player = position_groups["Unassigned"][unassigned_index]
        if player_is_available(player):
            bench.append(player)
        unassigned_index += 1
    
    # Ensure we have 11 starting players:
    # If we have less than 11, add more players from the bench
    while len(starting_xi) < 11 and bench:
        starting_xi.append(bench.pop(0))
        
    # If we have more than 11, move excess to bench
    while len(starting_xi) > 11:
        # Find lowest readiness player and move to bench
        starting_xi.sort(key=lambda x: x["readiness_score"])
        player_to_bench = starting_xi.pop(0)
        if len(bench) < 7:
            bench.append(player_to_bench)
    
    # Sort starting XI by position for display
    position_order = {"GK": 0, "DEF": 1, "MID": 2, "FWD": 3, "Unassigned": 4}
    starting_xi.sort(key=lambda x: position_order.get(x["position"], 4))
    
    # Find unavailable players
    all_selected_players = starting_xi + bench
    unavailable = []
    
    for player in player_readiness:
        if player not in all_selected_players:
            unavailable.append(player)
    
    # Check for tactical position coverage on bench (safely)
    try:
        positions_covered = {
            "GK": any(p["position"] == "GK" for p in bench),
            "DEF": any(p["position"] == "DEF" for p in bench),
            "MID": any(p["position"] == "MID" for p in bench),
            "FWD": any(p["position"] == "FWD" for p in bench)
        }
    except:
        positions_covered = {
            "GK": False,
            "DEF": False,
            "MID": False,
            "FWD": False
        }
    
    # Calculate team-level stats
    improving_count = sum(1 for p in player_readiness if p["trend"] > 0)
    declining_count = sum(1 for p in player_readiness if p["trend"] < 0)
    
    return {
        "starting_xi": starting_xi,
        "bench": bench,
        "unavailable": unavailable,
        "positions_covered": positions_covered,
        "improving_count": improving_count,
        "declining_count": declining_count
    }

def create_team_readiness_chart(player_readiness_data):
    """
    Create a horizontal bar chart showing player readiness for match day
    
    Parameters:
    player_readiness_data (list): List of player readiness dictionaries
    
    Returns:
    plotly.graph_objects.Figure: Plotly figure object
    """
    # Sort players by readiness score
    sorted_data = sorted(player_readiness_data, key=lambda x: x["readiness_score"], reverse=True)
    
    # Extract player names and scores
    player_names = [f"{p['player_name']} ({p['position']})" if 'position' in p else p['player_name'] 
                   for p in sorted_data]
    readiness_scores = [p["readiness_score"] for p in sorted_data]
    
    # Define color scheme based on readiness status
    colors = []
    for player in sorted_data:
        if player["status"] == "optimal":
            colors.append(THEME["SUCCESS"])
        elif player["status"] == "ready":
            colors.append("#88C054")  # Light green
        elif player["status"] == "limited":
            colors.append(THEME["WARNING"])
        elif player["status"] == "bench":
            colors.append("#E67E39")  # Orange
        else:
            colors.append(THEME["ACCENT"])  # Red for rest/unavailable
    
    # Create horizontal bar chart
    fig = go.Figure()
    
    # Add bars
    fig.add_trace(go.Bar(
        y=player_names,
        x=readiness_scores,
        orientation='h',
        marker=dict(
            color=colors,
            line=dict(color='rgba(0,0,0,0.4)', width=1)
        ),
        text=[f"{score:.1f}%" for score in readiness_scores],
        textposition='outside',
        hovertemplate=(
            "<b>%{y}</b><br>" +
            "Readiness: %{x:.1f}%<br>" +
            "<extra></extra>"
        )
    ))
    
    # Update layout
    fig.update_layout(
        title="Match Day Readiness Assessment",
        xaxis=dict(
            title="Readiness Score (%)",
            range=[0, 105],  # Add some space for labels
            showgrid=True,
            gridcolor='rgba(220,220,220,0.8)'
        ),
        yaxis=dict(
            title=None,
            autorange="reversed"  # To have highest scores at the top
        ),
        height=max(500, len(player_names) * 30),  # Adjust height based on number of players
        margin=dict(l=10, r=10, t=60, b=50),
        template="plotly_white"
    )
    
    # Add colored regions for different readiness levels
    readiness_levels = [
        {"range": [0, 30], "color": "rgba(230,57,70,0.1)", "label": "Rest"},
        {"range": [30, 45], "color": "rgba(230,126,57,0.1)", "label": "Bench"},
        {"range": [45, 60], "color": "rgba(244,162,97,0.1)", "label": "Limited"},
        {"range": [60, 75], "color": "rgba(136,192,84,0.1)", "label": "Ready"},
        {"range": [75, 100], "color": "rgba(42,157,143,0.1)", "label": "Optimal"}
    ]
    
    # Add shapes and annotations for readiness levels
    for level in readiness_levels:
        # Add shaded rectangle
        fig.add_shape(
            type="rect",
            x0=level["range"][0],
            x1=level["range"][1],
            y0=-0.5,
            y1=len(player_names) - 0.5,
            fillcolor=level["color"],
            line_width=0,
            layer="below"
        )
        
        # Add text annotation at the top
        fig.add_annotation(
            x=(level["range"][0] + level["range"][1]) / 2,
            y=len(player_names) + 0.5,
            text=level["label"],
            showarrow=False,
            font=dict(size=10),
            opacity=0.7
        )
    
    return fig

def render_match_readiness_dashboard(all_player_data, risk_threshold):
    """
    Render the match readiness dashboard section
    
    Parameters:
    all_player_data (DataFrame): Recovery data for all players
    risk_threshold (float): Threshold for determining risk
    """
    # Add explanation text to the sidebar
    with st.sidebar:
        st.markdown("## How It Works:")
        st.markdown("""
        ✅ **Recovery Data Analysis**: The system analyzes each player's recovery trends over the past 7 days.
        
        📊 **Readiness Score Calculation**: A composite readiness score (0-100%) is calculated based on:
        * Recent EMBOSS score average
        * Most recent score
        * Recovery trend (improving/declining)
        * Score stability/variability
        * Days below risk threshold
        
        🏟️ **Match Day Selection**: The system recommends an optimal starting XI and bench options based on physiological readiness.
        """)
    
    # Add legends on the right side using an expander
    with st.expander("**Readiness Categories:**", expanded=True):
        st.markdown("""
        * **75-100%**: Optimal - Full Training & Match
        * **60-75%**: Ready - Full Match
        * **45-60%**: Limited - Reduced Minutes (60-70)
        * **30-45%**: Bench Option - Limited Impact Sub
        * **Below 40%**: Rest/Recovery Required
        """)
    
    st.markdown("## Match Day Readiness Assessment")
    
    # Dashboard controls - simplified to only show match date
    # Match date selection (default to tomorrow)
    tomorrow = datetime.now().date() + timedelta(days=1)
    match_date = st.date_input(
        "Match Date", 
        value=tomorrow,
        min_value=datetime.now().date(),
        max_value=datetime.now().date() + timedelta(days=14)
    )
    
    # Generate squad recommendations using risk_threshold from sidebar
    squad_recommendations = get_squad_recommendations(
        all_player_data,
        risk_threshold,
        match_date
    )
    
    # Display starting XI and bench in a visually appealing way
    st.markdown("### Recommended Starting XI Based on Physiological Readiness")
    
    # Create position groups for display
    position_groups = {"GK": [], "DEF": [], "MID": [], "FWD": []}
    
    # Group players by position
    for player in squad_recommendations["starting_xi"]:
        position = player.get("position", "Unassigned")
        if position in position_groups:
            position_groups[position].append(player)
    
    # Display each position group
    col1, col2, col3, col4 = st.columns(4)
    
    positions = [
        ("GK", col1, "#3366FF"),  # Blue for GK
        ("DEF", col2, "#3366FF"),  # Blue for DEF
        ("MID", col3, "#3366FF"),  # Blue for MID
        ("FWD", col4, "#3366FF")   # Blue for FWD
    ]
    
    for position, col, color in positions:
        with col:
            st.markdown(f"#### {position}")
            for player in position_groups[position]:
                readiness = player["readiness_score"]
                status_color = (
                    THEME["SUCCESS"] if readiness >= 85 else
                    "#88C054" if readiness >= 70 else
                    THEME["WARNING"] if readiness >= 55 else
                    "#E67E39" if readiness >= 40 else
                    THEME["ACCENT"]
                )
                
                st.markdown(
                    f"""
                    <div style="
                        position: relative;
                        background-color: rgba(230, 240, 255, 1);
                        padding: 8px 12px;
                        padding-left: 16px;
                        margin-bottom: 8px;
                        border-radius: 4px;
                        text-align: left;
                        overflow: hidden;
                    ">
                        <div style="
                            position: absolute;
                            top: 0;
                            left: 0;
                            width: 6px;
                            height: 100%;
                            background-color: {color};
                        "></div>
                        <div style="font-weight: bold; font-size: 16px; text-align: left; margin-bottom: 5px;">
                            {player["player_name"]}
                        </div>
                        <div style="text-align: right;">
                            <div style="color: #3366FF; font-weight: 500; font-size: 16px;">
                                {readiness:.1f}%
                            </div>
                        </div>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
    
    # Display bench options
    st.markdown("### Bench Options")
    bench_cols = st.columns(7)
    
    for i, player in enumerate(squad_recommendations["bench"]):
        with bench_cols[i % 7]:
            readiness = player["readiness_score"]
            status_color = (
                THEME["SUCCESS"] if readiness >= 85 else
                "#88C054" if readiness >= 70 else
                THEME["WARNING"] if readiness >= 55 else
                "#E67E39" if readiness >= 40 else
                THEME["ACCENT"]
            )
            
            st.markdown(
                f"""
                <div style="
                    position: relative;
                    background-color: rgba(245, 245, 224, 5);
                    padding: 8px 12px;
                    padding-left: 16px;
                    margin-bottom: 8px;
                    border-radius: 4px;
                    text-align: left;
                    overflow: hidden;
                ">
                    <div style="
                        position: absolute;
                        top: 0;
                        left: 0;
                        width: 6px;
                        height: 100%;
                        background-color: #F4A261;
                    "></div>
                    <div style="font-weight: bold; font-size: 16px;">
                        {player["player_name"]}
                    </div>
                    <div style="text-align: right;">
                    <div style="color: #F4A261; font-weight: 500; font-size: 16px;">
                        {readiness:.1f}%
                    </div>
                </div>
                """, 
                unsafe_allow_html=True
            )
    
    # Display unavailable players (if any)
    if len(squad_recommendations["unavailable"]) > 0:
        st.markdown("### Fatigued Players")
        unavailable_cols = st.columns(7)
        
        for i, player in enumerate(squad_recommendations["unavailable"]):
            with unavailable_cols[i % 7]:
                st.markdown(
                    f"""
                    <div style="
                        position: relative;
                        background-color: rgba(255, 235, 235, 1);
                        padding: 8px 12px;
                        padding-left: 16px;
                        margin-bottom: 8px;
                        border-radius: 4px;
                        text-align: left;
                        overflow: hidden;
                    ">
                        <div style="
                            position: absolute;
                            top: 0;
                            left: 0;
                            width: 6px;
                            height: 100%;
                            background-color: {THEME["ACCENT"]};
                        "></div>
                        <div style="font-weight: bold; font-size: 16px;">
                            {player["player_name"]}
                        </div>
                        <div style="text-align: right;">
                        <div style="color: #E63A46; font-weight: 500; font-size: 16px;">
                            {player["readiness_score"]:.1f}%
                        </div>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
    

    st.markdown("<br><br>", unsafe_allow_html=True)  # Adds two line breaks for spacing
    # Show overall team readiness chart
    st.markdown("### Team Readiness Overview")
    
    # Combine all players for the chart
    all_players = (
        squad_recommendations["starting_xi"] + 
        squad_recommendations["bench"] + 
        squad_recommendations["unavailable"]
    )
    
    # Create and display the chart
    readiness_chart = create_team_readiness_chart(all_players)
    st.plotly_chart(readiness_chart, use_container_width=True)
    
    # Add team readiness metrics
    st.markdown("### Team Readiness Metrics")
    
    # Calculate average readiness for starting XI
    starting_xi_avg = sum(p["readiness_score"] for p in squad_recommendations["starting_xi"]) / len(squad_recommendations["starting_xi"]) if squad_recommendations["starting_xi"] else 0
    
    # Count players in each readiness category
    optimal_count = sum(1 for p in all_players if p["status"] == "optimal")
    ready_count = sum(1 for p in all_players if p["status"] == "ready")
    limited_count = sum(1 for p in all_players if p["status"] == "limited")
    bench_count = sum(1 for p in all_players if p["status"] == "bench")
    rest_count = sum(1 for p in all_players if p["status"] == "rest")
    
    # Display metrics in a grid
    metric_cols = st.columns(5)
    
    with metric_cols[0]:
        st.markdown(
            f"""
            <div style="text-align: center; padding: 10px; background-color: {THEME["CARD"]}; border-radius: 5px; box-shadow: 0 1px 3px rgba(0,0,0,0.12);">
                <div style="font-size: 14px; color: {THEME["TEXT_LIGHT"]};">Starting XI Avg</div>
                <div style="font-size: 24px; font-weight: bold; color: {THEME["PRIMARY"]};">{starting_xi_avg:.1f}%</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with metric_cols[1]:
        st.markdown(
            f"""
            <div style="text-align: center; padding: 10px; background-color: {THEME["CARD"]}; border-radius: 5px; box-shadow: 0 1px 3px rgba(0,0,0,0.12);">
                <div style="font-size: 14px; color: {THEME["SUCCESS"]};">Optimal</div>
                <div style="font-size: 24px; font-weight: bold; color: {THEME["PRIMARY"]};">{optimal_count}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with metric_cols[2]:
        st.markdown(
            f"""
            <div style="text-align: center; padding: 10px; background-color: {THEME["CARD"]}; border-radius: 5px; box-shadow: 0 1px 3px rgba(0,0,0,0.12);">
                <div style="font-size: 14px; color: #88C054;">Ready</div>
                <div style="font-size: 24px; font-weight: bold; color: {THEME["PRIMARY"]};">{ready_count}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with metric_cols[3]:
        st.markdown(
            f"""
            <div style="text-align: center; padding: 10px; background-color: {THEME["CARD"]}; border-radius: 5px; box-shadow: 0 1px 3px rgba(0,0,0,0.12);">
                <div style="font-size: 14px; color: {THEME["WARNING"]};">Limited</div>
                <div style="font-size: 24px; font-weight: bold; color: {THEME["PRIMARY"]};">{limited_count}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with metric_cols[4]:
        st.markdown(
            f"""
            <div style="text-align: center; padding: 10px; background-color: {THEME["CARD"]}; border-radius: 5px; box-shadow: 0 1px 3px rgba(0,0,0,0.12);">
                <div style="font-size: 14px; color: {THEME["ACCENT"]};">Rest</div>
                <div style="font-size: 24px; font-weight: bold; color: {THEME["PRIMARY"]};">{rest_count}</div>
            </div>
            """,
            unsafe_allow_html=True
        )