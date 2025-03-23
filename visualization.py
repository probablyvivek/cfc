# visualization.py
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