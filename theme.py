# theme.py
"""
Theme configuration for the CFC Recovery Insights Dashboard.
Modify this file to change the dashboard's appearance.
"""

# Theme color configuration
THEME = {
    'PRIMARY': "#0D1B2A",      # Darker Blue - primary color, headers, key elements
    'SECONDARY': "#A3CEF1",    # Light blue - secondary elements, accents
    'ACCENT': "#E63946",       # Red - high risk, alerts, errors
    'WARNING': "#F4A261",      # Orange - moderate risk, warnings
    'SUCCESS': "#2A9D8F",      # Green - optimal status, positive indicators
    'BACKGROUND': "#F8F9FA",   # Very Light gray - page background
    'CARD': "#FFFFFF",         # White - card backgrounds
    'TEXT': "#1A2B4C",         # Dark Blue/Near Black - primary text color
    'TEXT_LIGHT': "#6C757D"    # Gray - secondary text, labels
}

# Add status colors mapping for easier use in CSS and potentially elsewhere
STATUS_COLORS = {
    "optimal": THEME["SUCCESS"],
    "high_risk": THEME["ACCENT"],      # Added high_risk explicitly
    "moderate_risk": THEME["WARNING"], # Added moderate_risk explicitly
    "ready": "#6CB55A", # Brighter green for distinct 'Ready'
    "limited": THEME["WARNING"],
    "bench": "#E67E39", # Orange for 'Bench'
    "rest": THEME["ACCENT"],
    "unknown": THEME["TEXT_LIGHT"]
}

