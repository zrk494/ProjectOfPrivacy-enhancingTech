# About The Project - CS6290 Group Project: Polymarket Signal Analysis

**Date**: 2026-03-23

**Status**: **Updated Version** 

## 1. Project Overview

### Core Topic

Polymarket Signal Analysis — Empirical Detection of Unusual Market Stress Events and Sniper Attacks.

### Core Form

A Web-based **Static Analytical Showcase**. The project team runs data pipelines offline in the background to generate "anomalous events" datasets for specific markets. The final deliverable is a webpage that requires no real-time backend support, used to interactively display detection results and statistical evidence.

## 2. Goals & Non-Goals

### 2.1 Goals

- **Core Goal**: Implement an offline algorithm process that takes historical data as input and outputs a list of "anomalous events".
- **Display Goal**: Build a front-end interface that clearly correlates "market anomalies" with "statistical evidence" (such as stress scores, volume spikes, and sniper attack patterns).
- **Engineering Goals**:
  - Implement data cleaning and resampling mechanisms.
  - Implement two specific anomaly detection algorithms, **showcasing their causal relationship**:
    - **The Cause (Micro-level): Sniper Attack Detection**. Tracing the root cause by identifying specific suspicious wallet behaviors with session-based analysis.
    - **The Symptom (Macro-level): Market-Level Stress Anomaly Detection**. Detecting the resulting observable market disruptions triggered by unusual activities.

### 2.2 Non-Goals

- **No Real-time**: During demonstration, do not connect to Polymarket real-time API, no real-time monitoring.
- **No Trading**: Do not provide buy/sell recommendations, do not connect wallets.
- **No Complex Attribution**: Do not attempt to explain "why" anomalies occurred (such as scraping external news), only show "what happened".

## 3. Core Display Strategy

Given the static nature of the showcase and browser performance constraints, we will adopt a **"Detective Report" Card-based UI (Drill-down interaction)** in Streamlit to intuitively demonstrate the causal link between the two anomaly dimensions:

- **Level 1: Macro Evidence**: The card initially displays the macro-level symptoms (e.g., minute-level stress score spikes or extreme liquidity changes).
- **Level 2: Micro Tracing**: Users can expand the card to reveal the microscopic root cause, showing the specific suspect wallet address, its anomaly score, and the exact sequence of the sniper attack (e.g., rapid buy/sell pairs with large amounts).

## 4. Core Project Pipeline (Project Pipeline & User Flows)

The data flow of this project is strictly divided into three phases:

### Phase One: Data Acquisition & Preprocessing

*Objective: Build standardized, time-aligned historical datasets.*

1. **Ingest**: Script calls Polymarket API (CLOB/History) to pull raw trade data and timeseries/snapshot data for specified markets (such as "US Election 2024").
   - Acquire trade data with timestamp, size/amount, price, and wallet address information.
   - Acquire timeseries/snapshot data with midpoint, spread, depth, and imbalance information.
2. **Clean & Align**:
   - **Fill Missing Values**: Process API return gaps.
   - **Time Alignment**: Ensure that trade data and timeseries data are aligned at the same timestamps (resample to unified minute levels) to enable subsequent analysis.

### Phase Two: Algorithmic Detection

*Objective: Run offline algorithms, output anomalous event lists. We will focus on detecting two patterns:*

1. **Pattern A: Market-Level Stress Anomaly Detection**
   - **Definition**: Detect unusual market behavior through statistical analysis of aggregated trade and market state data.
   - **Detection Logic**:
     - Aggregate trade data into fixed time buckets (e.g., 60 seconds).
     - Aggregate timeseries/snapshot data into the same time buckets.
     - Fuse trade features and snapshot features.
     - Calculate rolling z-scores for multiple dimensions (trade activity, liquidity, price behavior).
     - Compute composite stress score and identify anomalous time buckets.
     - Merge contiguous anomalous buckets into stress events.
     - Enrich events with additional market state information and attribute dominant drivers.
   - **Output**: Marked as "Type A: Market Stress Anomaly".
2. **Pattern B: Sniper Attack Detection**
   - **Definition**: Detect manipulative behavior where attackers use large funds to execute rapid buy-sell sequences with ultra-short holding periods.
   - **Detection Logic**:
     - Use session-based analysis (transactions from same address within a short time window).
     - Apply anomaly detection with embedded transaction sequences.
     - Identify top anomalous sessions with specific sniper characteristics (large trade + buy then sell + ultra-short holding + 2 trades).
   - **Output**: Marked as "Type B: Sniper Attack".

### Phase Three: Result Showcase

*Objective: Users view analysis results generated in Phase Two through the Web interface.*

1. **Global Overview**:
   - Users open the webpage and see the full timeline of market stress events.
   - The timeline marks **Type A (Market Stress Anomaly)** and **Type B (Sniper Attack)** anomalies with different colors.
2. **Interactive Drill-down**:
   - User clicks a **Type A** marker -> Pop-up shows the stress score components, liquidity changes, and price behavior during the event (proving market stress).
   - User clicks a **Type B** marker -> Pop-up shows the transaction sequence, wallet address, and attack window visualization (proving sniper attack pattern).

## 5. Key Decisions & Risk Management

### 5.1 Identified Risks & Mitigation Strategies

| Risk Point                          | Description                                                  | Mitigation Strategy                                          |
| ----------------------------------- | ------------------------------------------------------------ | -------------------------------------------------------------- |
| **Data Unavailability**            | Sniper attack detection requires wallet address information which may not be available in current data sources. | **Data Source Expansion**. Acquire raw trade data with wallet addresses from Polymarket API or blockchain explorers to enable session-based analysis. |
| **Browser Performance Bottleneck**  | Loading large amounts of high-frequency data directly would crash the browser. | **On-demand Loading**. Frontend defaults to loading only aggregated overview data; only load detailed data for specific events when users click on them. |
| **Algorithm "Hindsight Bias"**       | Pre-calculated results may appear to be manually selected.    | **Explicitly display algorithm thresholds** on the interface (e.g., "Detection threshold: Top 5% stress scores"), showing that this is rule-based objective filtering. |

### 5.2 Tech Stack

- **Data Processing**: Python (Pandas, NumPy, Scikit-learn)
- **Data Source**: Polymarket Clob API / Historical Data Snapshots
- **Frontend Display**: Streamlit
- **Data Format**: Static JSON files

## 6. Project Structure

The project is organized into three main submodules:

1. **algorithm**: Contains core algorithm implementations for anomaly detection:
   - **CS6290-polymarket-anomaly-detection**: Market stress detection pipeline for identifying anomalous market pressure events.
   - **sniper_detection**: Sniper attack detection module for identifying suspicious wallet behaviors.

2. **data**: Contains data collection and storage components:
   - **pet-getdata**: Scripts for acquiring and processing Polymarket data.
   - **polymarket_data**: Storage for historical trade and timeseries data.

3. **visualize**: Contains frontend components for displaying detection results:
   - **frontend_sniper_detection**: Visualization components for sniper attack cases.
   - **app.py**: Main Streamlit application for result showcase.

## 7. Next Steps

1. **Algorithm Validation**:
   - Validate both market stress anomaly detection and sniper attack detection on historical data to confirm their effectiveness.
   - Fine-tune detection parameters to balance precision and recall.

2. **Frontend Development**:
   - Implement the Streamlit-based interactive showcase.
   - Design intuitive visualizations for both types of anomalies.

3. **Documentation**:
   - Complete detailed documentation for each module.
   - Create user guides for running the pipelines and interpreting results.

4. **Project Delivery**:
   - Finalize the static analytical showcase.
   - Prepare demonstration materials and presentation.
