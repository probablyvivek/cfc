
"""
Functions for generating synthetic training data for demonstration purposes.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_sample_data(num_players=24):
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
    date_range.reverse()  
    
    # Player names - Chelsea players and squad members
    player_names = [
        "Robert Sanchez", 
        "Filip Jörgensen",
        "Reece James", 
        "Malo Gusto",
        "Wesley Fofana",
        "Trevoh Chalobah",
        "Levi Colwill",
        "Benoit Badiashile",
        "Marc Cucurella",
        "Josh Acheampong",
        "Enzo Fernandez",
        "Moises Caicedo", 
        "Romeo Lavia",
        "Kiernan Dewsbury-Hall", 
        "Cole Palmer",          
        "Noni Madueke", 
        "Pedro Neto",
        "Tyrique George",
        "Nicolas Jackson",
        "Christopher Nkunku"
    ]
    
    # Select a subset of players if requested fewer than available names
    if num_players < len(player_names):
        players = player_names[:num_players]
    else:
        players = player_names
    
    # Generate data for each player
    all_data = []
    
    # 60% of players will be in optimal or ready condition (higher baseline recovery)
    ready_players = np.random.choice(players, int(len(players) * 0.6), replace=False).tolist()
    
    # 25% will be in limited minutes condition
    limited_players = []
    for player in players:
        if player not in ready_players and len(limited_players) < int(len(players) * 0.25):
            limited_players.append(player)
    
    # 10% will be in bench condition (not ideal recovery but can play)
    bench_players = []
    for player in players:
        if player not in ready_players and player not in limited_players and len(bench_players) < int(len(players) * 0.1):
            bench_players.append(player)
    
    # Remaining players will be in rest/recovery condition
    rest_players = []
    for player in players:
        if player not in ready_players and player not in limited_players and player not in bench_players:
            rest_players.append(player)
    
    # Add specific players to injury-prone list
    injury_prone_players = ["Romeo Lavia", "Wesley Fofana"]
    
    for player in players:
        # Seed based on player name for consistent but different patterns
        seed = sum(ord(c) for c in player)
        np.random.seed(seed)
        
        # Adjust base recovery traits based on player group
        if player in ready_players:
            # Higher base and lower variance for optimal/ready players
            recovery_base = np.random.uniform(0.1, 0.4)
            recovery_variance = np.random.uniform(0.1, 0.3)
        elif player in limited_players:
            # Moderate base and moderate variance
            recovery_base = np.random.uniform(-0.1, 0.2)
            recovery_variance = np.random.uniform(0.2, 0.4)
        elif player in bench_players:
            # Lower base but could be improving
            recovery_base = np.random.uniform(-0.2, 0.0)
            recovery_variance = np.random.uniform(0.3, 0.5)
        else:
            # Poor recovery for rest players
            recovery_base = np.random.uniform(-0.4, -0.2)
            recovery_variance = np.random.uniform(0.3, 0.5)
        
        # Add player-specific tendencies (key players might have different patterns)
        key_players = ["Cole Palmer", "Reece James", "Enzo Fernandez", "Moises Caicedo", "Nicolas Jackson", "Pedro Neto"]
        if player in key_players and player in ready_players:
            # Key ready players show even better baseline recovery
            recovery_base += 0.1
            recovery_variance -= 0.05
        
        # Generate baseline scores
        base_scores = np.random.normal(recovery_base, recovery_variance, len(date_range))
        
        # Add recovery patterns
        pattern = np.zeros_like(base_scores)
        
        # Simulate match days and recovery patterns
        match_days = [5, 12, 19, 26, 33, 40, 47, 54, 61, 68, 75, 82]
        for match_day in match_days:
            if match_day < len(pattern):
                # Match impact varies by player category
                if player in ready_players:
                    match_impact = np.random.uniform(0.1, 0.3)  # Less impact on ready players
                elif player in limited_players:
                    match_impact = np.random.uniform(0.2, 0.4)
                else:
                    match_impact = np.random.uniform(0.3, 0.5)  # More impact on less recovered players
                
                pattern[match_day] = -match_impact
                
                # Recovery pattern over next 3-4 days
                # Ready players recover faster
                if player in ready_players:
                    recovery_speed = np.random.uniform(0.15, 0.25)
                elif player in limited_players:
                    recovery_speed = np.random.uniform(0.1, 0.2)
                else:
                    recovery_speed = np.random.uniform(0.05, 0.15)
                
                for i in range(1, 4):
                    if match_day + i < len(pattern):
                        pattern[match_day + i] = -match_impact + i * recovery_speed
        
        # Add minor fatigue periods for all players
        num_issues = np.random.randint(1, 2) if player in ready_players else np.random.randint(2, 3)
        for _ in range(num_issues):
            # Place fatigue periods mostly in the past, not recent
            issue_start = np.random.randint(0, len(pattern) - 20)
            issue_length = np.random.randint(2, 5) if player in ready_players else np.random.randint(3, 7)
            
            # Severity varies by player group
            if player in ready_players:
                issue_severity = np.random.uniform(0.2, 0.5)
            elif player in limited_players:
                issue_severity = np.random.uniform(0.3, 0.6)
            else:
                issue_severity = np.random.uniform(0.4, 0.7)
            
            for i in range(issue_length):
                if issue_start + i < len(pattern):
                    # Recovery pattern from the issue
                    recovery_rate = (i/issue_length) * (0.8 if player in ready_players else 0.6)
                    pattern[issue_start + i] = -issue_severity + recovery_rate * issue_severity
        
        # Add improving trend for some ready players in last 10-14 days
        if player in ready_players and np.random.random() < 0.7:
            for i in range(10, 0, -1):
                if len(pattern) - i >= 0:
                    pattern[len(pattern) - i] += 0.05 * (10 - i) / 10
        
        # Add recent injury for injury-prone players
        if player in injury_prone_players and player not in ready_players:
            # Add recent injury or fatigue concern in the last 10 days
            issue_start = len(pattern) - np.random.randint(5, 10)
            issue_length = np.random.randint(3, 6)
            issue_severity = np.random.uniform(0.5, 0.9)
            
            for i in range(issue_length):
                if issue_start + i < len(pattern):
                    # Severe drop with slow recovery
                    recovery_rate = i/issue_length * 0.4  # Very slow recovery
                    pattern[issue_start + i] = -issue_severity + recovery_rate * issue_severity
        
        # Ensure players in rest condition have poor recent scores
        if player in rest_players:
            # Add very recent fatigue/injury in the last 3-7 days
            issue_start = len(pattern) - np.random.randint(3, 7)
            issue_length = np.random.randint(3, 5)
            issue_severity = np.random.uniform(0.6, 0.9)
            
            for i in range(issue_length):
                if issue_start + i < len(pattern):
                    # Severe drop with minimal recovery
                    recovery_rate = i/issue_length * 0.3
                    pattern[issue_start + i] = -issue_severity + recovery_rate * issue_severity
        
        # Combine base and pattern
        scores = np.clip(base_scores + pattern, -1, 1)
        
        # For ready players, ensure the most recent days have good scores
        if player in ready_players:
            for i in range(1, 6):  # Last 5 days
                if len(scores) - i >= 0:
                    # Ensure recent scores are positive for ready players
                    scores[len(scores) - i] = max(scores[len(scores) - i], np.random.uniform(0.2, 0.6))
        
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