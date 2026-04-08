- # CS6290 — Individual Evidence Pack (Milestone 2)

  ## Student Information

  - **Name:** ZHANG Ruikun
  - **Student ID (SID):** 59982716
  - **Group Number / Project Title:** Group 2 / Polymarket Signal Analysis — Empirical Detection of Unusual Odds Movements
  - **Milestone:** Milestone 2
  - **Date:** 08/03/2026

  ## 1) What I Contributed

  ### Branch 1: Core Visualization Infrastructure
  - **Data Visualization Dashboard**: Developed a Streamlit-based dashboard with three data views (Market Metadata, Time Series Data, Trade Data) for Polymarket data display.
  - **Multilingual Support**: Implemented English/Chinese language switching with complete language dictionary.
  - **Data Loading & Caching**: Created efficient loading functions with Streamlit caching (@st.cache_data) to optimize performance for large CSV files (~70MB).
  - **Interactive Visualization**: Integrated Plotly for interactive charts (price trends, order depth, trade volume).
  - **Anomaly Detection Interface**: Designed placeholder interfaces for two anomaly detection patterns.

  ### Branch 2: Project Refinement & Display Strategy
  - **Anomaly Framework**: Updated project description to define two anomaly forms with causal relationship:
    - **Micro-level (Cause)**: Sniper Attack Detection (malicious wallet behaviors)
    - **Macro-level (Symptom)**: Market-Level Statistical Anomaly Detection (market disruptions)
  - **Enhanced Display**: Implemented "Detective Report" Card-based UI with drill-down interaction:
    - Level 1: Macro-level symptoms (volume surges, price Z-Score anomalies)
    - Level 2: Micro-level root cause analysis (wallet addresses, anomaly scores, attack sequences)
  - **Raw Data Display**: Enhanced raw data presentation with improved filtering and pagination.
  - **Anomaly Showcase**: Designed structured anomaly display with statistical evidence and causal relationship visualization.

  ## 2) Evidence 

  | #    | Evidence type | Link / Reference                                         | What this shows                                              |
  | ---- | ------------- | -------------------------------------------------------- | ------------------------------------------------------------ |
  | 1    | Repository    | https://github.com/zrk494/ProjectOfPrivacy-enhancingTech | The central repository containing the initialized project structure and documentation. |
  | 2    | Screenshot    | The image below                                          | Implemented data display for collected Polymarket data using Streamlit. |

  - **Visualization Tool Research & Proof of Concept**

  ![屏幕截图 2026-03-08 183247](./MileStone2.assets/屏幕截图 2026-03-08 183247.png)

  ## 3) Validation Performed 

  - **Data Loading Validation**: Successfully tested data loading functions for all three data types (market metadata, time series, and trades) from the polymarket_data(1) directory, confirming proper CSV parsing and datetime conversion.
  - **Interface Functionality Testing**: Verified all dashboard components including market selection, view switching, data filtering, and pagination work correctly across different market datasets.
  - **Language Switching Verification**: Tested bilingual functionality by switching between English and Chinese interfaces, confirming that all text elements update correctly and maintain proper formatting.
  - **Performance Optimization Validation**: Confirmed that Streamlit's caching mechanism effectively reduces data loading time and prevents redundant processing when switching between views or markets.
  - **Visualization Component Testing**: Validated that Plotly charts render correctly with proper data ranges, legends, and interactive features including hover tooltips and zoom capabilities.

  ## 4) AI Usage Transparency

  - **AI tool(s) used:** Used **DeepSeek** for initial brainstorming and researching related technical topics. Used **Gemini** to assist in drafting boilerplate code for visualization and refining documentation structure.
  - **One AI output I rejected (and why it was wrong, risky, or insufficient):**
    - **Rejection**: Rejected the dual-window linked dashboard approach suggested by AI for displaying anomalies, as it was too complex and lacked user engagement.
    - **Correction**: Redesigned the display into an interactive card-based format to enhance user interaction and provide a clearer causal relationship visualization.

  ## 5) Risk

  - **Data availability for sniper attack detection.**
    - *Detail*: Sniper detection requires wallet address data not currently available; may need additional data sources.