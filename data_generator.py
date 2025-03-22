# data_generator.py
"""
Functions for generating synthetic training data for demonstration purposes.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_sample_data(num_players=10):
    """
    Generate sample data for demonstration with multiple players
    
    Parameters:
    num_players (int): Number of players to generate data for
    
    Returns:
    DataFrame: Sample data with player information
    """
    # Create a range of dates (90 days)
    today = datetime.now()
    date_range = [today - timedelta(days=i) for i in range(90)]
    date_range.reverse()  # Start from earliest date
    
    # Player names - mix of real Chelsea players and fictional names
    player_names = [
        "Reece James", 
        "Cole Palmer", 
        "Enzo Fernandez", 
        "Moises Caicedo", 
        "Nicolas Jackson", 
        "Romeo Lavia", 
        "Wesley Fofana", 
        "Noni Madueke", 
        "Christopher Nkunku",
        "Marc Cucurella",
        "Malo Gusto",
        "Levi Colwill"
    ]
    
    # Select a subset of players if requested fewer than available names
    if num_players < len(player_names):
        players = player_names[:num_players]
    else:
        players = player_names
    
    # Generate data for each player
    all_data = []
    
    for player in players:
        # Seed based on player name for consistent but different patterns
        seed = sum(ord(c) for c in player)
        np.random.seed(seed)
        
        # Base personality traits affect recovery patterns
        recovery_base = np.random.uniform(-0.1, 0.2)  # Some players naturally recover better
        recovery_variance = np.random.uniform(0.3, 0.5)  # Some players have more consistent recovery
        
        # Generate realistic EMBOSS scores with some patterns
        base_scores = np.random.normal(recovery_base, recovery_variance, len(date_range))
        
        # Add some realistic patterns (drops after match days)
        pattern = np.zeros_like(base_scores)
        
        # Simulate match days and recovery patterns
        match_days = [5, 12, 19, 26, 33, 40, 47, 54, 61, 68, 75, 82]
        for match_day in match_days:
            if match_day < len(pattern):
                # Some players are affected more by matches
                match_impact = np.random.uniform(0.3, 0.6)
                pattern[match_day] = -match_impact
                
                # Recovery pattern over next 3-4 days
                recovery_speed = np.random.uniform(0.1, 0.2)  # Some players recover faster
                for i in range(1, 4):
                    if match_day + i < len(pattern):
                        pattern[match_day + i] = -match_impact + i * recovery_speed
        
        # Add some random minor injuries or fatigue periods
        num_issues = np.random.randint(1, 4)
        for _ in range(num_issues):
            issue_start = np.random.randint(0, len(pattern) - 10)
            issue_length = np.random.randint(3, 7)
            issue_severity = np.random.uniform(0.3, 0.7)
            
            for i in range(issue_length):
                if issue_start + i < len(pattern):
                    # Recovery pattern from the issue
                    pattern[issue_start + i] = -issue_severity + (i/issue_length) * issue_severity
        
        # Combine base and pattern
        scores = np.clip(base_scores + pattern, -1, 1)
        
        # Create player specific dataframe
        player_df = pd.DataFrame({
            'date': pd.to_datetime(date_range),
            'emboss_baseline_score': scores,
            'player_name': player
        })
        
        all_data.append(player_df)
    
    # Combine all player data
    df = pd.concat(all_data, ignore_index=True)
    
    # Ensure the date column is properly formatted as datetime
    df['date'] = pd.to_datetime(df['date'])
    
    return df