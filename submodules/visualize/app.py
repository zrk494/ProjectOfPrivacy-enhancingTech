import streamlit as st
import pandas as pd
import numpy as np
import os
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Language Dictionary
LANGUAGES = {
    'en': {
        'page_title': 'Polymarket Signal Analysis',
        'title': '📊 Polymarket Signal Analysis',
        'project': '**Project**: Empirical Detection of Unusual Odds Movements',
        'current_stage': '**Current Stage**: Data Visualization Phase',
        'config_options': '⚙️ Configuration Options',
        'select_market': 'Select Market',
        'data_view': 'Data View',
        'metadata_view': 'Market Metadata',
        'timeseries_view': 'Time Series Data',
        'trade_view': 'Trade Data',
        'anomaly_detection': '🔍 Anomaly Detection',
        'pattern_a': 'Pattern A: Front-running/Insider Trading Detection',
        'pattern_b': 'Pattern B: Arbitrage Opportunity Detection',
        'under_development': '🚧 Under Development...',
        'pattern_a_rules': '''**Detection Rules**:
        - Price deviation > Z-Score threshold
        - Volume spike''',
        'pattern_b_rules': '''**Detection Rules**:
        - |Price(Yes) + Price(No) - 1| > threshold
        - Duration > N minutes''',
        'market_info': '📈 Market Information',
        'market_id': 'Market ID',
        'volume_24hr': '24h Volume',
        'liquidity': 'Liquidity',
        'question': '**Question**',
        'end_date': '**End Date**',
        'error_metadata': 'Unable to load market metadata. Please check data file path.',
        'error_file_not_found': 'Market metadata file not found',
        'all_markets': '📋 All Market Metadata',
        'total_markets': 'Total Markets',
        'total_volume': 'Total Volume',
        'avg_liquidity': 'Avg Liquidity',
        'timeseries_data': '📊 Market Time Series Data',
        'data_points': 'Data Points',
        'time_range': 'Time Range',
        'avg_midpoint': 'Avg Midpoint',
        'price_chart': 'Price Chart',
        'price_trend': 'Price Trend',
        'order_depth': 'Order Depth',
        'yes_midpoint': 'YES Midpoint',
        'no_midpoint': 'NO Midpoint',
        'bid_depth': 'Bid Depth',
        'ask_depth': 'Ask Depth',
        'data_details': 'Data Details',
        'time': 'Time',
        'midpoint': 'Midpoint',
        'best_bid': 'Best Bid',
        'best_ask': 'Best Ask',
        'spread': 'Spread',
        'bid_depth_top5': 'Bid Depth Top5',
        'ask_depth_top5': 'Ask Depth Top5',
        'warning_no_data': 'No YES contract time series data found for market',
        'trade_data': '💹 Market Trade Data',
        'warning_no_trade_data': 'No YES contract trade data found for market',
        'total_trades': 'Total Trades',
        'total_amount': 'Total Amount',
        'avg_price': 'Avg Price',
        'volume_distribution': 'Volume Distribution',
        'buy_sell_volume': 'Buy/Sell Volume',
        'buy': 'Buy',
        'sell': 'Sell',
        'trade_records': 'Trade Records',
        'page': 'Page',
        'side': 'Side',
        'price': 'Price',
        'size': 'Size',
        'amount': 'Amount',
        'showing_records': 'Showing',
        'to': 'to',
        'of': 'of',
        'records': 'records',
        'total': 'total',
        'footer': 'CS6290 Group Project - Polymarket Signal Analysis',
        'language': 'Language'
    },
    'zh': {
        'page_title': 'Polymarket 信号分析',
        'title': '📊 Polymarket 信号分析',
        'project': '**项目**: 实证检测异常赔率变动',
        'current_stage': '**当前阶段**: 数据展示阶段',
        'config_options': '⚙️ 配置选项',
        'select_market': '选择市场',
        'data_view': '数据视图',
        'metadata_view': '市场元数据',
        'timeseries_view': '时间序列数据',
        'trade_view': '交易数据',
        'anomaly_detection': '🔍 异常检测',
        'pattern_a': '模式A: 前运行/内幕交易检测',
        'pattern_b': '模式B: 套利机会检测',
        'under_development': '🚧 功能开发中...',
        'pattern_a_rules': '''**检测规则**:
        - 价格偏离 > Z-Score阈值
        - 交易量突增''',
        'pattern_b_rules': '''**检测规则**:
        - |Price(Yes) + Price(No) - 1| > 阈值
        - 持续时间 > N分钟''',
        'market_info': '📈 市场信息',
        'market_id': '市场ID',
        'volume_24hr': '24小时交易量',
        'liquidity': '流动性',
        'question': '**问题描述**',
        'end_date': '**结束日期**',
        'error_metadata': '无法加载市场元数据，请检查数据文件路径。',
        'error_file_not_found': '市场元数据文件不存在',
        'all_markets': '📋 所有市场元数据',
        'total_markets': '市场总数',
        'total_volume': '总交易量',
        'avg_liquidity': '平均流动性',
        'timeseries_data': '📊 市场时间序列数据',
        'data_points': '数据点数量',
        'time_range': '时间范围',
        'avg_midpoint': '平均中间价',
        'price_chart': '价格走势图',
        'price_trend': '价格走势',
        'order_depth': '订单深度',
        'yes_midpoint': 'YES中间价',
        'no_midpoint': 'NO中间价',
        'bid_depth': '买单深度',
        'ask_depth': '卖单深度',
        'data_details': '数据详情',
        'time': '时间',
        'midpoint': '中间价',
        'best_bid': '最高买价',
        'best_ask': '最低卖价',
        'spread': '价差',
        'bid_depth_top5': '买单深度',
        'ask_depth_top5': '卖单深度',
        'warning_no_data': '未找到市场的YES合约时间序列数据',
        'trade_data': '💹 市场交易数据',
        'warning_no_trade_data': '未找到市场的YES合约交易数据',
        'total_trades': '总交易笔数',
        'total_amount': '总交易金额',
        'avg_price': '平均交易价格',
        'volume_distribution': '交易量分布',
        'buy_sell_volume': '买入/卖出交易量',
        'buy': '买入',
        'sell': '卖出',
        'trade_records': '交易记录',
        'page': '页码',
        'side': '方向',
        'price': '价格',
        'size': '数量',
        'amount': '金额',
        'showing_records': '显示',
        'to': '到',
        'of': '条记录，共',
        'records': '条',
        'total': '条',
        'footer': 'CS6290 小组项目 - Polymarket 信号分析',
        'language': '语言'
    }
}

