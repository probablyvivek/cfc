# data_processing.py
"""
Functions for loading, processing, and cleaning player recovery data.
Includes handling uploaded files, default data, synthetic data generation fallback,
rolling average calculation, and weekly summary generation.
"""

import pandas as pd
import streamlit as st
from data_generator import generate_sample_data
from datetime import timedelta # Added timedelta here

def load_data(uploaded_file):
    """
    Load and preprocess data from an uploaded CSV file or use a default/synthetic dataset.

    Handles two potential CSV formats:
    1.  Columns: 'date', 'emboss_baseline_score', 'player_name' (optional)
    2.  Raw format: 'metric', 'value', 'sessionDate', 'playerId'/'playerName' (optional)

    Parameters:
    uploaded_file: File object from Streamlit file uploader, or None.

    Returns:
    DataFrame: A processed DataFrame with 'date' (datetime), 'emboss_baseline_score' (float),
               and 'player_name' (str) columns, sorted by date. Returns None on failure.
    """
    df = None
    if uploaded_file:
        try:
            temp_df = pd.read_csv(uploaded_file)

            # Check for standard format
            if "emboss_baseline_score" in temp_df.columns and "date" in temp_df.columns:
                df = temp_df.copy()
                df["date"] = pd.to_datetime(df["date"], errors='coerce') # Coerce errors to NaT
                if "player_name" not in df.columns:
                    # st.warning("⚠️ No 'player_name' column found. Assigning 'Default Player'.") # Suppressed message
                    df["player_name"] = "Default Player"

            # Check for raw format
            elif "metric" in temp_df.columns and "value" in temp_df.columns and "sessionDate" in temp_df.columns:
                # st.info("Detected raw data format. Processing...") # Suppressed message
                df = temp_df[temp_df["metric"] == "emboss_baseline_score"].copy()
                df["date"] = pd.to_datetime(df["sessionDate"], format="%d/%m/%Y", errors='coerce') # Use specific format

                # Handle player name variations
                if "playerId" in df.columns:
                    df.rename(columns={"playerId": "player_name"}, inplace=True)
                elif "playerName" in df.columns:
                    df.rename(columns={"playerName": "player_name"}, inplace=True)
                else:
                    # st.warning("⚠️ No player identifier column ('playerId' or 'playerName') found. Assigning 'Default Player'.") # Suppressed message
                    df["player_name"] = "Default Player"

                df = df[["date", "value", "player_name"]].rename(columns={"value": "emboss_baseline_score"})
            else:
                # Keep error message for format issues
                st.error("❌ Uploaded file format not recognized. Required columns missing. "
                         "Ensure it has ('date', 'emboss_baseline_score') or ('metric', 'value', 'sessionDate').")
                return None

            # Final processing for uploaded data
            df['emboss_baseline_score'] = pd.to_numeric(df['emboss_baseline_score'], errors='coerce') # Ensure numeric
            df.dropna(subset=['date', 'emboss_baseline_score'], inplace=True) # Drop rows where essential data is missing
            df = df.sort_values("date")
            # st.success(f"✅ Successfully loaded data for {df['player_name'].nunique()} player(s).") # Suppressed message
            return df

        except Exception as e:
            # Keep critical error messages
            st.error(f"❌ Error processing uploaded file: {str(e)}")
            st.error("Please ensure the file is a valid CSV and check date formats.")
            return None
    else:
        # Load default data or generate sample data
        try:
            # Attempt to load default cleaned data
            df = pd.read_csv("cleaned_data/cleaned_CFC_Recovery_Status_Data.csv")
            df["date"] = pd.to_datetime(df["date"], errors='coerce')
            if "player_name" not in df.columns:
                df["player_name"] = "Default Player" # Should ideally not happen for the cleaned file
            df['emboss_baseline_score'] = pd.to_numeric(df['emboss_baseline_score'], errors='coerce') # Ensure numeric
            df.dropna(subset=['date', 'emboss_baseline_score'], inplace=True)
            df = df.sort_values("date")
            # st.info("Using default recovery dataset.") # Optional: Inform user - keep this commented
            return df
        except FileNotFoundError:
            # Keep warning if default is missing and synthetic is used
            # st.warning("⚠️ Default dataset not found. Generating synthetic data for demonstration.")
            return generate_sample_data() # Use default number of players
        except Exception as e:
            # Keep critical error messages
            st.error(f"❌ Error loading default data: {str(e)}")
            st.warning("Generating synthetic data as fallback.") # Keep this warning
            return generate_sample_data()


