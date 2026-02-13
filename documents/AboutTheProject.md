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
  - Implement two specific anomaly detection algorithms: **Front-running/Insider Trading Patterns** and **Parity Formula Breakdown/Arbitrage Patterns**.

### 2.2 Non-Goals

- **No Real-time**: During demonstration, do not connect to Polymarket real-time API, no real-time monitoring.
- **No Trading**: Do not provide buy/sell recommendations, do not connect wallets.
- **No Tick-by-tick Analysis**: Do not process Tick-level transaction data, do not track specific accounts (Whale Tracking), focus only on aggregated prices and volumes.
- **No Complex Attribution**: Do not attempt to explain "why" anomalies occurred (such as scraping external news), only show "what happened".

## 3. Core Project Pipeline (Project Pipeline & User Flows)

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

1. **Pattern A: Pre-news "Front-running" Volatility (Front-running / Insider Pattern)**
   - **Definition**: Sudden dramatic fluctuations that occur during market calm periods, often indicating insider information leaks.
   - **Detection Logic**:
     - Calculate moving averages (MA) and standard deviations (StdDev) of prices.
     - Identify time windows with **Volume Spikes** (volume surges) accompanied by **High Z-Score** (price deviation from mean > 3σ).
   - **Output**: Marked as "Type A: Volatility Anomaly".
2. **Pattern B: Parity Formula Breakdown & Arbitrage (Parity Breakage / Arbitrage)**
   - **Definition**: In binary prediction markets, theoretically `Price(Yes) + Price(No)` should equal 1. When the sum significantly deviates from 1, it indicates market failure or risk-free arbitrage opportunities.
   - **Detection Logic**:
     - Calculate `Spread = |Price(Yes) + Price(No) - 1|`.
     - When `Spread > Threshold` (e.g., 0.02) and persists for more than N minutes, it is considered anomalous.
   - **Output**: Marked as "Type B: Arbitrage Opportunity".

### Phase Three: Result Showcase

*Objective: Users view analysis results generated in Phase Two through the Web interface.*

1. **Global Overview**:
   - Users open the webpage and see the full timeline of odds trends.
   - The timeline marks **Type A (Volatility)** and **Type B (Arbitrage)** anomalies with different colors.
2. **Interactive Drill-down**:
   - User clicks a **Type A** marker -> Pop-up shows the volume histogram and volatility curve at that moment (proving front-running).
   - User clicks a **Type B** marker -> Pop-up shows the superimposed curves of `Price(Yes) + Price(No)` (proving the two lines separate, sum not equal to 1).

## 4. Key Decisions & Risk Management

### 4.1 Identified Risks & Mitigation Strategies

| Risk Point                          | Description                                                  | Mitigation Strategy                                          |
| ----------------------------------- | ------------------------------------------------------------ | -------------------------------------------------------------- |
| **Data Alignment Error**            | If Yes and No trades don't occur at exactly the same millisecond, simple addition could lead to false "arbitrage signals". | **Resampling Buffer**. During preprocessing, downsample data (e.g., 1-minute or 5-minute windows), taking weighted average prices within that window to eliminate noise from micro-time differences. |
| **Browser Performance Bottleneck**  | Loading 6 months of high-frequency data directly would crash the browser. | **On-demand Loading**. Frontend defaults to loading only "hourly" overview data; only load "minute-level" details for that segment when users click specific events. |
| **Algorithm "Hindsight Bias"**       | Pre-calculated results may appear to be manually selected.    | **Explicitly display algorithm thresholds** on the interface (e.g., "Detection threshold: Spread > 0.05"), showing that this is rule-based objective filtering. |

### 4.2 Tentative Tech Stack

- **Data Processing**: Python (Pandas, NumPy)
- **Data Source**: Polymarket Clob API / Historical Data Snapshots
- **Frontend Display**: Streamlit
- **Data Format**: Static JSON files

## 5. Next Steps

1. **Spec Writing**: Based on this findings document, begin writing the detailed `SRS (Software Requirements Specification)`.
2. **Algorithm Validation**:
   - Write Python script to calculate `Price(Yes) + Price(No)` for a market.
   - Observe whether there are significant instances of `Sum != 1` in historical data to determine if "arbitrage detection" has practical demonstration value.