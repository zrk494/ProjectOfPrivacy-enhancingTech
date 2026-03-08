# About The Project - CS6290 Group Project: Polymarket Signal Analysis

**Date**: 2026-02-13

**Status**: **Draft Version** 

## 1. Project Overview

### Core Topic

Polymarket Signal Analysis — Empirical Detection of Unusual Odds Movements.

### Core Form

A Web-based **Static Analytical Showcase**. The project team will run data pipelines offline in the background to generate "anomalous events" datasets for specific markets. The final deliverable is a webpage that requires no real-time backend support, used to interactively display detection results and statistical evidence.

## 2. Goals & Non-Goals

### 2.1 Goals

- **Core Goal**: Implement an offline algorithm process that takes historical data as input and outputs a list of "anomalous events".
- **Display Goal**: Build a front-end interface that clearly correlates "odds anomalies" with "statistical evidence" (such as Z-Score mutations, volume spikes).
- **Engineering Goals**:
  - Implement data cleaning and resampling mechanisms.
  - Implement two specific anomaly detection algorithms, **showcasing their causal relationship**:
    - **The Cause (Micro-level): Sniper Attack Detection**. Tracing the root cause by identifying specific malicious wallet behaviors.
    - **The Symptom (Macro-level): Market-Level Statistical Anomaly Detection**. Detecting the resulting observable market disruptions triggered by the sniper's actions.

### 2.2 Non-Goals

- **No Real-time**: During demonstration, do not connect to Polymarket real-time API, no real-time monitoring.
- **No Trading**: Do not provide buy/sell recommendations, do not connect wallets.
- **No Tick-by-tick Analysis**: Do not process Tick-level transaction data, do not track specific accounts (Whale Tracking), focus only on aggregated prices and volumes.
- **No Complex Attribution**: Do not attempt to explain "why" anomalies occurred (such as scraping external news), only show "what happened".

## 3. Core Display Strategy

Given the static nature of the showcase and browser performance constraints, we will adopt a **"Detective Report" Card-based UI (Drill-down interaction)** in Streamlit to intuitively demonstrate the causal link between the two anomaly dimensions:

- **Level 1: Macro Evidence**: The card initially displays the macro-level symptoms (e.g., a minute-level trading volume surge or extreme Price Z-Score).
- **Level 2: Micro Tracing**: Users can expand the card to reveal the microscopic root cause, showing the specific suspect wallet address, its Isolation Forest anomaly score, and the exact sequence of the sniper attack (e.g., rapid buy/sell pairs with large amounts).

## 4. Core Project Pipeline (Project Pipeline & User Flows)

The data flow of this project is strictly divided into three phases:

### Phase One: Data Acquisition & Preprocessing

*Objective: Build standardized, time-aligned historical datasets.*

1. **Ingest**: Script calls Polymarket API (CLOB/History) to pull raw OHLCV data for specified markets (such as "US Election 2024") over the past 6 months.
   - Acquire data for mutually exclusive contract pairs (e.g., simultaneously obtain price sequences for both "Yes" and "No" contracts).
2. **Clean & Align**:
   - **Fill Missing Values**: Process API return gaps.
   - **Time Alignment**: This is crucial. Ensure that "Yes" and "No" price data are aligned at the same timestamps (resample to unified minute/hour levels) to enable subsequent parity formula calculations.

### Phase Two: Algorithmic Detection

*Objective: Run offline algorithms, output anomalous event lists. We will focus on detecting two patterns:*

1. **Pattern A: Market-Level Statistical Anomaly Detection**
   - **Definition**: Detect unusual market behavior through statistical analysis of aggregated price and volume data.
   - **Detection Logic**:
     - Calculate moving averages (MA) and standard deviations (StdDev) of prices.
     - Identify time windows with **Volume Spikes** (volume surges) accompanied by **High Z-Score** (price deviation from mean > 3σ).
   - **Output**: Marked as "Type A: Market Anomaly".
2. **Pattern B: Sniper Attack Detection**
   - **Definition**: Detect manipulative behavior where attackers use large funds to pump prices, then sell quickly after retail traders follow.
   - **Detection Logic**:
     - Use session-based analysis (transactions from same address within 30 minutes).
     - Apply Isolation Forest with AI features (Sentence-BERT for transaction sequences).
     - Identify top 5% most anomalous sessions with specific sniper characteristics.
   - **Output**: Marked as "Type B: Sniper Attack".

### Phase Three: Result Showcase

*Objective: Users view analysis results generated in Phase Two through the Web interface.*

1. **Global Overview**:
   - Users open the webpage and see the full timeline of odds trends.
   - The timeline marks **Type A (Market Anomaly)** and **Type B (Sniper Attack)** anomalies with different colors.
2. **Interactive Drill-down**:
   - User clicks a **Type A** marker -> Pop-up shows the volume histogram and volatility curve at that moment (proving statistical anomaly).
   - User clicks a **Type B** marker -> Pop-up shows the transaction sequence and session analysis (proving sniper attack pattern).

## 5. Key Decisions & Risk Management

### 5.1 Identified Risks & Mitigation Strategies

| Risk Point                          | Description                                                  | Mitigation Strategy                                          |
| ----------------------------------- | ------------------------------------------------------------ | -------------------------------------------------------------- |
| **Data Unavailability**            | Sniper attack detection requires wallet address information which may not be available in current data sources. | **Data Source Expansion**. Acquire raw trade data with wallet addresses from Polymarket API or blockchain explorers to enable session-based analysis. |
| **Browser Performance Bottleneck**  | Loading 6 months of high-frequency data directly would crash the browser. | **On-demand Loading**. Frontend defaults to loading only "hourly" overview data; only load "minute-level" details for that segment when users click specific events. |
| **Algorithm "Hindsight Bias"**       | Pre-calculated results may appear to be manually selected.    | **Explicitly display algorithm thresholds** on the interface (e.g., "Detection threshold: Spread > 0.05"), showing that this is rule-based objective filtering. |

### 5.2 Tentative Tech Stack

- **Data Processing**: Python (Pandas, NumPy, Scikit-learn)
- **Data Source**: Polymarket Clob API / Historical Data Snapshots
- **Frontend Display**: Streamlit
- **Data Format**: Static JSON files

## 6. Next Steps

1. **Spec Writing**: Based on this findings document, begin writing the detailed `SRS (Software Requirements Specification)`.
2. **Algorithm Validation**:
   - Write Python script to calculate `Price(Yes) + Price(No)` for a market.
   - Acquire wallet address data to enable session-based sniper attack detection.
   - Validate both statistical anomaly detection and sniper attack detection on historical data **to confirm their causal correlation**.