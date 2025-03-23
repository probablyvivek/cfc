"""
Functions for creating visualizations of recovery data.
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd
from theme import THEME

def create_plotly_chart(df, risk_threshold, show_rolling_avg=True, window=7, player_name="Unknown Player"):
    """
    Create an interactive Plotly chart for recovery data
    
    Parameters:
    df (DataFrame): DataFrame with recovery data
    risk_threshold (float): Threshold for considering scores as 'risk'
    show_rolling_avg (bool): Whether to show rolling average line
    window (int): Window size for rolling average
    player_name (str): Name of the player for chart title
    
    Returns:
    Figure: Plotly figure object
    """
    # Check if we have data to display
    if len(df) == 0:
        # Create empty figure with message
        fig = go.Figure()
        fig.add_annotation(
            text="No data available for the selected period",
            showarrow=False,
            font=dict(size=14, color=THEME['TEXT']),
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5
        )
        fig.update_layout(
            title={
                'text': f'EMBOSS Recovery Score Trend Analysis of {player_name}',
                'y': 0.95,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': dict(size=24, color=THEME['PRIMARY'], family='Arial, sans-serif')
            },
            plot_bgcolor='white',
            height=500,
        )
        return fig
    
    # Create a copy of the dataframe to avoid modifying the original
    df_chart = df.copy()
    
    # Make sure date is datetime
    df_chart['date'] = pd.to_datetime(df_chart['date'])
    
    # Calculate rolling average if requested and if we have enough data
    if show_rolling_avg:
        min_periods = min(window, len(df_chart))
        df_chart['rolling_avg'] = df_chart['emboss_baseline_score'].rolling(
            window=window, min_periods=1).mean()
    
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": False}]])
    
    # Add trace for individual data points
    # Color points based on risk threshold
    colors = ['#E63946' if score < risk_threshold else '#2A9D8F' 
              for score in df_chart['emboss_baseline_score']]
    
    # Add scatter plot for individual points
    fig.add_trace(
        go.Scatter(
            x=df_chart['date'], 
            y=df_chart['emboss_baseline_score'],
            mode='markers+lines',
            name='Daily Score',
            marker=dict(
                size=10,
                color=colors,
                line=dict(width=2, color='#FFFFFF')
            ),
            line=dict(color='rgba(26, 43, 76, 0.3)', width=1),
            hovertemplate='<b>%{x|%d %b}</b><br>Score: %{y:.2f}<extra></extra>'
        )
    )
    
    # Add rolling average line if requested
    if show_rolling_avg and 'rolling_avg' in df_chart.columns:
        fig.add_trace(
            go.Scatter(
                x=df_chart['date'],
                y=df_chart['rolling_avg'],
                mode='lines',
                name=f'{window}-Day Average',
                line=dict(color='#1A2B4C', width=3, dash='solid'),
                hovertemplate='<b>%{x|%d %b}</b><br>Avg: %{y:.2f}<extra></extra>'
            )
        )
    
    # Add risk threshold line
    fig.add_trace(
        go.Scatter(
            x=[df_chart['date'].min(), df_chart['date'].max()],
            y=[risk_threshold, risk_threshold],
            mode='lines',
            name='Risk Threshold',
            line=dict(color='#E63946', width=2, dash='dash'),
            hoverinfo='skip'
        )
    )
    
    # Check if we have enough data for shaded areas
    if len(df_chart) >= 2:
        # Add shaded areas for risk zones (use a safe approach)
        date_concat = pd.concat([df_chart['date'], df_chart['date'].sort_values(ascending=False)])
        
        fig.add_trace(
            go.Scatter(
                x=date_concat,
                y=[-1] * len(df_chart) + [risk_threshold] * len(df_chart),
                fill='toself',
                fillcolor='rgba(230, 57, 70, 0.1)',
                line=dict(color='rgba(0,0,0,0)'),
                hoverinfo='skip',
                showlegend=False
            )
        )
        
        # Add shaded areas for optimal zone
        fig.add_trace(
            go.Scatter(
                x=date_concat,
                y=[risk_threshold] * len(df_chart) + [1] * len(df_chart),
                fill='toself',
                fillcolor='rgba(42, 157, 143, 0.1)',
                line=dict(color='rgba(0,0,0,0)'),
                hoverinfo='skip',
                showlegend=False
            )
        )
    
    # Update layout
    fig.update_layout(
        title={
            'text': f'EMBOSS Recovery Score Trend Analysis of {player_name}',
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(size=24, color=THEME['PRIMARY'], family='Arial, sans-serif')
        },
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(size=12)
        ),
        plot_bgcolor='white',
        hovermode='x unified',
        xaxis=dict(
            title='Date',
            showgrid=True,
            gridcolor='rgba(220, 220, 220, 0.8)',
            tickformat='%d %b',
            tickangle=-30
        ),
        yaxis=dict(
            title='EMBOSS Score',
            range=[-1.05, 1.05],
            showgrid=True,
            gridcolor='rgba(220, 220, 220, 0.8)',
            zeroline=True,
            zerolinecolor='rgba(0, 0, 0, 0.2)'
        ),
        margin=dict(l=10, r=10, t=80, b=30),
        height=500,
    )
    
    return fig

def create_weekly_summary_chart(weekly_data):
    """
    Create a weekly summary chart
    
    Parameters:
    weekly_data (DataFrame): Weekly summary data
    
    Returns:
    Figure: Plotly figure object
    """
    # Check if we have data to display
    if len(weekly_data) == 0:
        # Create empty figure with message
        fig = go.Figure()
        fig.add_annotation(
            text="No weekly data available for the selected period",
            showarrow=False,
            font=dict(size=14, color=THEME['TEXT']),
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5
        )
        fig.update_layout(
            title={
                'text': 'Weekly Recovery Summary',
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': dict(size=18, color=THEME['PRIMARY'])
            },
            plot_bgcolor='white',
            height=350,
        )
        return fig
    
    fig = go.Figure()
    
    # Ensure customdata has the right shape by creating arrays safely
    min_values = weekly_data['min'].fillna(0).values
    max_values = weekly_data['max'].fillna(0).values
    risk_days = weekly_data['risk_days'].fillna(0).values.astype(int)
    
    # Add bar chart for average scores
    fig.add_trace(
        go.Bar(
            x=weekly_data['week_ending'],
            y=weekly_data['mean'],
            name='Weekly Average',
            marker_color=THEME['PRIMARY'],
            error_y=dict(
                type='data',
                symmetric=False,
                array=max_values - weekly_data['mean'].values,  # error bars going up
                arrayminus=weekly_data['mean'].values - min_values,  # error bars going down
                color=THEME['TEXT_LIGHT']
            ),
            hovertemplate='<b>Week ending: %{x|%d %b %Y}</b><br>' +
                         'Avg: %{y:.2f}<br>' +
                         'Min: %{customdata[0]:.2f}<br>' +
                         'Max: %{customdata[1]:.2f}<br>' +
                         'Risk days: %{customdata[2]}<extra></extra>',
            customdata=np.stack((min_values, max_values, risk_days), axis=-1)
        )
    )
    
    # Add risk days as a line
    fig.add_trace(
        go.Scatter(
            x=weekly_data['week_ending'],
            y=weekly_data['risk_days'],
            name='Risk Days',
            mode='lines+markers',
            line=dict(color=THEME['ACCENT'], width=3),
            marker=dict(size=8, color=THEME['ACCENT']),
            yaxis='y2',
            hovertemplate='<b>Week ending: %{x|%d %b %Y}</b><br>' +
                         'Risk days: %{y}<extra></extra>'
        )
    )
    
    # Calculate max risk days for y-axis scaling
    max_risk_days = max(weekly_data['risk_days'].max(), 1)
    
    # Update layout
    fig.update_layout(
        title={
            'text': 'Weekly Recovery Summary',
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(size=18, color=THEME['PRIMARY'])
        },
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        plot_bgcolor='white',
        xaxis=dict(
            title='Week Ending',
            tickformat='%d %b',
            tickangle=-30
        ),
        yaxis=dict(
            title='Average EMBOSS Score',
            range=[-1, 1],
            tickformat='.2f',
            side='left'
        ),
        yaxis2=dict(
            title='Risk Days',
            range=[0, max(7, max_risk_days + 1)],
            tickformat='d',
            overlaying='y',
            side='right'
        ),
        margin=dict(l=10, r=10, t=60, b=30),
        height=350,
    )
    
    return fig

def create_enhanced_workload_visualization(df_player, risk_threshold):
    """
    Create a more football-specific visualization for Acute vs Chronic Workload
    that is intuitive for physiotherapists and workload specialists
    
    Parameters:
    df_player (DataFrame): Complete player history data
    risk_threshold (float): Risk threshold value
    
    Returns:
    Figure: Plotly figure object
    """
    # Check if we have enough data (at least 28 days)
    if len(df_player) < 28:
        # Return empty figure with message
        fig = go.Figure()
        fig.add_annotation(
            text="Insufficient data for workload analysis (28 days required)",
            showarrow=False,
            font=dict(size=14, color=THEME['TEXT']),
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5
        )
        fig.update_layout(
            height=300,
            plot_bgcolor='white'
        )
        return fig
        
    # Create a figure with primary and secondary y-axes
    fig = make_subplots(
        rows=2, 
        cols=1,
        row_heights=[0.7, 0.3],
        vertical_spacing=0.05,
        subplot_titles=("Weekly EMBOSS Score Averages", "")
    )
    
    # Calculate weekly averages for the past 4 weeks
    recent_data = df_player.tail(28).copy()
    recent_data['week_number'] = (recent_data['date'].max() - recent_data['date']).dt.days // 7
    
    # Group by week
    weekly_data = []
    week_labels = []
    
    for week_num in range(4):
        week_df = recent_data[recent_data['week_number'] == week_num]
        
        if len(week_df) > 0:
            week_avg = week_df['emboss_baseline_score'].mean()
            start_date = week_df['date'].min().strftime('%d %b')
            end_date = week_df['date'].max().strftime('%d %b')
            label = f"{start_date} - {end_date}"
            
            weekly_data.append({
                'week_num': 3 - week_num,  # Reverse so most recent is last
                'label': label,
                'avg_score': week_avg,
                'min_score': week_df['emboss_baseline_score'].min(),
                'max_score': week_df['emboss_baseline_score'].max(),
                'days_below_threshold': (week_df['emboss_baseline_score'] < risk_threshold).sum(),
                'days_count': len(week_df)
            })
    
    # Sort by week_num to ensure correct order (oldest to newest)
    weekly_data.sort(key=lambda x: x['week_num'])
    
    # Extract data for plotting
    week_labels = [w['label'] for w in weekly_data]
    avg_scores = [w['avg_score'] for w in weekly_data]
    min_scores = [w['min_score'] for w in weekly_data]
    max_scores = [w['max_score'] for w in weekly_data]
    below_threshold = [w['days_below_threshold'] for w in weekly_data]
    
    # Calculate acute (last 7 days) and chronic (previous 21 days) workloads
    if len(weekly_data) == 4:
        acute_load = avg_scores[-1]
        chronic_load = sum(avg_scores[:-1]) / 3
        
        # Calculate ACWR
        acwr = acute_load / chronic_load if chronic_load != 0 else 1.0
        
        # Determine week-to-week change
        week_change = avg_scores[-1] - avg_scores[-2]
    else:
        acute_load = avg_scores[-1] if weekly_data else 0
        chronic_load = sum(avg_scores) / len(avg_scores) if weekly_data else 0
        acwr = 1.0
        week_change = 0
    
    # Determine colors based on ACWR
    if acwr > 1.5:
        acwr_zone = "High Risk"
        acwr_color = "#E63946"  # Red
    elif acwr > 1.3:
        acwr_zone = "Moderate Risk"
        acwr_color = "#F4A261"  # Orange
    elif acwr > 0.8:
        acwr_zone = "Optimal Zone"
        acwr_color = "#2A9D8F"  # Green
    else:
        acwr_zone = "Undertraining"
        acwr_color = "#A3CEF1"  # Light blue
    
    # Add bar chart for weekly averages with error bars
    fig.add_trace(
        go.Bar(
            x=week_labels,
            y=avg_scores,
            name="Weekly EMBOSS Average",
            marker_color=[
                THEME['SECONDARY'] if i < len(weekly_data) - 1 else THEME['PRIMARY'] 
                for i in range(len(weekly_data))
            ],
            error_y=dict(
                type='data',
                symmetric=False,
                array=[max_s - avg_s for max_s, avg_s in zip(max_scores, avg_scores)],
                arrayminus=[avg_s - min_s for min_s, avg_s in zip(avg_scores, min_scores)],
                color=THEME['TEXT_LIGHT']
            ),
            hovertemplate='<b>%{x}</b><br>Avg: %{y:.2f}<br>Min: %{customdata[0]:.2f}<br>Max: %{customdata[1]:.2f}<br>Days Below Threshold: %{customdata[2]}<extra></extra>',
            customdata=np.column_stack((min_scores, max_scores, below_threshold)),
            showlegend=False
        ),
        row=1, col=1
    )
    
    # Add risk threshold line on the bar chart
    fig.add_trace(
        go.Scatter(
            x=week_labels,
            y=[risk_threshold] * len(week_labels),
            mode='lines',
            name='Risk Threshold',
            line=dict(color=THEME['ACCENT'], width=2, dash='dash'),
            showlegend=False
        ),
        row=1, col=1
    )
    
    # Calculate normalized deviation from ideal ACWR (1.0)
    # For visualization purposes, we'll use a range from 0-2 for ACWR
    ideal_acwr = 1.0
    normalized_positions = []
    
    for i in range(21):  # 21 points for smooth curve
        acwr_value = i * 0.1  # 0.0 to 2.0
        normalized_positions.append(acwr_value)
    
    # Calculate "risk values" for each ACWR position (bell curve)
    risk_values = []
    for acwr_value in normalized_positions:
        if acwr_value < 0.8:
            # Undertraining zone (linear increase up to 0.8)
            risk = 40 + (acwr_value / 0.8) * 40
        elif acwr_value <= 1.1:
            # Optimal zone (highest safety)
            risk = 80 + (acwr_value - 0.8) * (100 - 80) / 0.3
        elif acwr_value <= 1.5:
            # Increasing risk zone (sharp decline)
            risk = 100 - (acwr_value - 1.1) * (100 - 40) / 0.4
        else:
            # High risk zone (flatten out at the bottom)
            risk = 40 - (acwr_value - 1.5) * 30
        
        risk_values.append(max(0, min(100, risk)))
    
    # Add ACWR curve to the bottom panel
    fig.add_trace(
        go.Scatter(
            x=normalized_positions,
            y=risk_values,
            mode='lines',
            name='Risk Profile',
            line=dict(color='rgba(200,200,200,0.5)', width=3),
            fill='tozeroy',
            fillcolor='rgba(200,200,200,0.1)',
            showlegend=False
        ),
        row=2, col=1
    )
    
    # Add colored vertical bands for ACWR zones
    acwr_zones = [
        {"name": "Undertraining", "min": 0, "max": 0.8, "color": "rgba(163, 206, 241, 0.2)"},
        {"name": "Optimal Zone", "min": 0.8, "max": 1.3, "color": "rgba(42, 157, 143, 0.2)"},
        {"name": "Moderate Risk", "min": 1.3, "max": 1.5, "color": "rgba(244, 162, 97, 0.2)"},
        {"name": "High Risk", "min": 1.5, "max": 2.0, "color": "rgba(230, 57, 70, 0.2)"}
    ]
    
    # Add vertical band for each zone
    for zone in acwr_zones:
        fig.add_shape(
            type="rect",
            x0=zone["min"],
            x1=zone["max"],
            y0=0,
            y1=100,
            fillcolor=zone["color"],
            line_width=0,
            layer="below",
            row=2, col=1
        )
        
        # Add zone label
        fig.add_annotation(
            x=(zone["min"] + zone["max"]) / 2,
            y=10,
            text=zone["name"],
            showarrow=False,
            font=dict(size=9, color="gray"),
            row=2, col=1
        )
    
    # Add marker for current ACWR with distinctive diamond shape
    fig.add_trace(
        go.Scatter(
            x=[acwr],
            y=[risk_values[min(int(acwr * 10), len(risk_values)-1)]],
            mode='markers',
            name=f'Current ACWR: {acwr:.2f}',
            marker=dict(
                symbol='diamond',
                size=16,
                color=acwr_color,
                line=dict(width=2, color='white')
            ),
            hovertemplate=f'<b>ACWR: {acwr:.2f}</b><br>Status: {acwr_zone}<extra></extra>',
            showlegend=False
        ),
        row=2, col=1
    )
    
    # Add annotation for current ACWR
    fig.add_annotation(
        x=acwr,
        y=risk_values[min(int(acwr * 10), len(risk_values)-1)] + 15,
        text=f"ACWR: {acwr:.2f}",
        showarrow=True,
        arrowhead=2,
        arrowcolor=acwr_color,
        arrowsize=1,
        arrowwidth=2,
        font=dict(size=12, color=acwr_color, family="Arial, sans-serif"),
        bgcolor="white",
        bordercolor=acwr_color,
        borderpad=4,
        borderwidth=1,
        row=2, col=1
    )
    
    # Update layout
    fig.update_layout(
        title={
            'text': "Acute Chronic Workload Analysis",
            'y': 0.98,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(size=20, color=THEME['PRIMARY'])
        },
        plot_bgcolor='white',
        height=600,
        margin=dict(l=40, r=40, t=80, b=60)
    )
    
    # Update y-axis for weekly averages
    fig.update_yaxes(
        title_text="EMBOSS Score",
        range=[-1, 1],
        showgrid=True,
        gridcolor='rgba(220, 220, 220, 0.8)',
        row=1, col=1
    )
    
    # Update x-axis for weekly averages
    fig.update_xaxes(
        title_text="Weekly Periods",
        showgrid=False,
        row=1, col=1
    )
    
    # Update y-axis for ACWR chart
    fig.update_yaxes(
        title_text="Safety Level (%)",
        range=[0, 100],
        showgrid=False,
        row=2, col=1
    )
    
    # Update x-axis for ACWR chart
    fig.update_xaxes(
        title_text="Acute Chronic Workload Ratio",
        showgrid=True,
        gridcolor='rgba(220, 220, 220, 0.8)',
        range=[0, 2],
        tickvals=[0, 0.5, 0.8, 1.0, 1.3, 1.5, 2.0],
        row=2, col=1
    )
    
    # Add summary stats as annotations
    fig.add_annotation(
        x=0.02,
        y=0.98,
        xref="paper",
        yref="paper",
        text=f"<b>Acute Load:</b> {acute_load:.2f}",
        showarrow=False,
        font=dict(size=12, color=THEME['PRIMARY']),
        bgcolor="white",
        bordercolor=THEME['PRIMARY'],
        borderpad=4,
        borderwidth=1,
        align="left"
    )
    
    fig.add_annotation(
        x=0.02,
        y=0.93,
        xref="paper",
        yref="paper",
        text=f"<b>Chronic Load:</b> {chronic_load:.2f}",
        showarrow=False,
        font=dict(size=12, color=THEME['TEXT']),
        bgcolor="white",
        bordercolor=THEME['TEXT'],
        borderpad=4,
        borderwidth=1,
        align="left"
    )
    
    fig.add_annotation(
        x=0.98,
        y=0.98,
        xref="paper",
        yref="paper",
        text=f"<b>ACWR:</b> {acwr:.2f}",
        showarrow=False,
        font=dict(size=12, color=acwr_color),
        bgcolor="white",
        bordercolor=acwr_color,
        borderpad=4,
        borderwidth=1,
        align="right"
    )
    
    fig.add_annotation(
        x=0.98,
        y=0.93,
        xref="paper",
        yref="paper",
        text=f"<b>Week Change:</b> {week_change:+.2f}",
        showarrow=False,
        font=dict(size=12, color=THEME['TEXT'] if abs(week_change) < 0.1 else (THEME['SUCCESS'] if week_change > 0 else THEME['ACCENT'])),
        bgcolor="white",
        bordercolor=THEME['TEXT'] if abs(week_change) < 0.1 else (THEME['SUCCESS'] if week_change > 0 else THEME['ACCENT']),
        borderpad=4,
        borderwidth=1,
        align="right"
    )
    
    return fig