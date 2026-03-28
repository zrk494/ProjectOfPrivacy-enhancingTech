import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from config import LANGUAGES, PRICE_CHART_HEIGHT
from data import load_timeseries_data, calculate_timeseries_statistics

def display_timeseries_view(market_id, lang):
    """显示时间序列数据视图"""
    st.subheader(f"{LANGUAGES[lang]['timeseries_data']} (ID: {market_id})")
    
    # 加载YES和NO时间序列数据
    yes_df = load_timeseries_data(market_id, "YES")
    no_df = load_timeseries_data(market_id, "NO")
    
    if yes_df.empty:
        st.warning(f"{LANGUAGES[lang]['warning_no_data']} {market_id}")
        return
    
    # 显示数据统计信息
    stats = calculate_timeseries_statistics(yes_df)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(LANGUAGES[lang]['data_points'], stats['data_points'])
    with col2:
        if stats['time_range']:
            st.metric(LANGUAGES[lang]['time_range'], f"{stats['time_range'][0]} 至 {stats['time_range'][1]}")
        else:
            st.metric(LANGUAGES[lang]['time_range'], "N/A")
    with col3:
        st.metric(LANGUAGES[lang]['avg_midpoint'], f"{stats['avg_midpoint']:.6f}")
    
    # 创建交互式图表
    st.subheader(LANGUAGES[lang]['price_chart'])
    
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=(LANGUAGES[lang]['price_trend'], LANGUAGES[lang]['order_depth']),
        vertical_spacing=0.15
    )
    
    # 价格图表
    fig.add_trace(
        go.Scatter(
            x=yes_df['datetime'],
            y=yes_df['midpoint'],
            mode='lines',
            name=LANGUAGES[lang]['yes_midpoint'],
            line=dict(color='blue')
        ),
        row=1, col=1
    )
    
    if not no_df.empty:
        fig.add_trace(
            go.Scatter(
                x=no_df['datetime'],
                y=no_df['midpoint'],
                mode='lines',
                name=LANGUAGES[lang]['no_midpoint'],
                line=dict(color='red')
            ),
            row=1, col=1
        )
    
    # 深度图表
    fig.add_trace(
        go.Scatter(
            x=yes_df['datetime'],
            y=yes_df['bid_depth_top5'],
            mode='lines',
            name=LANGUAGES[lang]['bid_depth'],
            line=dict(color='green'),
            showlegend=False
        ),
        row=2, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=yes_df['datetime'],
            y=yes_df['ask_depth_top5'],
            mode='lines',
            name=LANGUAGES[lang]['ask_depth'],
            line=dict(color='orange'),
            showlegend=False
        ),
        row=2, col=1
    )
    
    fig.update_layout(
        height=PRICE_CHART_HEIGHT,
        showlegend=True,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, width='stretch')
    
    # 显示数据表格
    st.subheader(LANGUAGES[lang]['data_details'])
    st.dataframe(
        yes_df[['datetime', 'midpoint', 'best_bid', 'best_ask', 'spread', 'bid_depth_top5', 'ask_depth_top5']].tail(100),
        width='stretch',
        column_config={
            "datetime": LANGUAGES[lang]['time'],
            "midpoint": LANGUAGES[lang]['midpoint'],
            "best_bid": LANGUAGES[lang]['best_bid'],
            "best_ask": LANGUAGES[lang]['best_ask'],
            "spread": LANGUAGES[lang]['spread'],
            "bid_depth_top5": LANGUAGES[lang]['bid_depth_top5'],
            "ask_depth_top5": LANGUAGES[lang]['ask_depth_top5']
        }
    )