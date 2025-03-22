# [CFC Performance Insights Vizathon](https://chelsea-fc-performance-insights.github.io/Competition/index.html)

**17th March - 7th April 2025**  
**#CFCInsights**

## What the competition is all about?
Create the most compelling **Physical Performance interface** for elite football players and their coaches. This **vizathon** is a platform to showcase **innovative design skills, technical mastery, and user-focused thinking**. Your work can have a **real-world impact** on professional football performance analysis.

![Modules Overview](https://github.com/probablyvivek/cfc/blob/main/images/Modules.png?raw=true)

## Our Focus: **Recovery**
For this competition, our entry is focused on the **Recovery** module — tracking how well players recover from physical exertion and using that data to drive smarter coaching decisions and behavioral nudges.

------

### Recovery Module

![Recovery](https://github.com/probablyvivek/cfc/blob/main/images/Recovery.png?raw=True)

**Objective:** Track **how well players recover** after high-intensity sessions & optimize readiness for future matches.

#### Key Metrics Tracked:
- **Sleep Quality**
- **Muscle Soreness**
- **Biomarker Analysis**
- **Joint Mobility & Muscle Load Tolerance**
- **Subjective Recovery Perception**
- **Overall Recovery Score (EMBOSS)**

#### Recovery Dataset Fields:
![Recovery Data](https://github.com/probablyvivek/cfc/blob/main/images/RecoveryData.png?raw=True)

Each recovery category includes two metrics:
- `_completeness`: Percentage of completed tests (0–100%)
- `_composite`: Score relative to player’s norm (e.g. -0.5 = 50% below usual level)

**Categories Include:**
- `bio`: Blood biomarkers indicating inflammation and fatigue
- `msk_joint_range`: Joint range in ankles, knees, hips
- `msk_load_tolerance`: Muscle force tolerance (hip & thigh)
- `subjective`: Player-reported recovery status
- `soreness`: Muscle soreness reported by player
- `sleep`: Quality of previous night's sleep

**Aggregated Metric:**
- `emboss_baseline_score`: Overall recovery score across all categories

------

### Our Focus Areas for the Vizathon:
We’re building a focused, player-first experience centered around the Recovery module.

Our project will highlight:
- 📈 **Recovery Trends** — via EMBOSS score and microcycle insights
- 🧬 **Category Snapshots** — composite & completeness by type (e.g. soreness, sleep)
- 🔔 **Contextual Nudges** — subtle but powerful coach/player alerts
- 🧩 **Functional Simplicity** — clean visual language and minimal clicks

The interface will be developed **entirely in Python** using:
- **Flask + React** for a fast, modular web app
- **pandas** for data wrangling
- **Plotly or Chart.js** (via React) for compelling visualizations

