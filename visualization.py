# visualization.py
"""
Functions for creating interactive Plotly visualizations of player recovery data,
including daily trends and weekly summaries. Optimized for compact theme.
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd
from theme import THEME # Ensure theme is imported

def create_plotly_chart(df, risk_threshold, show_rolling_avg=True, window=7, player_name="Unknown Player"):
    """
    Create an interactive Plotly chart showing daily EMBOSS scores and trends.
    Optimized layout for compact display. Includes chart title.
    """
    if df is None or df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No data available for the selected period.", showarrow=False,
                           xref="paper", yref="paper", x=0.5, y=0.5, font=dict(color=THEME['TEXT_LIGHT']))
        fig.update_layout(title=f'Recovery Trend - {player_name}', height=350, plot_bgcolor=THEME['CARD']) # Reduced default height
        return fig

    df_chart = df.copy()
    df_chart['date'] = pd.to_datetime(df_chart['date'])
    df_chart = df_chart.sort_values('date')

    if show_rolling_avg:
        effective_window = min(window, len(df_chart))
        if effective_window < 1: effective_window = 1
        df_chart['rolling_avg'] = df_chart['emboss_baseline_score'].rolling(
            window=effective_window, min_periods=1).mean()

    fig = go.Figure()

    # Add scatter plot for individual daily scores
    point_colors = [THEME['ACCENT'] if score < risk_threshold else THEME['SUCCESS']
                    for score in df_chart['emboss_baseline_score']]
    fig.add_trace(
        go.Scatter(
            x=df_chart['date'],
            y=df_chart['emboss_baseline_score'],
            mode='markers+lines',
            name='Daily Score',
            marker=dict(
                size=8, # Slightly smaller markers
                color=point_colors,
                line=dict(width=1, color=THEME['CARD'])
            ),
            line=dict(color='rgba(108, 117, 125, 0.3)', width=1), # Slightly thicker line
            hovertemplate='<b>%{x|%a, %d %b}</b><br>Score: %{y:.2f}<extra></extra>'
        )
    )

    if show_rolling_avg and 'rolling_avg' in df_chart.columns:
        fig.add_trace(
            go.Scatter(
                x=df_chart['date'],
                y=df_chart['rolling_avg'],
                mode='lines',
                name=f'{window}-Day Avg',
                line=dict(color=THEME['PRIMARY'], width=1), # Slightly thinner avg line
                hovertemplate='Avg: %{y:.2f}<extra></extra>'
            )
        )

    fig.add_trace(
        go.Scatter(
            x=[df_chart['date'].min(), df_chart['date'].max()],
            y=[risk_threshold, risk_threshold],
            mode='lines',
            name='Risk Threshold',
            line=dict(color=THEME['ACCENT'], width=1.5, dash='dash'), # Thinner threshold line
            hoverinfo='skip'
        )
    )

    # Add shaded background areas
    if len(df_chart) >= 1:
        date_min = df_chart['date'].min() - pd.Timedelta(days=0.5) # Extend slightly for visuals
        date_max = df_chart['date'].max() + pd.Timedelta(days=0.5)
        fig.add_shape(type="rect", xref="x", yref="y",
                      x0=date_min, y0=-1.05, x1=date_max, y1=risk_threshold,
                      fillcolor=THEME['ACCENT'], opacity=0.06, layer="below", line_width=0) # More subtle opacity
        fig.add_shape(type="rect", xref="x", yref="y",
                      x0=date_min, y0=risk_threshold, x1=date_max, y1=1.05,
                      fillcolor=THEME['SUCCESS'], opacity=0.09, layer="below", line_width=0) # More subtle opacity


    # Update layout for compact aesthetics
    fig.update_layout(
        # --- REINSTATED TITLE ---
        title=dict(
            text=f'{player_name}',
            y=0.98, # Position slightly lower from top
            x=0.05, # Position left
            xanchor='left',
            yanchor='top',
            font=dict(size=16, color=THEME['PRIMARY'], family="Arial, sans-serif") # Slightly smaller title
        ),
        # --- END TITLE ---
        legend=dict(
            orientation="h", yanchor="bottom", y=1.0, xanchor="right", x=1, # Adjusted slightly
            font=dict(size=12, color=THEME['TEXT_LIGHT']),
            bgcolor='rgba(255,255,255,0.6)'
        ),
        plot_bgcolor=THEME['CARD'],
        paper_bgcolor=THEME['CARD'],
        hovermode='x unified',
        xaxis=dict(
            title=None,
            showgrid=True, gridcolor='rgba(220, 220, 220, 0.4)',
            tickformat='%d %b',
        ),
        yaxis=dict(
            # --- CORRECTED: Nested font inside title dict ---
            title=dict(
                text='EMBOSS Score',
                font=dict(size=11, color=THEME['TEXT_LIGHT'])
            ),
            # --- END CORRECTION ---
            range=[-1.05, 1.05],
            showgrid=True, gridcolor='rgba(220, 220, 220, 0.4)',
            zeroline=True, zerolinecolor='rgba(0, 0, 0, 0.15)',
            tickfont=dict(size=10),
        ),
        margin=dict(l=40, r=20, t=35, b=30), # Adjusted top margin for title
        height=380,
    )

    return fig

def create_weekly_summary_chart(weekly_data):
    """
    Create a compact chart summarizing weekly recovery metrics. Includes chart title.
    """
    if weekly_data is None or weekly_data.empty:
        fig = go.Figure()
        fig.add_annotation(text="No weekly summary data available.", showarrow=False,
                           xref="paper", yref="paper", x=0.5, y=0.5, font=dict(color=THEME['TEXT_LIGHT']))
        fig.update_layout(title='Weekly Recovery Summary', height=300, plot_bgcolor=THEME['CARD']) # Reduced height
        return fig

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    min_values = weekly_data['min'].fillna(0).values
    max_values = weekly_data['max'].fillna(0).values
    risk_days = weekly_data['risk_days'].fillna(0).astype(int).values

    fig.add_trace(
        go.Bar(
            x=weekly_data['week_ending'],
            y=weekly_data['mean'],
            name='Avg Score (Min/Max)',
            marker_color=THEME['PRIMARY'],
            opacity=0.7,
            error_y=dict(
                type='data', symmetric=False,
                array=max_values - weekly_data['mean'].values,
                arrayminus=weekly_data['mean'].values - min_values,
                color=THEME['TEXT_LIGHT'], thickness=1, width=2,
            ),
            hovertemplate=(
                '<b>Week: %{x|%d %b %Y}</b><br>'
                'Avg: %{y:.2f} (Min: %{customdata[0]:.2f}, Max: %{customdata[1]:.2f})<br>'
                'Risk Days: %{customdata[2]}<extra></extra>'
            ),
            customdata=np.stack((min_values, max_values, risk_days), axis=-1)
        ),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(
            x=weekly_data['week_ending'],
            y=risk_days,
            name='Risk Days',
            mode='lines+markers',
            line=dict(color=THEME['ACCENT'], width=2),
            marker=dict(size=6, color=THEME['ACCENT']),
            hovertemplate='Risk Days: %{y}<extra></extra>'
        ),
        secondary_y=True,
    )

    max_risk_days_val = max(weekly_data['risk_days'].fillna(0).astype(int).max(), 1) if not weekly_data.empty else 1
    fig.update_layout(
         # --- REINSTATED TITLE ---
        title=dict(
            text='Weekly Summary',
            y=0.98, # Position slightly lower from top
            x=0.05, # Position left
            xanchor='left',
            yanchor='top',
            font=dict(size=14, color=THEME['PRIMARY'], family="Arial, sans-serif") # Slightly smaller title
        ),
        # --- END TITLE ---
        legend=dict(
            orientation="h", yanchor="bottom", y=1.0, xanchor="right", x=1,
            font=dict(size=10, color=THEME['TEXT_LIGHT']),
            bgcolor='rgba(255,255,255,0.6)'
        ),
        plot_bgcolor=THEME['CARD'],
        paper_bgcolor=THEME['CARD'],
        barmode='overlay',
        xaxis=dict(
            title=None, tickformat='%d %b',
            gridcolor='rgba(220, 220, 220, 0.4)',
            tickfont=dict(size=10),
        ),
        yaxis=dict(
             # --- CORRECTED: Nested font inside title dict ---
            title=dict(
                text='Avg Score',
                font=dict(size=11, color=THEME['TEXT_LIGHT'])
            ),
             # --- END CORRECTION ---
            range=[-1.05, 1.05], tickformat='.1f',
            showgrid=True, gridcolor='rgba(220, 220, 220, 0.4)',
            zeroline=True, zerolinecolor='rgba(0, 0, 0, 0.15)',
            tickfont=dict(size=10),
        ),
        yaxis2=dict(
             # --- CORRECTED: Nested font inside title dict ---
            title=dict(
                text='Risk Days',
                font=dict(size=11, color=THEME['TEXT_LIGHT'])
            ),
             # --- END CORRECTION ---
            range=[0, max(7, max_risk_days_val + 1)], tickformat='d',
            showgrid=False, overlaying='y', side='right',
            tickfont=dict(size=10),
        ),
        hovermode='x unified',
        margin=dict(l=40, r=40, t=35, b=30), # Adjusted top margin for title
        height=350,
    )

    return fig