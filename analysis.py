# analysis.py
"""
Functions for analyzing player recovery data, providing physiotherapist-grade
recommendations based on recent EMBOSS scores and patterns.
"""
import pandas as pd
import numpy as np

def get_recommendations(recent_data, risk_threshold):
    """
    Generate recovery recommendations based on recent EMBOSS scores.

    Analyzes the last 7 days of data to assess risk level (optimal, moderate, high)
    based on scores below threshold, average score, trend, and variability.
    Provides tailored recommendations for training modification, recovery protocols,
    and monitoring.

    Parameters:
    recent_data (DataFrame): DataFrame of the last 7 days of recovery data for a player.
                             Requires 'emboss_baseline_score' and 'date' columns.
    risk_threshold (float): The EMBOSS score threshold indicating potential risk.

    Returns:
    dict: A dictionary containing:
        'status' (str): 'optimal', 'moderate_risk', or 'high_risk'.
        'title' (str): A summary title with an indicator emoji.
        'recommendations' (list): A list of specific recommendation strings.
        'metrics' (dict): Key metrics used for the analysis:
            'below_threshold' (int): Count of days score was below threshold.
            'recent_avg' (float): Average score over the period.
            'recent_min' (float): Minimum score over the period.
            'trend' (float): Score trend (latter half avg - first half avg).
            'variability' (float): Standard deviation of scores over the period.
    """
    if recent_data is None or recent_data.empty or len(recent_data) < 3: # Need at least 3 days
        status = 'unknown'
        title = '⚪ Insufficient Recent Data'
        recommendations = ['Collect more daily data (min 3 days) for analysis.']
        metrics = {'below_threshold': 0, 'recent_avg': np.nan, 'recent_min': np.nan, 'trend': 0, 'variability': 0}
        if recent_data is not None and not recent_data.empty:
             metrics['recent_avg'] = recent_data['emboss_baseline_score'].mean()
             metrics['recent_min'] = recent_data['emboss_baseline_score'].min()
             metrics['below_threshold'] = (recent_data['emboss_baseline_score'] < risk_threshold).sum()

        return {
            'status': status, 'title': title,
            'recommendations': recommendations, 'metrics': metrics
        }


    # Calculate metrics
    below_threshold = (recent_data['emboss_baseline_score'] < risk_threshold).sum()
    recent_avg = recent_data['emboss_baseline_score'].mean()
    recent_min = recent_data['emboss_baseline_score'].min()

    # Calculate trend (comparing first vs. second half of the period)
    trend = 0
    n_days = len(recent_data)
    if n_days >= 4:
        first_half_avg = recent_data.iloc[:n_days//2]['emboss_baseline_score'].mean()
        second_half_avg = recent_data.iloc[n_days//2:]['emboss_baseline_score'].mean()
        trend = second_half_avg - first_half_avg

    # Calculate variability (standard deviation)
    variability = recent_data['emboss_baseline_score'].std() if n_days > 1 else 0

    # --- Determine Status and Recommendations ---
    # NOTE: Recommendations are examples and should be adapted by qualified staff.

    # High Risk Conditions
    if below_threshold >= 3 or recent_min < (risk_threshold - 0.3) or (below_threshold >= 2 and trend < -0.15):
        status = "high_risk"
        title = "⚠️ High Risk: Intervention Required"
        # Sub-categorize high risk based on patterns
        if recent_min < (risk_threshold - 0.4) or (below_threshold >= 4):
             recommendations = [
                "Significant load reduction (e.g., 50-70%) or complete rest for 24-48h.",
                "Prioritize passive recovery: extended sleep, low-intensity active recovery (walk, swim).",
                "Implement targeted recovery modalities (e.g., contrast baths, compression).",
                "Medical/Physio assessment strongly advised to rule out injury/illness.",
                "Focus on nutrition: adequate hydration, protein, anti-inflammatory foods.",
                "Monitor closely, potentially twice daily, before resuming graded activity."
            ]
        elif variability > 0.35: # High inconsistency
            recommendations = [
                "Moderate load reduction (e.g., 30-50%), focus on consistency.",
                "Standardize daily routines: sleep/wake times, meal times.",
                "Implement consistent pre- and post-training recovery protocols.",
                "Assess potential external stressors (travel, sleep environment, life stress).",
                "Consider subjective wellness questionnaires alongside EMBOSS.",
                "Gradual return to load once scores stabilize in a better range."
             ]
        else: # Cumulative fatigue likely
             recommendations = [
                "Moderate-to-Significant load reduction (e.g., 40-60%).",
                "Introduce a full recovery day or very light active recovery.",
                "Emphasize sleep quality and duration (aim for 8-10 hours).",
                "Consider manual therapy or targeted mobility work.",
                "Ensure adequate caloric and macronutrient intake for recovery.",
                "Plan next training block carefully to avoid recurrence."
            ]

    # Moderate Risk Conditions - Adjusted average check
    elif below_threshold >= 1 or recent_avg < (risk_threshold + 0.05) or (trend < -0.1 and recent_avg < (risk_threshold + 0.15)):
        status = "moderate_risk"
        title = "🟠 Moderate Risk: Caution Advised"
        if trend < -0.1: # Declining trend
            recommendations = [
                "Reduce training intensity/volume by 20-30% for the next 1-2 sessions.",
                "Ensure adequate recovery time between high-intensity stimuli.",
                "Increase focus on post-session recovery (nutrition timing, cool-down).",
                "Monitor response to next session closely.",
                "Reinforce importance of sleep and hydration.",
                "Consider slightly longer warm-up/activation routines."
            ]
        elif variability > 0.25: # Moderate inconsistency
             recommendations = [
                "Maintain overall load but adjust daily based on readiness (score, subjective).",
                "Reinforce consistent application of recovery strategies.",
                "Review nutrition and hydration habits for consistency.",
                "Encourage consistent sleep patterns.",
                "Monitor for developing negative trends.",
                "Emphasize pre-session preparation (mobility, activation)."
            ]
        else: # Generally moderate risk
            recommendations = [
                "Slight reduction in training load (e.g., 15-25%) or modify session goals.",
                "Pay extra attention to recovery protocols (e.g., stretching, foam rolling).",
                "Prioritize sleep hygiene.",
                "Ensure adequate carbohydrate intake around training.",
                "Monitor subjective feelings (soreness, fatigue, mood).",
                "Be prepared to adjust load further if scores don't improve."
            ]

    # Optimal Conditions
    else:
        status = "optimal"
        title = "✅ Optimal: Ready for Training"
        if trend > 0.15 and recent_avg > 0.2: # Strong positive trend
             recommendations = [
                "Maintain current training load or consider progressive overload (5-10% increase).",
                "Continue effective recovery strategies.",
                "Reinforce positive habits contributing to good recovery.",
                "Monitor closely if increasing load to ensure recovery sustains.",
                "Opportunity for technical/tactical focus during high readiness.",
                "Ensure nutrition supports adaptation to training."
            ]
        else: # Stable optimal
             recommendations = [
                "Continue with planned training program.",
                "Maintain consistent recovery routines.",
                "Focus on optimizing nutrition and sleep for performance.",
                "Monitor daily scores to catch any negative changes early.",
                "Regularly review recovery effectiveness.",
                "Ensure readiness for planned training intensities."
            ]

    return {
        'status': status,
        'title': title,
        'recommendations': recommendations,
        'metrics': {
            'below_threshold': below_threshold,
            'recent_avg': recent_avg,
            'recent_min': recent_min,
            'trend': trend,
            'variability': variability
        }
    }