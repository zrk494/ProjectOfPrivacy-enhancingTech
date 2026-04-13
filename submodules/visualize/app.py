import streamlit as st
from config import PAGE_TITLE, PAGE_LAYOUT, PAGE_ICON, LANGUAGES
from data import load_market_metadata
from views import (
    display_metadata_view,
    display_timeseries_view,
    display_trade_view,
    display_anomaly_view
)
from utils import create_sidebar, display_market_info, create_header, create_footer

# 页面配置
st.set_page_config(
    page_title=PAGE_TITLE,
    layout=PAGE_LAYOUT,
    page_icon=PAGE_ICON
)

def main():
    """主应用函数"""
    # 加载市场元数据
    metadata_df = load_market_metadata('en')  # 初始语言设为英文
    
    if metadata_df.empty:
        st.error("无法加载市场元数据，请检查数据文件路径。")
        return
    
    # 语言选择（默认英文）
    lang = 'en'
    
    # 创建侧边栏
    lang, selected_market_id, view_type = create_sidebar(lang, metadata_df)

    # 创建页面头部
    create_header(lang)
    
    # 显示市场信息（仅在非异常视图下）
    if selected_market_id and view_type != 'anomaly':
        market_info = metadata_df[metadata_df['market_id'] == selected_market_id].iloc[0]
        display_market_info(market_info, lang)
    
    # 显示数据基于视图选择
    st.divider()
    
    # 如果是异常视图，单独渲染
    if view_type == 'anomaly' and selected_market_id:
        # 显示异常可视化专用视图
        st.title("异常检测可视化" if lang == 'zh' else "Anomaly Detection Visualization")
        st.markdown("### 专用异常检测分析界面" if lang == 'zh' else "### Dedicated Anomaly Detection Analysis Interface")
        display_anomaly_view(selected_market_id, lang)
    else:
        # 主页面保持显示原有三个视图
        if view_type == 'metadata':
            display_metadata_view(metadata_df, lang)
        elif view_type == 'timeseries' and selected_market_id:
            display_timeseries_view(selected_market_id, lang)
        elif view_type == 'trade' and selected_market_id:
            display_trade_view(selected_market_id, lang)
    
    # 创建页脚
    create_footer(lang)

if __name__ == "__main__":
    main()