# analysis.py
"""
Functions for analyzing player recovery data with advanced physiotherapy
and workload management principles.
"""

def get_recommendations(recent_data, risk_threshold):
    """
    Generate physiotherapist-grade recommendations based on recovery status,
    including workload management, recovery protocols, and return-to-play guidance.
    
    Parameters:
    recent_data (DataFrame): Recent recovery data (typically last 7 days)
    risk_threshold (float): Threshold for determining risk level
    
    Returns:
    dict: Dictionary with status, title, recommendations, and metrics
    """
    below_threshold = (recent_data['emboss_baseline_score'] < risk_threshold).sum()
    recent_avg = recent_data['emboss_baseline_score'].mean() if not recent_data.empty else 0
    recent_min = recent_data['emboss_baseline_score'].min() if not recent_data.empty else 0
    
    # Calculate trend using first half vs second half of data
    if len(recent_data) >= 4:
        first_half = recent_data.iloc[:len(recent_data)//2]['emboss_baseline_score'].mean()
        second_half = recent_data.iloc[len(recent_data)//2:]['emboss_baseline_score'].mean()
        trend = second_half - first_half
    else:
        trend = 0
    
    # Calculate variability (as a physiological marker of recovery instability)
    variability = recent_data['emboss_baseline_score'].std() if len(recent_data) > 1 else 0
    
    # Assess severity by considering various factors
    if below_threshold >= 3 or recent_min < risk_threshold - 0.3 or (below_threshold >= 2 and trend < -0.1):
        status = "high_risk"
        title = "⚠️ High Risk: Recovery Intervention Needed"
        
        # Determine specific high-risk scenario for targeted recommendations
        if recent_min < risk_threshold - 0.4:
            # Acute fatigue scenario
            recommendations = [
                "Immediate 48-hour recovery protocol (passive recovery)",
                "Reduce training load by 50-60%, focus on technique over intensity",
                "Implement contrast therapy (3:1 cold:hot) and compression therapy",
                "Schedule assessment with medical staff to rule out underlying issues",
                "Emphasize sleep hygiene: 9+ hours with pre-sleep routine",
                "Increase protein intake to 1.8-2.0g/kg body weight to support recovery"
            ]
        elif variability > 0.3:
            # High variability scenario (inconsistent recovery)
            recommendations = [
                "Implement 36-hour modified recovery protocol",
                "Reduce intensity by 40%, emphasize steady-state over interval work",
                "Focus on sleep consistency (regular sleep/wake times)",
                "Implement daily recovery monitoring with morning readiness assessment",
                "Schedule physiotherapy for targeted recovery techniques",
                "Adjust nutrition timing: increase pre/post session carbohydrate window"
            ]
        else:
            # Cumulative fatigue scenario
            recommendations = [
                "Implement full recovery protocol for 48-72 hours",
                "Reduce training volume by 40-50%, remove high-intensity components",
                "Prioritize sleep quality enhancement and aim for 8-9 hours",
                "Schedule manual therapy session with physiotherapy team",
                "Consider lower-body unloading techniques (pool-based recovery)",
                "Implement detailed recovery diary with 3x daily monitoring"
            ]
    
    elif below_threshold >= 1 or recent_avg < risk_threshold + 0.15 or (trend < -0.05 and recent_avg < 0):
        status = "moderate_risk"
        title = "🟠 Moderate Risk: Modified Training Recommended"
        
        # Determine specific moderate-risk scenario
        if trend < -0.1:
            # Declining trend scenario
            recommendations = [
                "Reduce training volume by 20-30% for next 2-3 sessions",
                "Implement recovery-focused day between high-intensity sessions",
                "Increase emphasis on tissue preparation (targeted mobility work)",
                "Adjust carbohydrate intake timing around training sessions",
                "Focus on quality sleep (8+ hours) with 30-min pre-sleep routine",
                "Monitor morning HRV and subjective readiness scores"
            ]
        elif variability > 0.2:
            # Moderate variability scenario
            recommendations = [
                "Modify training intensity by 15-25% based on daily readiness",
                "Implement structured recovery protocols between sessions",
                "Focus on nutrition consistency and hydration timing",
                "Incorporate targeted mobility work for primary muscle groups",
                "Establish consistent sleep/wake cycle with 7.5-8.5 hours of sleep",
                "Monitor subjective wellness scores daily (fatigue, soreness, mood)"
            ]
        else:
            # General moderate risk scenario
            recommendations = [
                "Reduce training intensity by 20-25% for next 2 sessions",
                "Increase recovery time between high-intensity exposures",
                "Emphasize nutrition timing and 30-30-30 macronutrient distribution",
                "Prioritize sleep quality improvements and consistent timing",
                "Implement specific mobility protocols pre/post training",
                "Monitor symptoms closely during next training block"
            ]
    
    else:
        status = "optimal"
        title = "✅ Optimal: Continue Current Program"
        
        # Determine specific optimal scenario
        if trend > 0.1:
            # Improving trend scenario
            recommendations = [
                "Maintain current training load with option to progress 5-10%",
                "Continue proactive recovery protocols between sessions",
                "Focus on nutrition quality and timing for performance",
                "Maintain consistent sleep hygiene practices",
                "Consider additional technical development during good recovery periods",
                "Document effective recovery strategies in player profile"
            ]
        elif recent_avg > 0.3:
            # Excellent recovery scenario
            recommendations = [
                "Opportunity to introduce progressive overload (10-15%)",
                "Maintain recovery protocols with focus on proactive strategies",
                "Consider introducing new training stimuli during this window",
                "Optimize nutrition for performance and adaptation",
                "Maintain sleep quality while potentially increasing training volume",
                "Document key performance indicators during optimal recovery phases"
            ]
        else:
            # General optimal scenario
            recommendations = [
                "Maintain current training progression with daily monitoring",
                "Continue consistent recovery routines between sessions",
                "Focus on nutrition quality and fueling for performance",
                "Maintain sleep consistency and quality (7-9 hours)",
                "Regular monitoring of recovery metrics with weekly review",
                "Prepare for potential increase in training load if recovery sustains"
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

def analyze_workload_progression(player_data, current_week_data, risk_threshold):
    """
    Analyze workload progression and make recommendations for future training loads
    
    Parameters:
    player_data (DataFrame): Complete player history data
    current_week_data (DataFrame): Data from current week only
    risk_threshold (float): Risk threshold value
    
    Returns:
    dict: Workload analysis and recommendations
    """
    # Get recent 4 weeks of data for acute:chronic ratio
    if len(player_data) < 28:
        return {
            "status": "insufficient_data",
            "title": "⚠️ Insufficient Data for Workload Analysis",
            "message": "At least 4 weeks of data required for workload analysis",
            "recommendations": [
                "Continue collecting daily recovery data",
                "Use RPE and training load metrics to supplement recovery data",
                "Focus on establishing baseline recovery patterns"
            ]
        }
    
    # Calculate acute (1 week) vs chronic (4 week) workload ratio
    recent_4_weeks = player_data.tail(28)
    acute_load = player_data.tail(7)['emboss_baseline_score'].mean()
    chronic_load = recent_4_weeks['emboss_baseline_score'].mean()
    
    # Avoid division by zero
    acwr = acute_load / chronic_load if chronic_load != 0 else 1.0
    
    # Calculate week-to-week changes
    if len(player_data) >= 14:
        previous_week = player_data.iloc[-14:-7]['emboss_baseline_score'].mean()
        week_change = acute_load - previous_week
    else:
        week_change = 0
    
    # Analyze workload status
    if acwr > 1.5:
        return {
            "status": "high_spike",
            "title": "⚠️ High Acute:Chronic Workload Ratio",
            "acwr": acwr,
            "week_change": week_change,
            "recommendations": [
                "Reduce training load by 15-20% for next 3-5 days",
                "Implement 'acute recovery' protocol to manage spike",
                "Increase recovery monitoring frequency to twice daily",
                "Gradually return to normal loading with max 5-10% increases",
                "Review training design to avoid future load spikes"
            ]
        }
    elif acwr < 0.8:
        return {
            "status": "detraining_risk",
            "title": "⚙️ Low Acute:Chronic Workload Ratio",
            "acwr": acwr,
            "week_change": week_change,
            "recommendations": [
                "Progressively increase load by 5-10% per session",
                "Focus on maintaining neuromuscular readiness with activation work",
                "Implement progressive loading strategy over next 7-10 days",
                "Monitor tissue resilience during load increase phase",
                "Emphasize quality movement patterns during rebuilding phase"
            ]
        }
    else:
        return {
            "status": "optimal_progression",
            "title": "✅ Balanced Workload Progression",
            "acwr": acwr,
            "week_change": week_change,
            "recommendations": [
                "Maintain current loading strategy with consistent progression",
                "Continue with planned periodization model",
                "Monitor for early signs of fatigue accumulation",
                "Focus on optimizing recovery between training stimuli",
                "Document effective loading patterns for future reference"
            ]
        }