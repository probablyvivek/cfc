# data_generator.py
"""
Functions for generating synthetic player recovery (EMBOSS score) data
for demonstration purposes, simulating realistic patterns like match impact,
fatigue periods, and player status differences. Adjusted to increase likelihood
of generating enough players for a typical matchday squad (11 ready, 5 bench).
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Consistent Player List and Positions (can be shared or kept separate)
SYNTHETIC_PLAYERS = {
    "Robert Sanchez": "GK", "Filip Jörgensen": "GK",
    "Reece James": "DEF", "Malo Gusto": "DEF", "Wesley Fofana": "DEF",
    "Trevoh Chalobah": "DEF", "Levi Colwill": "DEF", "Benoit Badiashile": "DEF",
    "Marc Cucurella": "DEF", "Josh Acheampong": "DEF",
    "Enzo Fernandez": "MID", "Moises Caicedo": "MID", "Romeo Lavia": "MID",
    "Kiernan Dewsbury-Hall": "MID",
    "Cole Palmer": "FWD", "Noni Madueke": "FWD", "Pedro Neto": "FWD",
    "Tyrique George": "FWD", "Nicolas Jackson": "FWD", "Christopher Nkunku": "FWD"
    # Add any other players if needed for num_players > 20
}
# Key players often playing more minutes or under higher scrutiny
KEY_PLAYERS_LIST = ["Cole Palmer", "Reece James", "Enzo Fernandez", "Moises Caicedo", "Nicolas Jackson", "Pedro Neto", "Levi Colwill", "Malo Gusto"]
# Players historically more prone to injury or needing careful load management
INJURY_PRONE_LIST = ["Romeo Lavia", "Wesley Fofana", "Reece James", "Christopher Nkunku", "Benoit Badiashile"]


def generate_sample_data(num_players=20, days=90):
    """
    Generate sample EMBOSS score data for a specified number of players over a period.

    Creates varied recovery patterns based on simulated player status.
    Adjusted percentages and score parameters aim to generate ~11+ 'Ready' players
    and ~5+ 'Bench' players according to team_readiness.py logic.

    Parameters:
    num_players (int): Number of players to generate data for (max based on SYNTHETIC_PLAYERS).
    days (int): Number of past days to generate data for.

    Returns:
    DataFrame: Sample data with columns 'date', 'emboss_baseline_score', 'player_name'.
    """
    today = datetime.now().date() # Use date only for consistency
    date_range = [today - timedelta(days=i) for i in range(days)]
    date_range.reverse() # Chronological order

    available_player_names = list(SYNTHETIC_PLAYERS.keys())
    if num_players > len(available_player_names):
        print(f"Warning: Requested {num_players} players, but only {len(available_player_names)} unique names available. Using max available.")
        num_players = len(available_player_names)

    # Randomly select players for the simulation
    players_to_simulate = np.random.choice(available_player_names, num_players, replace=False).tolist()

    all_data = []

    # --- Define Player Status Categories ---
    # NEW ALLOCATION: Increase Ready and Bench percentages
    shuffled_players = players_to_simulate.copy()
    np.random.shuffle(shuffled_players)

    # Target: ~11+ Ready/Optimal (>=65 score), ~5+ Bench/Limited (>=35 score) = 16 total available
    # Let's allocate generously to ensure we usually meet the target.
    num_ready = int(num_players * 0.65)     # ~65% Ready/Optimal (Target score > 0.2 -> Readiness ~65+)
    num_limited = int(num_players * 0.15)   # ~15% Limited (Target score ~0.0-0.2 -> Readiness ~50-65) - Can contribute to bench
    num_bench = int(num_players * 0.15)     # ~15% Bench (Target score ~-0.2-0.0 -> Readiness ~35-50)
    num_rest = num_players - num_ready - num_limited - num_bench # Remaining are 'Rest'

    ready_players = shuffled_players[:num_ready]
    limited_players = shuffled_players[num_ready : num_ready + num_limited]
    bench_players = shuffled_players[num_ready + num_limited : num_ready + num_limited + num_bench]
    rest_players = shuffled_players[num_ready + num_limited + num_bench:]

    # print(f"Generating data with target allocation: {len(ready_players)} Ready, {len(limited_players)} Limited, {len(bench_players)} Bench, {len(rest_players)} Rest players.") # Optional print

    for player_name in players_to_simulate:
        # Seed based on player name for consistent yet distinct patterns per player
        seed = sum(ord(c) for c in player_name)
        np.random.seed(seed)

        # --- Base Recovery Profile based on Status (ADJUSTED RANGES) ---
        if player_name in ready_players:
            # Target Readiness > 65 (often > 80) -> Need scores consistently > 0.2
            recovery_base = np.random.uniform(0.25, 0.55) # Higher base score range
            recovery_variance = np.random.uniform(0.08, 0.20) # Keep variance low for consistency
        elif player_name in limited_players:
            # Target Readiness 50-65 -> Need scores around 0.0 to 0.2
            recovery_base = np.random.uniform(0.0, 0.25) # Moderate base
            recovery_variance = np.random.uniform(0.15, 0.30) # Moderate variance
        elif player_name in bench_players:
            # Target Readiness 35-50 -> Need scores around -0.2 to 0.0
            recovery_base = np.random.uniform(-0.15, 0.05) # Lower base, overlapping slightly with limited
            recovery_variance = np.random.uniform(0.20, 0.35) # Moderate/higher variance
        else: # rest_players
            # Target Readiness < 35 -> Need scores consistently < -0.2
            recovery_base = np.random.uniform(-0.6, -0.25) # Low base score
            recovery_variance = np.random.uniform(0.20, 0.40) # Can be variable but generally low

        # Adjustments for specific player types (Keep similar logic)
        if player_name in KEY_PLAYERS_LIST and player_name in ready_players:
            recovery_base += 0.05
            recovery_variance *= 0.9
        if player_name in INJURY_PRONE_LIST and player_name not in ready_players:
             recovery_base -= 0.1
             recovery_variance += 0.05


        # Generate baseline scores
        base_scores = np.random.normal(recovery_base, recovery_variance, len(date_range))

        # --- Simulate Events and Patterns (Keep similar logic, maybe reduce fatigue severity slightly for Ready/Bench) ---
        pattern = np.zeros_like(base_scores)

        # Simulate match days
        match_days_indices = np.arange(5, days, 7)
        for md_index in match_days_indices:
            if md_index < len(pattern):
                # Impact slightly less severe for ready players
                if player_name in ready_players: match_impact = np.random.uniform(0.08, 0.20) # Reduced impact
                elif player_name in limited_players: match_impact = np.random.uniform(0.15, 0.35)
                elif player_name in bench_players: match_impact = np.random.uniform(0.20, 0.40)
                else: match_impact = np.random.uniform(0.30, 0.55)

                pattern[md_index] -= match_impact

                # Recovery curve (Ready recovers faster)
                if player_name in ready_players: recovery_speed = np.random.uniform(0.08, 0.18) # Slightly faster recovery
                elif player_name in limited_players: recovery_speed = np.random.uniform(0.05, 0.15)
                elif player_name in bench_players: recovery_speed = np.random.uniform(0.04, 0.12)
                else: recovery_speed = np.random.uniform(0.02, 0.10) # Slower recovery if less ready

                cumulative_recovery = 0
                for i in range(1, 4):
                    if md_index + i < len(pattern):
                        # Add recovery increment, ensuring it doesn't overshoot too much
                        daily_recovery = recovery_speed * np.random.uniform(0.8, 1.2) # Add some daily variance
                        cumulative_recovery += daily_recovery
                        # Apply recovery relative to the initial dip
                        pattern[md_index + i] += min(cumulative_recovery, match_impact * 1.1) # Allow slight overshoot


        # Simulate fatigue/minor issue periods
        # Reduce frequency/severity slightly for higher readiness groups
        if player_name in ready_players: num_issues = np.random.randint(0, 2)
        elif player_name in limited_players or player_name in bench_players: num_issues = np.random.randint(1, 3)
        else: num_issues = np.random.randint(2, 4) # More issues for Rest players

        for _ in range(num_issues):
            issue_start = np.random.randint(0, max(1, days - 20))
            issue_length = np.random.randint(3, 7)

            if player_name in ready_players: issue_severity = np.random.uniform(0.15, 0.30) # Less severe
            elif player_name in limited_players or player_name in bench_players: issue_severity = np.random.uniform(0.25, 0.50)
            else: issue_severity = np.random.uniform(0.40, 0.70) # More severe for Rest

            for i in range(issue_length):
                if issue_start + i < len(pattern):
                    recovery_factor = (i / issue_length) * 0.8
                    pattern[issue_start + i] -= issue_severity * (1 - recovery_factor)


        # Simulate recent status for specific groups (Keep similar logic)
        if player_name in rest_players or (player_name in INJURY_PRONE_LIST and player_name not in ready_players):
            recent_issue_start = days - np.random.randint(7, 14)
            recent_issue_length = np.random.randint(4, 7)
            recent_severity = np.random.uniform(0.4, 0.8)
            for i in range(recent_issue_length):
                 if recent_issue_start + i < len(pattern):
                    recovery_factor = (i / recent_issue_length) * 0.3 # Slow recovery
                    pattern[recent_issue_start + i] -= recent_severity * (1 - recovery_factor)

        # Ensure recent positive trend/scores for Ready players
        if player_name in ready_players:
            for i in range(min(10, days)): # Last 10 days
                if days - 1 - i >= 0:
                    # Add slight positive trend
                    pattern[days - 1 - i] += 0.005 * i
                    # Ensure score doesn't randomly dip too low recently
                    base_plus_pattern = base_scores[days - 1 - i] + pattern[days - 1 - i]
                    if base_plus_pattern < 0.15: # If score dips below 0.15 recently for ready player
                        pattern[days - 1 - i] += (0.15 - base_plus_pattern) # Nudge it back up


        # Combine base scores with patterns and clamp to [-1, 1]
        scores = np.clip(base_scores + pattern, -1.0, 1.0)

        # Final check: Floor recent scores for Ready players
        if player_name in ready_players:
             for i in range(min(5, days)): # Last 5 days
                 scores[days - 1 - i] = max(scores[days - 1 - i], np.random.uniform(0.2, 0.6)) # Ensure minimum recent score


        # Create player DataFrame
        player_df = pd.DataFrame({
            'date': pd.to_datetime(date_range), # Ensure datetime objects
            'emboss_baseline_score': scores,
            'player_name': player_name
        })
        all_data.append(player_df)

    # Combine all player data
    final_df = pd.concat(all_data, ignore_index=True)
    final_df['date'] = pd.to_datetime(final_df['date']) # Ensure datetime type again

    return final_df