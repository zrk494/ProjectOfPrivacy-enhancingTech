import streamlit as st
from config import LANGUAGES

def create_sidebar(lang, metadata_df):
    """创建侧边栏"""
    # 语言选择器
    lang = st.sidebar.radio(
        "🌐 Language / 语言",
        ['en', 'zh'],
        format_func=lambda x: 'English' if x == 'en' else '中文'
    )
    
    # 异常视图切换按钮（放在最前面，以便控制其他元素的显示）
    st.sidebar.header(LANGUAGES[lang]['anomaly_detection'])
    use_anomaly_view = st.sidebar.checkbox("进入异常可视化专用视图" if lang == 'zh' else "Enter Anomaly Visualization View", value=False)
    
    # 只有在非异常视图下才显示市场选择和数据视图
    if not use_anomaly_view:
        # 配置选项
        st.sidebar.header(LANGUAGES[lang]['config_options'])
        
        # 市场选择器
        if not metadata_df.empty:
            market_options = metadata_df[['market_id', 'question']].copy()
            market_options['display_name'] = market_options['market_id'].astype(str) + " - " + market_options['question'].str[:50] + "..."
            selected_display = st.sidebar.selectbox(LANGUAGES[lang]['select_market'], market_options['display_name'].tolist())
            selected_market_id = market_options[market_options['display_name'] == selected_display]['market_id'].values[0]
        else:
            selected_market_id = None
            st.sidebar.warning("No market data available")
        
        # 视图选择器（仅包含基础视图）
        view_options = [
            LANGUAGES[lang]['metadata_view'],
            LANGUAGES[lang]['timeseries_view'],
            LANGUAGES[lang]['trade_view']
        ]
        view_mapping = {
            LANGUAGES[lang]['metadata_view']: 'metadata',
            LANGUAGES[lang]['timeseries_view']: 'timeseries',
            LANGUAGES[lang]['trade_view']: 'trade'
        }
        selected_view = st.sidebar.radio(LANGUAGES[lang]['data_view'], view_options)
        
        # 确定最终视图类型
        final_view_type = view_mapping[selected_view]
    else:
        # 在异常视图下，需要选择市场
        if not metadata_df.empty:
            market_options = metadata_df[['market_id', 'question']].copy()
            market_options['display_name'] = market_options['market_id'].astype(str) + " - " + market_options['question'].str[:50] + "..."
            selected_display = st.sidebar.selectbox(LANGUAGES[lang]['select_market'], market_options['display_name'].tolist())
            selected_market_id = market_options[market_options['display_name'] == selected_display]['market_id'].values[0]
        else:
            selected_market_id = None
            st.sidebar.warning("No market data available")
        
        final_view_type = 'anomaly'
    
    return lang, selected_market_id, final_view_type

def display_market_info(market_info, lang):
    """显示市场信息"""
    st.subheader(f"{LANGUAGES[lang]['market_info']}: {market_info['question'][:50]}...")
    
    # 显示市场详情
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(LANGUAGES[lang]['market_id'], str(market_info['market_id']))
    with col2:
        st.metric(LANGUAGES[lang]['volume_24hr'], f"${market_info['volume_24hr']:,.2f}")
    with col3:
        st.metric(LANGUAGES[lang]['liquidity'], f"${market_info['liquidity']:,.2f}")
    
    st.markdown(f"{LANGUAGES[lang]['question']}: {market_info['question']}")
    st.markdown(f"{LANGUAGES[lang]['end_date']}: {market_info['end_date']}")

def create_header(lang):
    """创建页面头部"""
    st.title(LANGUAGES[lang]['title'])
    st.markdown(f"""
    {LANGUAGES[lang]['project']}  
    {LANGUAGES[lang]['current_stage']}
    """)

def create_footer(lang):
    """创建页脚"""
    st.divider()
    st.caption(LANGUAGES[lang]['footer'])