# 1. Page Configuration
st.set_page_config(
    page_title="Polymarket Signal Analysis",
    layout="wide",
    page_icon="📊"
)

# 2. Data Loading Functions
@st.cache_data(ttl=3600)
def load_market_metadata(lang):
    data_path = r"polymarket_data(1)\polymarket_data\market_metadata.csv"
    if os.path.exists(data_path):
        df = pd.read_csv(data_path)
        return df
    else:
        st.error(f"{LANGUAGES[lang]['error_file_not_found']}: {data_path}")
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def load_timeseries_data(market_id, token_type="YES"):
    data_path = rf"polymarket_data(1)\polymarket_data\timeseries\{market_id}_{token_type}.csv"
    if os.path.exists(data_path):
        df = pd.read_csv(data_path)
        df['datetime'] = pd.to_datetime(df['datetime'])
        return df
    else:
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def load_trade_data(market_id, token_type="YES"):
    data_path = rf"polymarket_data(1)\polymarket_data\trades\{market_id}_{token_type}.csv"
    if os.path.exists(data_path):
        df = pd.read_csv(data_path)
        df['datetime'] = pd.to_datetime(df['datetime'])
        return df
    else:
        return pd.DataFrame()

# 3. Main Application
def main():
    # Language selector in sidebar
    lang = st.sidebar.radio(
        "🌐 Language / 语言",
        ['en', 'zh'],
        format_func=lambda x: 'English' if x == 'en' else '中文'
    )
    
    # Update page title based on language
    st.set_page_config(
        page_title=LANGUAGES[lang]['page_title'],
        layout="wide",
        page_icon="📊"
    )
    
    st.title(LANGUAGES[lang]['title'])
    st.markdown(f"""
    {LANGUAGES[lang]['project']}  
    {LANGUAGES[lang]['current_stage']}
    """)

    # Load market metadata
    metadata_df = load_market_metadata(lang)
    
    if metadata_df.empty:
        st.error(LANGUAGES[lang]['error_metadata'])
        return

    # 4. Sidebar Configuration
    st.sidebar.header(LANGUAGES[lang]['config_options'])
    
    # Market Selector
    market_options = metadata_df[['market_id', 'question']].copy()
    market_options['display_name'] = market_options['market_id'].astype(str) + " - " + market_options['question'].str[:50] + "..."
    selected_display = st.sidebar.selectbox(LANGUAGES[lang]['select_market'], market_options['display_name'].tolist())
    selected_market_id = market_options[market_options['display_name'] == selected_display]['market_id'].values[0]
    
    # View Selector
    view_options = [LANGUAGES[lang]['metadata_view'], LANGUAGES[lang]['timeseries_view'], LANGUAGES[lang]['trade_view']]
    view_mapping = {
        LANGUAGES[lang]['metadata_view']: 'metadata',
        LANGUAGES[lang]['timeseries_view']: 'timeseries',
        LANGUAGES[lang]['trade_view']: 'trade'
    }
    selected_view = st.sidebar.radio(LANGUAGES[lang]['data_view'], view_options)
    
    # Anomaly Detection Placeholder
    st.sidebar.divider()
    st.sidebar.header(LANGUAGES[lang]['anomaly_detection'])
    
    if st.sidebar.button(LANGUAGES[lang]['pattern_a']):
        st.sidebar.info(LANGUAGES[lang]['under_development'])
        st.sidebar.markdown(LANGUAGES[lang]['pattern_a_rules'])
    
    if st.sidebar.button(LANGUAGES[lang]['pattern_b']):
        st.sidebar.info(LANGUAGES[lang]['under_development'])
        st.sidebar.markdown(LANGUAGES[lang]['pattern_b_rules'])
    
    # 5. Display Market Information
    st.divider()
    st.subheader(f"{LANGUAGES[lang]['market_info']}: {selected_display}")
    
    # Get selected market metadata
    market_info = metadata_df[metadata_df['market_id'] == selected_market_id].iloc[0]
    
    # Display market details
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(LANGUAGES[lang]['market_id'], str(market_info['market_id']))
    with col2:
        st.metric(LANGUAGES[lang]['volume_24hr'], f"${market_info['volume_24hr']:,.2f}")
    with col3:
        st.metric(LANGUAGES[lang]['liquidity'], f"${market_info['liquidity']:,.2f}")
    
    st.markdown(f"{LANGUAGES[lang]['question']}: {market_info['question']}")
    st.markdown(f"{LANGUAGES[lang]['end_date']}: {market_info['end_date']}")
    
    # 6. Display Data Based on View Selection
    st.divider()
    
    view_type = view_mapping[selected_view]
    if view_type == 'metadata':
        display_metadata_view(metadata_df, lang)
    elif view_type == 'timeseries':
        display_timeseries_view(selected_market_id, lang)
    elif view_type == 'trade':
        display_trade_view(selected_market_id, lang)
    
    # 7. Footer
    st.divider()
    st.caption(LANGUAGES[lang]['footer'])

