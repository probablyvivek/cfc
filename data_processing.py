"""
Functions for processing, loading, and cleaning recovery data.
"""

import pandas as pd
import streamlit as st
from data_generator import generate_sample_data

def load_data(uploaded_file):
    """
    Load and preprocess data from uploaded file or default source
    
    Parameters:
    uploaded_file: File object from Streamlit file uploader
    
    Returns:
    DataFrame: Processed data frame with player information
    """
    if uploaded_file:
        temp_df = pd.read_csv(uploaded_file)
        try:
            if "emboss_baseline_score" in temp_df.columns and "date" in temp_df.columns:
                df = temp_df.copy()
                df["date"] = pd.to_datetime(df["date"])
                
                # If there's no player_name column, add a default
                if "player_name" not in df.columns:
                    df["player_name"] = "Unknown Player"
                
                return df
            elif "metric" in temp_df.columns and "value" in temp_df.columns:
                # Raw file format handling
                df = temp_df[temp_df["metric"] == "emboss_baseline_score"].copy()
                df["date"] = pd.to_datetime(df["sessionDate"], format="%d/%m/%Y")
                
                # Extract player information if available
                if "playerId" in df.columns:
                    df.rename(columns={"playerId": "player_name"}, inplace=True)
                elif "playerName" in df.columns:
                    df.rename(columns={"playerName": "player_name"}, inplace=True)
                else:
                    df["player_name"] = "Unknown Player"
                    
                df = df[["date", "value", "player_name"]].dropna().sort_values("date")
                df.rename(columns={"value": "emboss_baseline_score"}, inplace=True)
                return df
            else:
                st.error("❌ Uploaded file format not recognized.")
                return None
        except Exception as e:
            st.error(f"❌ Error processing file: {str(e)}")
            return None
    else:
        # Load default data
        try:
            df = pd.read_csv("cleaned_data/cleaned_CFC_Recovery_Status_Data.csv")
            df["date"] = pd.to_datetime(df["date"])
            
            # If there's no player_name column, add a default
            if "player_name" not in df.columns:
                df["player_name"] = "Unknown Player"
                
            return df
        except Exception as e:
            # Generate sample data if default file not found
            st.warning("⚠️ Default data not found. Using synthetic data.")
            return generate_sample_data()

def calculate_rolling_average(df, window=7):
    """
    Calculate rolling average of scores with error handling
    
    Parameters:
    df (DataFrame): DataFrame with 'emboss_baseline_score' column
    window (int): Window size for rolling average
    
    Returns:
    DataFrame: DataFrame with added 'rolling_avg' column
    """
    if df is None or len(df) == 0:
        return df
    
    df = df.copy()
    
    # Make sure window size is valid
    effective_window = min(window, len(df))
    if effective_window < 1:
        effective_window = 1
    
    try:
        # Calculate rolling average
        df['rolling_avg'] = df['emboss_baseline_score'].rolling(
            window=effective_window, 
            min_periods=1
        ).mean()
    except Exception as e:
        # Fallback method if rolling fails
        st.warning(f"Warning: Couldn't calculate rolling average using standard method. Using alternative approach.")
        # Simple manual calculation as fallback
        rolling_values = []
        for i in range(len(df)):
            start_idx = max(0, i - effective_window + 1)
            rolling_values.append(df['emboss_baseline_score'].iloc[start_idx:i+1].mean())
        df['rolling_avg'] = rolling_values
    
    return df

def get_weekly_summary(df, risk_threshold):
    """
    Generate weekly summary statistics
    
    Parameters:
    df (DataFrame): DataFrame with 'emboss_baseline_score' and 'date' columns
    risk_threshold (float): Threshold for considering days as 'risk' days
    
    Returns:
    DataFrame: Weekly summary statistics
    """
    from datetime import timedelta
    
    if len(df) == 0:
        # Return empty dataframe with correct structure if no data
        return pd.DataFrame(columns=['week_ending', 'mean', 'min', 'max', 'std', 'risk_days', 'risk_pct'])
    
    # Explicitly convert date to datetime to ensure compatibility
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'])
    
    # Group by week manually instead of using resample
    df['week_ending'] = df['date'].apply(lambda x: x + pd.Timedelta(days=(6 - x.dayofweek)))
    
    # Aggregate by week_ending
    weekly_stats = df.groupby('week_ending').agg({
        'emboss_baseline_score': ['mean', 'min', 'max', 'std']
    }).reset_index()
    
    # Flatten the multi-level columns
    weekly_stats.columns = ['week_ending', 'mean', 'min', 'max', 'std']
    
    # Calculate number of days below threshold each week
    risk_days = []
    for week_end in weekly_stats['week_ending']:
        week_start = week_end - timedelta(days=6)
        week_data = df[(df['date'] >= week_start) & (df['date'] <= week_end)]
        days_below = (week_data['emboss_baseline_score'] < risk_threshold).sum()
        risk_days.append(days_below)
    
    weekly_stats['risk_days'] = risk_days
    
    # Calculate days in each week (might be less than 7 for partial weeks)
    days_in_week = []
    for week_end in weekly_stats['week_ending']:
        week_start = week_end - timedelta(days=6)
        days = len(df[(df['date'] >= week_start) & (df['date'] <= week_end)])
        days_in_week.append(days)
    
    weekly_stats['days_in_week'] = days_in_week
    weekly_stats['risk_pct'] = weekly_stats.apply(
        lambda row: (row['risk_days'] / row['days_in_week']) * 100 if row['days_in_week'] > 0 else 0, 
        axis=1
    )
    
    return weekly_stats