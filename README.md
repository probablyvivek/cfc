# [CFC Performance Insights Vizathon](https://chelsea-fc-performance-insights.github.io/Competition/index.html)

**17th March - 7th April 2025**
**#CFCInsights**

## What the competition is all about?
Create the most compelling **Physical Performance interface** for elite football players and their coaches. This **vizathon** is a platform to showcase **innovative design skills, technical mastery, and user-focused thinking**. Your work can have a **real-world impact** on professional football performance analysis.

![Modules Overview](https://github.com/probablyvivek/cfc/blob/main/images/Modules.png?raw=true)

## Main Focus: **Load Demand + Recovery**
For this competition, we will analyze and visualize **two critical aspects** of player performance:

-------
### 1. Load Demand

![GPS](https://github.com/probablyvivek/cfc/blob/main/images/GPS.png?raw=True)

**Objective:** Analyze the physical strain experienced by players during matches and training sessions.

**Key Metrics:**
- **Distance Covered:** Total distance in meters or kilometers
- **Speed Zones:**
  - Distance over 21 km/h
  - Distance over 24 km/h
  - Distance over 27 km/h
- **Acceleration/Deceleration Events:**
  - Events above 2.5 m/s²
  - Events above 3.5 m/s²
  - Events above 4.5 m/s²
- **Workload Intensity:** Duration and peak speed
- **Heart Rate Zones:**
  - Zone 1 (50–60% Max HR)
  - Zone 2 (60–70% Max HR)
  - Zone 3 (70–80% Max HR)
  - Zone 4 (80–90% Max HR)
  - Zone 5 (90–100% Max HR)

**Dataset Fields:**
- `date`: Session or match date
- `opposition_code`: Identifier for opposing team
- `opposition_full`: Full opposing team name
- `md_plus_code`: Days after match (e.g., MD+1)
- `md_minus_code`: Days before match (e.g., MD-1)
- `season`: Season of data collection
- `distance`: Total distance covered
- `distance_over_21`: Distance at speeds above 21 km/h
- `distance_over_24`: Distance at speeds above 24 km/h
- `distance_over_27`: Distance at speeds above 27 km/h
- `accel_decel_over_2_5`: Events >2.5 m/s²
- `accel_decel_over_3_5`: Events >3.5 m/s²
- `accel_decel_over_4_5`: Events >4.5 m/s²
- `day_duration`: Session duration (minutes)
- `peak_speed`: Highest recorded speed
- `hr_zone_1_hms`: Time spent in heart rate zone 1 (50-60% Max HR)
- `hr_zone_2_hms`: Time spent in heart rate zone 2 (60-70% Max HR)
- `hr_zone_3_hms`: Time spent in heart rate zone 3 (70-80% Max HR)
- `hr_zone_4_hms`: Time spent in heart rate zone 4 (80-90% Max HR)
- `hr_zone_5_hms`: Time spent in heart rate zone 5 (90-100% Max HR)

---------

### 2. Recovery

![Recovery](https://github.com/probablyvivek/cfc/blob/main/images/Recovery.png?raw=True)

**Objective:** Track **how well players recover** after high-intensity sessions & optimize readiness.

**Key Metrics:**
- **Sleep Quality**
- **Muscle Soreness**
- **Biomarker Analysis**
- **Recovery Scores**

**Dataset Fields:**
- `bio`: Blood biomarkers indicating inflammation and fatigue
- `msk_joint_range`: Joint flexibility (ankles, knees, hips)
- `msk_load_tolerance`: Muscular capacity for thigh and hip force production
- `subjective`: Player-reported recovery perception
- `soreness`: Self-assessed muscle soreness
- `sleep`: Quality assessment of previous night's sleep
  Each category includes two metrics:
  - **Completeness:** Test completion percentage (0–100%)
  - **Composite:** Category score relative to player's normative values (expressed as %)

**Overall Recovery Score:** Aggregated `emboss_baseline_score` combining all composite scores.

------
**Correlation Analysis:** We’ll also explore **how load demand impacts recovery trends** to provide **actionable insights** for coaches & players.
