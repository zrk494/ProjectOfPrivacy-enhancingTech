import streamlit as st
from config import LANGUAGES

def display_metadata_view(metadata_df, lang):
    """显示市场元数据视图"""
    st.subheader(LANGUAGES[lang]['all_markets'])
    
    # 显示汇总统计信息
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(LANGUAGES[lang]['total_markets'], len(metadata_df))
    with col2:
        st.metric(LANGUAGES[lang]['total_volume'], f"${metadata_df['volume_24hr'].sum():,.2f}")
    with col3:
        st.metric(LANGUAGES[lang]['avg_liquidity'], f"${metadata_df['liquidity'].mean():,.2f}")
    
    # 显示元数据表格
    st.dataframe(
        metadata_df[['market_id', 'question', 'end_date', 'volume_24hr', 'liquidity']],
        width='stretch',
        column_config={
            "market_id": LANGUAGES[lang]['market_id'],
            "question": LANGUAGES[lang]['question'],
            "end_date": LANGUAGES[lang]['end_date'],
            "volume_24hr": LANGUAGES[lang]['volume_24hr'],
            "liquidity": LANGUAGES[lang]['liquidity']
        }
    )