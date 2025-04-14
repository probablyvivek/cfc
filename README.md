
# CFC Player Recovery & Readiness Hub 

---

## 1. The Vizathon Challenge

This project is an entry for the **[CFC Performance Insights Vizathon](https://chelsea-fc-performance-insights.github.io/Competition/index.html)** (17th March - 14th April 2025).

The challenge: Create the most compelling **Physical Performance interface** for elite football players and their coaches, showcasing innovative design, technical mastery, and user-focused thinking.

![Modules Overview](https://github.com/probablyvivek/cfc/blob/main/images/Modules.png?raw=true)

## 2. Our Focus: The Recovery Module

Our entry specifically targets the **Recovery** module.

![Recovery Module Focus](https://github.com/probablyvivek/cfc/blob/main/images/Recovery.png?raw=True)

**Objective:** Track **how well players recover** after high-intensity sessions & optimize readiness for future matches using data to drive smarter coaching decisions and behavioral nudges.

### Recovery Data & Key Metrics

The dashboard primarily utilizes the provided recovery dataset, focusing on metrics indicating recovery status across various categories:

*   **Categories:** Biomarkers (`bio`), Joint Range (`msk_joint_range`), Muscle Load Tolerance (`msk_load_tolerance`), Subjective Perception (`subjective`), Muscle Soreness (`soreness`), Sleep Quality (`sleep`).
*   **Metrics per Category:**
    *   `_completeness`: Percentage of completed tests (0–100%).
    *   `_composite`: Score relative to player’s norm (e.g., -0.5 = 50% below usual level).
*   **Overall Aggregated Metric:**
    *   `emboss_baseline_score`: A single score (ranging -1.0 to +1.0) summarizing overall recovery across all categories. This is the central metric used throughout the dashboard.
        *   **Positive Scores (> 0.2):** Generally good recovery.
        *   **Scores Around Zero (0 to 0.2):** Normal/stable state.
        *   **Negative Scores (< 0):** Potential fatigue/incomplete recovery.

![Recovery Data Fields](https://github.com/probablyvivek/cfc/blob/main/images/RecoveryData.png?raw=True)

## 3. Our Solution: The CFC Recovery Insights Dashboard

We developed an interactive web application using **Streamlit** to provide coaches, sports scientists, and physiotherapists with actionable insights derived from the EMBOSS recovery score.

**Core Purpose:**

*   Translate raw recovery scores into clear visual trends and status assessments.
*   Facilitate informed decisions on **Training Load Management**.
*   Aid in **Injury Prevention** by flagging risk indicators.
*   Support **Match Day Readiness** assessment and squad planning.
*   Provide a platform to monitor **Recovery Strategy Effectiveness**.

## 4. Key Features

The dashboard offers two primary views:
---

## a) Individual Player Analysis

### 📊 Detailed View
- Deep-dive into a selected player's recovery over custom time periods: **7, 14, 30, 90 days, All Time**

### 🔢 Metric Cards
- **Avg Score:** Average EMBOSS score over selected period  
- **Recent Avg:** Avg over the last 7 days  
- **Days Below Risk Threshold:** Count of risk days  
- **Risk %:** Percentage of days below threshold  

### 📈 Recovery Trend Chart
- Interactive daily **EMBOSS score plot**  
- Color-coded by **risk status**  
- Optional **rolling average** overlay  
- **Configurable risk threshold** line  

### 📅 Weekly Summary Chart
- Aggregated weekly view  
- Shows **average scores**, **min/max range**, and **risk day counts**

### 💡 Analysis & Recommendations Panel
- **Overall status assessment:** Based on last 7 days  
  - Optimal
  - Moderate Risk
  - High Risk  
- **Key 7-day Metrics:**
  - Avg, Min, Risk Days, Trend, Variability  
- **Tiered Recommendations:** Personalized intervention suggestions  
- **Additional Data Insights:**  
  - Best/worst day  
  - Consistency score  

---

## b) Team Readiness

### 👥 Squad Overview
- High-level view for match day planning

### 🧮 Readiness Score (0–100)
- Based on recent EMBOSS data:
  - Latest score  
  - 7-day average  
  - Trend  
  - Variability  
  - Risk days  

### 📊 Squad Summary Metrics
- Players by status:
  - Optimal
  - Ready
  - Limited
  - Bench
  - Rest
  - Unknown  
- Total available  
- XI average readiness  

### 🧪 Recommended Starting XI
- Auto-suggested lineup based on readiness score  
- Takes **position requirements** into account (GK, DEF, MID, FWD)

### 🧑‍🤝‍🧑 Bench & Unavailable Tabs
- List of substitutes and unavailable players  
- Includes readiness details

### 🃏 Player Cards
- Compact format with:
  - Player Name  
  - Position / Status  
  - Readiness Score (%)  
  - Trend Icon: ▲ (Improving), ▼ (Declining), ▬ (Stable)  
  - **Hover for more details**

### 📊 Full Squad Readiness Chart
- Horizontal bar chart of all players  
- Color-coded by readiness status  
- Enables quick comparison across squad  

---

Let me know if you'd like this broken into multiple files, converted into code-friendly format (for Streamlit/HTML), or integrated into your UI.
## 5. Visual Showcase

*(**Note:** Please replace these placeholders with actual screenshots of your dashboard)*

*   **Individual Player View Screenshot:**
    `[Insert Screenshot of Individual Player Analysis View Here]`
*   **Team Readiness View Screenshot:**
    `[Insert Screenshot of Team Readiness View Here]`

## 6. Technology Stack

This dashboard was developed **entirely in Python** using the following libraries:

*   **Streamlit:** Core framework for building the interactive web application UI.
*   **Pandas:** Data manipulation, cleaning, and analysis.
*   **NumPy:** Numerical calculations.
*   **Plotly:** Generating interactive charts and visualizations.
*   **Matplotlib:** Used indirectly for color conversions (hex to rgba).

*Note: The original Vizathon brief suggested Flask/React. We opted for Streamlit to enable rapid prototyping and development within the competition timeframe, focusing on delivering functional data insights and visualizations efficiently.*

## 7. Code Structure

The project is organized into modular Python files:

*   `dashboard.py`: Main Streamlit application script; handles UI layout, sidebar, view rendering, and orchestrates calls to other modules.
*   `theme.py`: Defines the visual theme (colors, CSS styles).
*   `data_processing.py`: Handles data loading (CSV upload, default file, synthetic fallback), cleaning, and basic calculations (rolling average, weekly summary).
*   `data_generator.py`: Generates synthetic EMBOSS score data for demonstration purposes if real/default data is unavailable.
*   `analysis.py`: Contains logic for analyzing individual player 7-day data to determine status and generate recommendations.
*   `visualization.py`: Creates the Plotly charts for the Individual Player view (Recovery Trend, Weekly Summary).
*   `team_readiness.py`: Calculates player readiness scores, implements squad selection logic, and renders the Team Readiness view components (including the overview chart).


### Data

*   The application can use an uploaded CSV file.
*   If no file is uploaded, it looks for `./cleaned_data/cleaned_CFC_Recovery_Status_Data.csv`.
*   If the default file is not found, it generates synthetic data using `data_generator.py`.

## 8. Customization & Extension

*   **Appearance:** Modify `theme.py` (colors, CSS).
*   **Risk Threshold:** Adjust the slider in the sidebar.
*   **Analysis Logic:** Update rules in `analysis.py` and `team_readiness.py`.
*   **Data Sources:** Modify `data_processing.py` to handle different formats or sources.
*   **Visualizations:** Adapt charts in `visualization.py` and `team_readiness.py`.

## 9. Important Considerations

*   **Context is Crucial:** The interpretation of scores and recommendations requires expert judgment based on team context, player history, and other factors. This dashboard is a decision-support tool.
*   **Data Quality:** The accuracy of insights depends entirely on consistent and reliable input data.
*   **Model Simplicity:** The analysis and readiness models are rule-based. Real-world applications might benefit from incorporating more data sources (training load, subjective wellness, etc.) and potentially more complex modeling techniques.

---