def calculate_rolling_average(df, window=7):
    """
    Calculate the rolling average of the 'emboss_baseline_score'.

    Parameters:
    df (DataFrame): Input DataFrame containing 'emboss_baseline_score'.
                    Assumes df is sorted by date for the player.
    window (int): The window size for the rolling average.

    Returns:
    DataFrame: The original DataFrame with an added 'rolling_avg' column.
               Returns the input df if it's None or empty.
    """
    if df is None or df.empty:
        return df

    df = df.copy() # Work on a copy

    # Ensure window is not larger than the dataframe length for calculation
    effective_window = min(window, len(df))
    if effective_window < 1: effective_window = 1 # Should not happen, but safe guard

    try:
        # Calculate rolling average, ensuring enough periods
        df['rolling_avg'] = df['emboss_baseline_score'].rolling(
            window=effective_window,
            min_periods=1 # Start calculating even if window isn't full
        ).mean()
    except Exception as e:
        st.warning(f"⚠️ Could not calculate rolling average smoothly: {e}. Using simple mean.")
        # Fallback: Calculate expanding mean if rolling fails (less ideal but functional)
        df['rolling_avg'] = df['emboss_baseline_score'].expanding(min_periods=1).mean()

    return df

def get_weekly_summary(df, risk_threshold):
    """
    Generate weekly summary statistics from the recovery data.

    Calculates mean, min, max, std dev, and risk days per week.
    Weeks are defined ending on Sunday.

    Parameters:
    df (DataFrame): DataFrame with 'emboss_baseline_score' and 'date' (datetime) columns.
    risk_threshold (float): Score threshold below which a day is considered a 'risk' day.

    Returns:
    DataFrame: DataFrame containing weekly summary statistics:
               'week_ending', 'mean', 'min', 'max', 'std', 'risk_days', 'days_in_week', 'risk_pct'.
               Returns an empty DataFrame if the input is empty.
    """

    if df is None or df.empty:
        return pd.DataFrame(columns=['week_ending', 'mean', 'min', 'max', 'std', 'risk_days', 'days_in_week', 'risk_pct'])

    df = df.copy()
    df['date'] = pd.to_datetime(df['date']) # Ensure correct dtype

    # Group by week ending on Sunday
    # 'W-SUN' ensures weeks end on Sunday. Using Grouper for robustness.
    weekly_agg = df.groupby(pd.Grouper(key='date', freq='W-SUN')).agg(
        mean=('emboss_baseline_score', 'mean'),
        min=('emboss_baseline_score', 'min'),
        max=('emboss_baseline_score', 'max'),
        std=('emboss_baseline_score', 'std'),
        days_in_week=('emboss_baseline_score', 'size') # Count number of entries per week
    ).reset_index() # Reset index to get 'date' (week ending) as a column

    weekly_agg.rename(columns={'date': 'week_ending'}, inplace=True)

    # Calculate risk days per week more efficiently
    df['is_risk_day'] = df['emboss_baseline_score'] < risk_threshold
    risk_days_per_week = df.groupby(pd.Grouper(key='date', freq='W-SUN'))['is_risk_day'].sum().reset_index()
    risk_days_per_week.rename(columns={'date': 'week_ending', 'is_risk_day': 'risk_days'}, inplace=True)

    # Merge aggregated stats with risk day counts
    weekly_summary = pd.merge(weekly_agg, risk_days_per_week, on='week_ending', how='left')
    weekly_summary['risk_days'] = weekly_summary['risk_days'].fillna(0).astype(int) # Fill NaNs if a week had no data

    # Calculate risk percentage
    weekly_summary['risk_pct'] = weekly_summary.apply(
        lambda row: (row['risk_days'] / row['days_in_week']) * 100 if row['days_in_week'] > 0 else 0,
        axis=1
    )

    # Fill std NaN for weeks with only one data point
    weekly_summary['std'] = weekly_summary['std'].fillna(0)

    return weekly_summary[['week_ending', 'mean', 'min', 'max', 'std', 'risk_days', 'days_in_week', 'risk_pct']]