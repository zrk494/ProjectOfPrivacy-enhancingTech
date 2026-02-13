import streamlit as st
import pandas as pd
import numpy as np

# 1. Page Configuration
st.set_page_config(page_title="Polymarket Signal Analysis", layout="wide")

st.title("📊 Polymarket Signal Analysis Dashboard")
st.markdown("""
**Project:** Empirical Detection of Unusual Odds Movements  
**Scope:** Phase 3 - Visualizing Detection Results (Pre-computed Data)
""")

# 2. Mock Data Generation (Replace with your Phase 1/2 JSON/CSV output)
@st.cache_data
def load_data():
    dates = pd.date_range(start='2024-06-01', periods=200, freq='12H')
    # Generate mock price for 'Yes' contract
    price_yes = np.random.uniform(0.45, 0.55, 200)
    # Simulate a "Type A: Front-running" anomaly (Price Spike)
    price_yes[150:155] += 0.35 
    # Simulate a "Type B: Parity Break" (Price_Yes + Price_No != 1)
    price_no = 1 - price_yes
    price_no[50:55] -= 0.15 
    
    df = pd.DataFrame({
        'Timestamp': dates,
        'Price_Yes': price_yes,
        'Price_No': price_no,
        'Volume': np.random.randint(1000, 50000, 200)
    })
    return df

data = load_data()

# 3. Sidebar Configuration
st.sidebar.header("Algorithm Parameters")
z_threshold = st.sidebar.slider("Anomaly Sensitivity (Z-Score)", 1.0, 5.0, 3.0)
st.sidebar.divider()
st.sidebar.info("This dashboard displays pre-computed data analyzed in Phase 2.")

# 4. Top Metrics (Summary)
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Market Status", "US Election 2024", delta="Active")
with col2:
    st.metric("Total Anomalies Detected", "12")
with col3:
    st.metric("Data Period", "6 Months")

st.divider()

# 5. Main Visualization
st.subheader("Market Price Overview (Interactive)")
# Display price of Yes contract
st.line_chart(data, x='Timestamp', y=['Price_Yes', 'Price_No'])

# 6. Specific Anomaly Detection (Phase 3 Logic)
st.subheader("Detailed Evidence: Detection Results")

tab1, tab2 = st.tabs(["Type A: Front-running", "Type B: Parity Breakage"])

with tab1:
    st.warning("Detection Rule: Price deviation > Z-Score Threshold + Volume Spike")
    # Simulation logic for detection
    anomalies_a = data[data['Price_Yes'] > 0.8] # Mock filter
    if not anomalies_a.empty:
        st.write("Identified Abnormal Movements:")
        st.dataframe(anomalies_a[['Timestamp', 'Price_Yes', 'Volume']])
    else:
        st.write("No Type A anomalies found with current parameters.")

with tab2:
    st.warning("Detection Rule: |Price(Yes) + Price(No) - 1| > Threshold")
    # Calculate sum to show parity break
    data['Parity_Sum'] = data['Price_Yes'] + data['Price_No']
    anomalies_b = data[abs(data['Parity_Sum'] - 1) > 0.1]
    
    if not anomalies_b.empty:
        st.write("Arbitrage Opportunities (Inefficiency detected):")
        st.line_chart(data, x='Timestamp', y='Parity_Sum')
        st.dataframe(anomalies_b[['Timestamp', 'Price_Yes', 'Price_No', 'Parity_Sum']])
    else:
        st.success("Market Parity is stable (Sum ≈ 1.0).")

# 7. Footer
st.divider()
st.caption("CS6290 Group Project - Empirical Data Analytics")