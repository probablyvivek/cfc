# analysis.py
"""
Functions for analyzing player recovery data.
"""

def get_recommendations(recent_data, risk_threshold):
    """
    Generate recommendations based on recovery status
    
    Parameters:
    recent_data (DataFrame): Recent recovery data (typically last 7 days)
    risk_threshold (float): Threshold for determining risk level
    
    Returns:
    dict: Dictionary with status, title, recommendations, and metrics
    """
    below_threshold = (recent_data['emboss_baseline_score'] < risk_threshold).sum()
    recent_avg = recent_data['emboss_baseline_score'].mean()
    recent_min = recent_data['emboss_baseline_score'].min()
    
    if below_threshold >= 3:
        status = "high_risk"
        title = "⚠️ High Risk: Recovery Intervention Needed"
        recommendations = [
            "Implement full recovery protocol for 48 hours",
            "Reduce training intensity by 40-50%",
            "Focus on sleep quality (8+ hours) and hydration",
            "Schedule recovery session with physiotherapy team",
            "Consider sitting out next training session if no improvement"
        ]
    elif below_threshold >= 1:
        status = "moderate_risk"
        title = "🟠 Moderate Risk: Modified Training Recommended"
        recommendations = [
            "Reduce training intensity by 20-30%",
            "Increase recovery time between sessions",
            "Emphasize proper nutrition and hydration",
            "Additional focus on sleep quality",
            "Monitor symptoms closely during next session"
        ]
    else:
        status = "optimal"
        title = "✅ Optimal: Continue Current Program"
        recommendations = [
            "Maintain current training load",
            "Continue regular recovery protocols",
            "Optimize nutrition for performance",
            "Regular monitoring of recovery metrics",
            "Prepare for potential increase in intensity if suitable"
        ]
    
    return {
        'status': status,
        'title': title,
        'recommendations': recommendations,
        'metrics': {
            'below_threshold': below_threshold,
            'recent_avg': recent_avg,
            'recent_min': recent_min
        }
    }