def display_metadata_view(metadata_df, lang):
    st.subheader(LANGUAGES[lang]['all_markets'])
    
    # Display summary statistics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(LANGUAGES[lang]['total_markets'], len(metadata_df))
    with col2:
        st.metric(LANGUAGES[lang]['total_volume'], f"${metadata_df['volume_24hr'].sum():,.2f}")
    with col3:
        st.metric(LANGUAGES[lang]['avg_liquidity'], f"${metadata_df['liquidity'].mean():,.2f}")
    
    # Display metadata table
    st.dataframe(
        metadata_df[['market_id', 'question', 'end_date', 'volume_24hr', 'liquidity']],
        use_container_width=True,
        column_config={
            "market_id": LANGUAGES[lang]['market_id'],
            "question": LANGUAGES[lang]['question'],
            "end_date": LANGUAGES[lang]['end_date'],
            "volume_24hr": LANGUAGES[lang]['volume_24hr'],
            "liquidity": LANGUAGES[lang]['liquidity']
        }
    )

def display_timeseries_view(market_id, lang):
    st.subheader(f"{LANGUAGES[lang]['timeseries_data']} (ID: {market_id})")
    
    # Load YES and NO timeseries data
    yes_df = load_timeseries_data(market_id, "YES")
    no_df = load_timeseries_data(market_id, "NO")
    
    if yes_df.empty:
        st.warning(f"{LANGUAGES[lang]['warning_no_data']} {market_id}")
        return
    
    # Display data statistics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(LANGUAGES[lang]['data_points'], len(yes_df))
    with col2:
        st.metric(LANGUAGES[lang]['time_range'], f"{yes_df['datetime'].min()} 至 {yes_df['datetime'].max()}")
    with col3:
        st.metric(LANGUAGES[lang]['avg_midpoint'], f"{yes_df['midpoint'].mean():.6f}")
    
    # Create interactive charts
    st.subheader(LANGUAGES[lang]['price_chart'])
    
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=(LANGUAGES[lang]['price_trend'], LANGUAGES[lang]['order_depth']),
        vertical_spacing=0.15
    )
    
    # Price chart
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
    
    # Depth chart
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
        height=600,
        showlegend=True,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Display data table
    st.subheader(LANGUAGES[lang]['data_details'])
    st.dataframe(
        yes_df[['datetime', 'midpoint', 'best_bid', 'best_ask', 'spread', 'bid_depth_top5', 'ask_depth_top5']].tail(100),
        use_container_width=True,
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

def display_trade_view(market_id, lang):
    st.subheader(f"{LANGUAGES[lang]['trade_data']} (ID: {market_id})")
    
    # Load YES and NO trade data
    yes_df = load_trade_data(market_id, "YES")
    no_df = load_trade_data(market_id, "NO")
    
    if yes_df.empty:
        st.warning(f"{LANGUAGES[lang]['warning_no_trade_data']} {market_id}")
        return
    
    # Combine data
    all_trades = pd.concat([yes_df, no_df], ignore_index=True)
    
    # Display statistics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(LANGUAGES[lang]['total_trades'], len(all_trades))
    with col2:
        st.metric(LANGUAGES[lang]['total_amount'], f"${all_trades['amount'].sum():,.2f}")
    with col3:
        st.metric(LANGUAGES[lang]['avg_price'], f"${all_trades['price'].mean():.6f}")
    
    # Trade volume chart
    st.subheader(LANGUAGES[lang]['volume_distribution'])
    
    buy_trades = all_trades[all_trades['side'] == 'BUY']
    sell_trades = all_trades[all_trades['side'] == 'SELL']
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=buy_trades['datetime'],
        y=buy_trades['amount'],
        name=LANGUAGES[lang]['buy'],
        marker_color='green'
    ))
    
    fig.add_trace(go.Bar(
        x=sell_trades['datetime'],
        y=sell_trades['amount'],
        name=LANGUAGES[lang]['sell'],
        marker_color='red'
    ))
    
    fig.update_layout(
        title=LANGUAGES[lang]['buy_sell_volume'],
        xaxis_title=LANGUAGES[lang]['time'],
        yaxis_title=LANGUAGES[lang]['amount'],
        barmode='stack',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Display trade table with pagination
    st.subheader(LANGUAGES[lang]['trade_records'])
    
    page_size = 50
    total_pages = (len(all_trades) + page_size - 1) // page_size
    page = st.number_input(LANGUAGES[lang]['page'], min_value=1, max_value=total_pages, value=1)
    
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    
    st.dataframe(
        all_trades[['datetime', 'side', 'price', 'size', 'amount']].iloc[start_idx:end_idx],
        use_container_width=True,
        column_config={
            "datetime": LANGUAGES[lang]['time'],
            "side": LANGUAGES[lang]['side'],
            "price": LANGUAGES[lang]['price'],
            "size": LANGUAGES[lang]['size'],
            "amount": LANGUAGES[lang]['amount']
        }
    )
    
    st.caption(f"{LANGUAGES[lang]['showing_records']} {start_idx + 1} {LANGUAGES[lang]['to']} {min(end_idx, len(all_trades))} {LANGUAGES[lang]['of']} {len(all_trades)} {LANGUAGES[lang]['records']}")

if __name__ == "__main__":
    main()