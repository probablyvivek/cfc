# theme.py
"""
Theme configuration for the CFC Recovery Insights Dashboard.
Modify this file to change the dashboard's appearance.
"""

# Theme color configuration
THEME = {
    'PRIMARY': "#1A2B4C",      # Dark blue - primary color
    'SECONDARY': "#A3CEF1",    # Light blue - secondary elements
    'ACCENT': "#E63946",       # Red - for alerts and highlights
    'WARNING': "#F4A261",      # Orange - for warnings
    'SUCCESS': "#2A9D8F",      # Green - for positive indicators
    'BACKGROUND': "#F8F9FA",   # Light background
    'CARD': "#FFFFFF",         # Card background
    'TEXT': "#1A2B4C",         # Primary text color
    'TEXT_LIGHT': "#6C757D"    # Secondary text color
}

def apply_theme_css():
    """
    Returns CSS styling for the dashboard based on the theme configuration.
    """
    return f"""
    <style>
        /* Base styles */
        .main .block-container {{
            padding-top: 1rem;
            padding-bottom: 1rem;
        }}
        
        /* Card styling */
        .metric-card {{
            background-color: {THEME['CARD']};
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            padding: 20px;
            text-align: center;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        .metric-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        }}
        .metric-value {{
            font-size: 28px;
            font-weight: 700;
            color: {THEME['PRIMARY']};
        }}
        .metric-label {{
            font-size: 14px;
            color: {THEME['TEXT_LIGHT']};
            margin-bottom: 5px;
        }}
        
        /* Status box styling */
        .status-box {{
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
        }}
        .status-icon {{
            font-size: 24px;
            margin-right: 10px;
        }}
        
        /* Chart area */
        .chart-area {{
            background-color: {THEME['CARD']};
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            padding: 20px;
            margin-top: 20px;
        }}
        
        /* Header */
        .dashboard-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }}
        .dashboard-title {{
            font-size: 36px;
            font-weight: 800;
            color: {THEME['PRIMARY']};
            margin: 0;
        }}
        .user-info {{
            text-align: right;
            font-size: 14px;
            color: {THEME['TEXT']};
        }}
        
        /* Recommendations panel */
        .recommendation-panel {{
            background-color: {THEME['CARD']};
            border-left: 5px solid {THEME['SECONDARY']};
            border-radius: 10px;
            padding: 15px;
            margin-top: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        
        /* Weekly summary */
        .weekly-summary {{
            background-color: {THEME['CARD']};
            border-radius: 10px;
            padding: 15px;
            margin-top: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        
        /* Footer */
        .dashboard-footer {{
            text-align: center;
            padding: 20px;
            color: {THEME['TEXT_LIGHT']};
            font-size: 12px;
        }}
    </style>
    """