def apply_theme_css():
    """
    Returns CSS styling for the dashboard. Includes styles for base elements, metrics,
    status boxes, charts, panels, and team readiness. Aims for a clean but
    slightly more visually structured 'Figma-like' feel.
    """
    # --- Generate Status Specific CSS Rules ---
    status_css_rules = ""
    # Player Cards (Team Readiness)
    for status, color in STATUS_COLORS.items():
        if status not in ["high_risk", "moderate_risk"]: # Exclude analysis statuses from card styling
            status_css_rules += f"""
            .player-card-v2.{status} {{ border-left-color: {color}; }}
            .player-card-v2.{status} .player-status-badge {{ background-color: {color}; color: white; }}
            .player-card-v2.{status} .readiness-score {{ color: {color}; }}
            """
    # Status Box & Rec Title (Individual Analysis)
    for status, color in STATUS_COLORS.items():
         status_css_rules += f"""
         .status-box.{status} {{ border-left-color: {color}; background-color: {color}1A; }}
         .status-box.{status} h3 {{ color: {color}; }}
         .info-panel h3.{status} {{ color: {color}; }}
         """

    # Special case for unknown status badge/box color
    status_css_rules += f"""
        .player-card-v2.unknown .player-status-badge {{ background-color: {STATUS_COLORS['unknown']}; color: {THEME['TEXT']}; }}
        .status-box.unknown {{ border-left-color: {STATUS_COLORS['unknown']}; background-color: {STATUS_COLORS['unknown']}1A; }}
        .status-box.unknown h3 {{ color: {STATUS_COLORS['unknown']}; }}
        .info-panel h3.unknown {{ color: {STATUS_COLORS['unknown']}; }}
        """

    # --- Main CSS String ---
    return f"""
    <style>
        /* --- Base & General Styles --- */
        body {{
            background-color: {THEME['BACKGROUND']};
            color: {THEME['TEXT']};
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji";
        }}
        .main .block-container {{
            padding-top: 1.5rem;
            padding-bottom: 1.5rem;
            padding-left: 2rem;
            padding-right: 2rem;
        }}
        h1, h2, h3, h4, h5, h6 {{
            color: {THEME['PRIMARY']};
            font-weight: 600;
            margin-top: 0;
            margin-bottom: 0.6rem;
        }}
        p {{
            color: {THEME['TEXT']};
            line-height: 1.55;
            margin-bottom: 0.8rem;
        }}
        small {{
             font-size: 0.85em;
             color: {THEME['TEXT_LIGHT']};
        }}
        hr {{
            border: none;
            border-top: 1px solid #e9ecef;
            margin: 1.8rem 0;
        }}
        /* --- Tabs --- */
        .stTabs {{ margin-bottom: 1rem; }} /* Add margin below the whole tab container */
        .stTabs [data-baseweb="tab-list"] {{
        	gap: 12px;
            border-bottom: 2px solid #e9ecef;
            /* margin-bottom: 1rem; REMOVED margin here, added to .stTabs */
        }}
        .stTabs [data-baseweb="tab"] {{
        	height: 40px; background-color: transparent; border-radius: 6px 6px 0 0;
        	padding: 8px 14px; color: {THEME['TEXT_LIGHT']}; border: none;
            border-bottom: 2px solid transparent; margin-bottom: -2px;
            transition: color 0.2s ease, border-color 0.2s ease;
        }}
        .stTabs [data-baseweb="tab"]:hover {{ background-color: #f0f2f6; color: {THEME['PRIMARY']}; }}
        .stTabs [aria-selected="true"] {{
              background-color: transparent; font-weight: 600; color: {THEME['PRIMARY']};
              border: none; border-bottom: 2px solid {THEME['PRIMARY']}; margin-bottom: -2px;
         }}


        /* --- Header --- */
        .dashboard-header {{
            display: flex; justify-content: space-between; align-items: flex-end;
            margin-bottom: 2rem; padding-bottom: 12px; border-bottom: 1px solid #dee2e6;
        }}
        .dashboard-title {{ font-size: 26px; font-weight: 600; color: {THEME['PRIMARY']}; margin: 0; line-height: 1.1; }}
        .user-info {{ text-align: right; font-size: 13px; color: {THEME['TEXT_LIGHT']}; line-height: 1.4; padding-bottom: 2px; }}
        .user-info b {{ color: {THEME['TEXT']}; font-weight: 600; }}

        /* --- Individual Player: Metrics Section --- */
        .metric-card {{
            background-color: {THEME['CARD']}; border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05); border: 1px solid #e9ecef;
            border-top: 3px solid {THEME['SECONDARY']}33; padding: 15px 18px;
            text-align: center; height: 100%; /* Keep height 100% for equal height in columns */
            display: flex; flex-direction: column; justify-content: center;
            margin-bottom: 0; /* Columns gap handles spacing */
            transition: box-shadow 0.2s ease, border-top-color 0.2s ease;
        }}
         .metric-card:hover {{ box-shadow: 0 3px 8px rgba(0, 0, 0, 0.07); border-top-color: {THEME['SECONDARY']}88; }}
        .metric-value {{ font-size: 24px; font-weight: 600; color: {THEME['PRIMARY']}; line-height: 1.1; margin-bottom: 3px; /* Reduced margin */ }}
        .metric-value span {{ font-size: 0.7em; margin-left: 3px; vertical-align: middle; display: inline-block; }}
        .metric-label {{ font-size: 13px; color: {THEME['TEXT_LIGHT']}; margin-bottom: 0; /* CORRECTED: Removed '10', set to 0 */ font-weight: 500; }}

        /* Add space below the metrics row using CSS */
        /* Target the element holding the columns. This selector might be unstable. */
        /* Inspect element in browser if this doesn't work. */
        div[data-testid="stHorizontalBlock"] > div:has(div.metric-card) {{
             margin-bottom: 1.8rem; /* Space below metrics row */
        }}


        /* --- Individual Player: Status Box --- */
        .status-box {{
            padding: 15px 20px; /* Increased padding slightly */
            border-radius: 8px;
            margin-bottom: 1.8rem; /* CORRECTED: Was margin-above, ensure sufficient space */
            display: flex; align-items: center; box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            border: 1px solid #e9ecef; border-left-width: 6px; border-left-style: solid;
        }}
        .status-icon {{ font-size: 24px; margin-right: 15px; }}
        .status-box h3 {{ margin-top: 0; margin-bottom: 3px; font-size: 1.1em; font-weight: 600; }}
        .status-box small {{ font-size: 0.85em; color: {THEME['TEXT_LIGHT']}; display: block; }}


        /* --- Individual Player: Chart Area --- */
        .chart-area {{ padding: 5px 10px 10px 10px; }}


        /* --- Individual Player: Info Panel (Recs, Insights) --- */
        .info-panel {{ padding: 20px 22px; }}
        .info-panel-title {{ margin-top: 0; margin-bottom: 18px; font-size: 1.15em; font-weight: 600; color: {THEME['PRIMARY']}; padding-bottom: 8px; border-bottom: 1px solid #eee; }}
        .info-panel-content {{ overflow-y: auto; }} /* Keep scroll */
        .info-panel h3 {{ margin-top: 0; margin-bottom: 8px; font-size: 1.05em; font-weight: 600; }}
        .info-panel h4 {{ margin-top: 15px; margin-bottom: 8px; font-size: 0.9em; color: {THEME['PRIMARY']}; font-weight: 600; text-transform: uppercase; letter-spacing: 0.8px; }}
        .info-panel .analysis-text {{ font-size: 0.9em; color: {THEME['TEXT_LIGHT']}; background-color: #f8f9fa; padding: 8px 12px; border-radius: 4px; margin-bottom: 15px; line-height: 1.5; }}
        .info-panel .analysis-text b {{ font-weight: 600; color: {THEME['TEXT']}; }}
        .info-panel ul {{ font-size: 0.9em; color: {THEME['TEXT']}; line-height: 1.6; margin-bottom: 10px; padding-left: 18px; list-style-type: disc; }}
        .info-panel li {{ margin-bottom: 6px; }}
        .info-panel small {{ display: block; margin-top: 15px; padding-top: 10px; border-top: 1px dashed #e0e0e0; font-size: 0.8em; color: {THEME['TEXT_LIGHT']}; font-style: italic; }}
        .info-panel .insights-separator {{ border-top: 1px solid #e9ecef; margin: 20px 0 15px 0; }}

        /* --- Team Readiness Styles --- */
        /* ... (Team styles remain unchanged) ... */
        .summary-box {{ background-color: {THEME['CARD']}; border-radius: 6px; padding: 10px; text-align: center; border: 1px solid #e9ecef; box-shadow: 0 1px 2px rgba(0,0,0,0.05); height: 100%; display: flex; flex-direction: column; justify-content: center; margin-bottom: 10px; }} .summary-box-label {{ font-size: 0.75em; color: {THEME['TEXT_LIGHT']}; margin-bottom: 3px; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; }} .summary-box-value {{ font-size: 1.6em; font-weight: 600; color: {THEME['PRIMARY']}; line-height: 1.1; }} .summary-box.optimal .summary-box-value {{ color: {STATUS_COLORS['optimal']}; }} .summary-box.ready .summary-box-value {{ color: {STATUS_COLORS['ready']}; }} .summary-box.limited .summary-box-value {{ color: {STATUS_COLORS['limited']}; }} .summary-box.bench .summary-box-value {{ color: {STATUS_COLORS['bench']}; }} .summary-box.rest .summary-box-value {{ color: {STATUS_COLORS['rest']}; }}
        .player-card-v2 {{ background-color: {THEME['CARD']}; border-radius: 6px; padding: 8px 10px; margin-bottom: 6px; border-left: 5px solid grey; box-shadow: 0 1px 2px rgba(0,0,0,0.04); display: flex; justify-content: space-between; align-items: center; border: 1px solid #e9ecef; }} .player-card-v2:hover {{ box-shadow: 0 2px 5px rgba(0,0,0,0.08); transform: translateY(-1px); }} .player-card-v2 .player-info {{ flex-grow: 1; margin-right: 8px; overflow: hidden; }} .player-card-v2 .player-name {{ font-weight: 600; font-size: 0.9em; color: {THEME['TEXT']}; display: block; margin-bottom: 1px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }} .player-card-v2 .player-tag {{ font-size: 0.75em; font-weight: 600; padding: 1px 6px; border-radius: 4px; display: inline-block; text-transform: uppercase; letter-spacing: 0.5px; line-height: 1.3; text-align: center; margin-top: 2px; }} .player-card-v2 .player-status-badge {{ color: white; }} .player-card-v2 .player-position-text {{ color: {THEME['TEXT_LIGHT']}; background-color: transparent; font-weight: 500; padding: 1px 0; }} .player-card-v2 .player-readiness {{ text-align: right; white-space: nowrap; }} .player-card-v2 .readiness-score {{ font-size: 1.0em; font-weight: 700; margin-right: 2px; }} .player-card-v2 .trend-icon {{ font-size: 0.8em; margin-left: 3px; display: inline-block; vertical-align: middle; line-height: 1; }}


        /* Apply status colors via CSS rules */
        {status_css_rules}


        /* --- Footer --- */
        .dashboard-footer {{ text-align: center; padding: 20px 20px 15px 20px; color: {THEME['TEXT_LIGHT']}; font-size: 12px; border-top: 1px solid #e9ecef; margin-top: 2.5rem; }}

    </style>
    """