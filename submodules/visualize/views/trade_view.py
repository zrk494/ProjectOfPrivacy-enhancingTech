import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from config import LANGUAGES, VOLUME_CHART_HEIGHT, PAGE_SIZE
from data import load_trade_data, calculate_trade_statistics

def display_trade_view(market_id, lang):
    """显示交易数据视图"""
    st.subheader(f"{LANGUAGES[lang]['trade_data']} (ID: {market_id})")
    
    # 加载YES和NO交易数据
    yes_df = load_trade_data(market_id, "YES")
    no_df = load_trade_data(market_id, "NO")
    
    if yes_df.empty:
        st.warning(f"{LANGUAGES[lang]['warning_no_trade_data']} {market_id}")
        return
    
    # 合并数据
    all_trades = pd.concat([yes_df, no_df], ignore_index=True)
    
    # 显示统计信息
    stats = calculate_trade_statistics(all_trades)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(LANGUAGES[lang]['total_trades'], stats['total_trades'])
    with col2:
        st.metric(LANGUAGES[lang]['total_amount'], f"${stats['total_amount']:,.2f}")
    with col3:
        st.metric(LANGUAGES[lang]['avg_price'], f"${stats['avg_price']:.6f}")
    
    # 交易量图表
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
        height=VOLUME_CHART_HEIGHT
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 显示交易表格（带分页）
    st.subheader(LANGUAGES[lang]['trade_records'])
    
    page_size = PAGE_SIZE
    total_pages = (len(all_trades) + page_size - 1) // page_size
    
    # 使用会话状态管理页码
    if 'trade_page' not in st.session_state:
        st.session_state.trade_page = 1
    
    # 分页控件
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button(LANGUAGES[lang]['previous'] if 'previous' in LANGUAGES[lang] else "Previous", disabled=st.session_state.trade_page == 1):
            st.session_state.trade_page -= 1
    with col2:
        st.write(f"{LANGUAGES[lang]['page']}: {st.session_state.trade_page} / {total_pages}")
    with col3:
        if st.button(LANGUAGES[lang]['next'] if 'next' in LANGUAGES[lang] else "Next", disabled=st.session_state.trade_page == total_pages):
            st.session_state.trade_page += 1
    
    # 确保页码在有效范围内
    page = max(1, min(st.session_state.trade_page, total_pages))
    st.session_state.trade_page = page
    
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