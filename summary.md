# CFC Player Recovery & Readiness Hub

**Participant(s):** Vivek Tiwari
**Competition:** CFC Performance Insights Vizathon (17th March – 14th April 2025) — #CFCInsights  
**Focus Area:** Recovery Module

---

## 1. Introduction & Vizathon Context

This document outlines our submission for the CFC Performance Insights Vizathon. The challenge involved building a high-impact physical performance interface tailored for elite football players and coaching staff.

Our submission focuses on the **Recovery Module**, translating daily recovery data into actionable insights to enhance player management, reduce risk, and improve decision-making for training and match readiness.

---

## 2. Project Overview & Purpose

The **CFC Player Recovery & Readiness Hub** is an interactive web-based dashboard built using **Python** and **Streamlit**. It is designed for use by coaches, physiotherapists, and sports science staff to:

- Visualize player recovery trends effectively  
- Detect early signs of fatigue or sub-optimal recovery  
- Inform training load adjustments using data-driven insights  
- Evaluate match readiness and assist in optimal squad selection  
- Centralize recovery monitoring for improved team-wide decisions

The tool centers around the **EMBOSS** metric (Enhanced Monitoring of Baseline Output Status Scores) included in the competition dataset.

---

## 3. Key Features

The dashboard includes two primary user-selectable views:

### a) Individual Player Analysis

- **Deep Dive:** Detailed breakdown of a selected player’s recovery over custom time windows (Last 7, 14, 30, 90 days, or All Time)
- **Summary Metrics:** Snapshot of key indicators like Average Score, Recent Average, Risk Days, and Risk Percentage
- **Interactive Recovery Trend Chart:** Daily EMBOSS score visualization with:
  - Risk status color coding
  - Optional rolling average
  - Customizable threshold line
- **Weekly Summary Chart:** Aggregated weekly average scores, min/max ranges, and number of risk days
- **Analysis & Recommendations Panel:**
  - Recovery status classification (Optimal, Moderate Risk, High Risk) based on 7-day data
  - Actionable, tiered recommendations tailored to current status
  - Key 7-day metrics: Average, Min, Trend, Variability, Risk Days
  - Additional insights like best/worst recovery day and consistency score

### b) Team Readiness View

- **Squad Overview:** High-level readiness snapshot for the entire team
- **Readiness Score (0–100):** Composite score using the past 7 days of EMBOSS data, factoring in:
  - Latest score
  - 7-day average
  - Trend direction
  - Score variability
  - Number of risk days
- **Automated Starting XI Suggestion:** Intelligent selection based on:
  - Readiness scores
  - Positional requirements (GK, DEF, MID, FWD)
- **Bench & Availability Tabs:** Clear listing of:
  - Substitute candidates
  - Players unavailable due to rest, data issues, or low readiness
- **Summary Metrics:**
  - Player counts by status (Optimal, Ready, Limited, Bench, Rest, Unknown)
  - Average readiness of the suggested Starting XI
- **Readiness Comparison Chart:** Horizontal bar chart comparing readiness across the squad with color-coded status
- **Player Cards:** Compact visuals showing:
  - Player name and position/status
  - Readiness score (%)
  - Trend icon (up, down, stable)
  - Hover-enabled detailed metrics

---

## 4. Technical Stack

The dashboard was developed entirely using **Python**, with the following libraries:

- **Streamlit**: Web app framework for rapid dashboard development  
- **Pandas**: Data manipulation and transformation  
- **NumPy**: Numerical computations  
- **Plotly**: Interactive plotting and charting  
- **Matplotlib**: Utility functions including color processing  

Streamlit was chosen to enable fast iteration and intuitive UI development within the vizathon timeline.

---

## 5. Data Handling

- Primary metric: **emboss_baseline_score** (range: -1.0 to +1.0)  
- Accepts user-uploaded CSV data (specific formats supported)  
- Defaults to `cleaned_data/cleaned_CFC_Recovery_Status_Data.csv` if available  
- If no data is provided, synthetic demo data can be generated  
- The **Recovery Risk Threshold** is user-configurable via a sidebar slider

---
