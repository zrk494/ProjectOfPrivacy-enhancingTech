import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from config import LANGUAGES, DEFAULT_SCORE_METHOD
from data import (
    load_polymarket_anomaly_data,
    load_sniper_detection_data,
    load_sniper_detailed_cases,
    load_sniper_all_cases,
    load_bucket_features,
    load_bucket_scores,
    load_market_stress_summary,
    load_all_stress_events,
    process_anomaly_data
)

def display_anomaly_view(market_id, lang):
    """显示异常数据视图"""
    st.subheader(f"{LANGUAGES[lang]['anomaly_detection']}")
    
    # 异常检测类型选择
    anomaly_type = st.selectbox(
        LANGUAGES[lang]['select_anomaly_type'],
        [LANGUAGES[lang]['polymarket_anomaly'], LANGUAGES[lang]['sniper_detection']]
    )
    
    if anomaly_type == LANGUAGES[lang]['polymarket_anomaly']:
        display_polymarket_anomaly_new(market_id, lang)
    else:
        display_sniper_detection_cards(lang)

def display_polymarket_anomaly_new(market_id, lang):
    """显示重构后的多市场异常检测视图 - 三层下钻式"""
    
    # 视图层级选择
    view_layer = st.radio(
        LANGUAGES[lang]['select_view_layer'],
        [
            LANGUAGES[lang]['market_overview'],
            LANGUAGES[lang]['single_market_events'],
            LANGUAGES[lang]['single_event_diagnostics']
        ],
        horizontal=True
    )
    
    if view_layer == LANGUAGES[lang]['market_overview']:
        display_layer1_market_overview(lang)
    elif view_layer == LANGUAGES[lang]['single_market_events']:
        display_layer2_single_market_events(market_id, lang)
    else:
        display_layer3_single_event_diagnostics(market_id, lang)

def display_layer1_market_overview(lang):
    """第一层：全市场宏观概览"""
    st.subheader(LANGUAGES[lang]['layer_1_title'])
    
    # 加载数据
    summary_df = load_market_stress_summary(DEFAULT_SCORE_METHOD)
    all_events_df = load_all_stress_events(DEFAULT_SCORE_METHOD)
    
    if summary_df.empty and all_events_df.empty:
        st.warning(LANGUAGES[lang]['no_anomaly_data'])
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top 压力事件排行榜
        st.subheader(LANGUAGES[lang]['top_stress_events'])
        if not all_events_df.empty:
            top_events = all_events_df.sort_values('peak_stress_score', ascending=False).head(10)
            # 从 market_file 提取 market_id（去掉 _YES 后缀）
            if 'market_file' in top_events.columns:
                top_events['market_id'] = top_events['market_file'].str.split('_').str[0]
            display_cols = ['market_id', 'start_datetime', 'duration_minutes', 'total_amount', 'peak_stress_score']
            existing_cols = [c for c in display_cols if c in top_events.columns]
            st.dataframe(top_events[existing_cols], use_container_width=True)
        else:
            st.info(LANGUAGES[lang]['no_anomaly_data'])
    
    with col2:
        # 市场健康度对比
        st.subheader(LANGUAGES[lang]['market_health_comparison'])
        if not summary_df.empty and 'stress_events' in summary_df.columns and 'market_stem' in summary_df.columns:
            fig = px.bar(
                summary_df,
                x='market_stem',
                y='stress_events',
                title=LANGUAGES[lang]['market_health_comparison'],
                labels={'stress_events': LANGUAGES[lang]['stress_events_count'], 'market_stem': LANGUAGES[lang]['market_name']},
                color='stress_events',
                color_continuous_scale='Reds'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(LANGUAGES[lang]['no_anomaly_data'])

def display_layer2_single_market_events(market_id, lang):
    """第二层：单市场事件汇总"""
    st.subheader(LANGUAGES[lang]['layer_2_title'])
    
    # 加载数据
    events_df = load_polymarket_anomaly_data(market_id, DEFAULT_SCORE_METHOD)
    
    if events_df.empty:
        st.warning(LANGUAGES[lang]['no_anomaly_data'])
        return
    
    processed_df = process_anomaly_data(events_df)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 事件归因分布
        st.subheader(LANGUAGES[lang]['event_attribution_distribution'])
        if 'dominant_driver' in processed_df.columns:
            driver_counts = processed_df['dominant_driver'].value_counts()
            driver_labels = {
                'activity': LANGUAGES[lang]['trading_activity'],
                'liquidity': LANGUAGES[lang]['liquidity_change'],
                'price_dislocation': LANGUAGES[lang]['price_dislocation'],
                'mixed': LANGUAGES[lang]['mixed_factors']
            }
            fig = px.pie(
                values=driver_counts.values,
                names=[driver_labels.get(d, d) for d in driver_counts.index],
                title=LANGUAGES[lang]['event_attribution_distribution'],
                hole=0.4
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No driver attribution data available")
    
    with col2:
        # 事件气泡图
        st.subheader(LANGUAGES[lang]['event_bubble_chart'])
        if all(c in processed_df.columns for c in ['start_datetime', 'peak_stress_score', 'total_amount', 'dominant_driver']):
            fig = px.scatter(
                processed_df,
                x='start_datetime',
                y='peak_stress_score',
                size='total_amount',
                color='dominant_driver',
                hover_data=['duration_minutes'],
                title=LANGUAGES[lang]['event_bubble_chart'],
                labels={
                    'peak_stress_score': LANGUAGES[lang]['max_stress_score'],
                    'total_amount': LANGUAGES[lang]['total_amount']
                }
            )
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Insufficient data for bubble chart")
    
    # 事件详情列表
    st.subheader(LANGUAGES[lang]['event_details_list'])
    display_cols = ['start_datetime', 'end_datetime', 'duration_minutes', 'peak_stress_score', 'total_amount', 'dominant_driver']
    existing_cols = [c for c in display_cols if c in processed_df.columns]
    st.dataframe(processed_df[existing_cols], use_container_width=True)

def display_layer3_single_event_diagnostics(market_id, lang):
    """第三层：单事件微观诊断"""
    st.subheader(LANGUAGES[lang]['layer_3_title'])
    
    # 加载数据
    events_df = load_polymarket_anomaly_data(market_id, DEFAULT_SCORE_METHOD)
    bucket_features = load_bucket_features(market_id, DEFAULT_SCORE_METHOD)
    bucket_scores = load_bucket_scores(market_id, DEFAULT_SCORE_METHOD)
    
    if events_df.empty or bucket_features.empty or bucket_scores.empty:
        st.warning(LANGUAGES[lang]['no_anomaly_data'])
        return
    
    processed_df = process_anomaly_data(events_df)
    
    # 选择事件
    event_options = []
    for idx, row in processed_df.iterrows():
        start_str = str(row.get('start_datetime', 'N/A'))
        score = row.get('peak_stress_score', 0)
        event_options.append(f"Event {idx+1}: {start_str} (Score: {score:.2f})")
    
    selected_event_idx = st.selectbox(
        LANGUAGES[lang]['select_event'],
        range(len(event_options)),
        format_func=lambda x: event_options[x]
    )
    
    selected_event = processed_df.iloc[selected_event_idx]
    
    # 获取事件时间范围
    start_time = selected_event.get('start_datetime')
    end_time = selected_event.get('end_datetime')
    
    if start_time is None or end_time is None:
        st.error("Event time range not available")
        return
    
    # 合并 bucket 数据
    merged_buckets = pd.merge(bucket_features, bucket_scores, on='bucket', how='left', suffixes=('', '_score'))
    
    if 'datetime' not in merged_buckets.columns and 'datetime' in bucket_features.columns:
        merged_buckets['datetime'] = bucket_features['datetime']
    
    if 'datetime' not in merged_buckets.columns:
        st.error("No datetime column in bucket data")
        return
    
    merged_buckets['datetime'] = pd.to_datetime(merged_buckets['datetime'])
    
    # 扩展时间范围（前后各10分钟）
    if pd.notna(start_time) and pd.notna(end_time):
        start_dt = pd.to_datetime(start_time)
        end_dt = pd.to_datetime(end_time)
        extended_start = start_dt - pd.Timedelta(minutes=10)
        extended_end = end_dt + pd.Timedelta(minutes=10)
        
        filtered_buckets = merged_buckets[
            (merged_buckets['datetime'] >= extended_start) & 
            (merged_buckets['datetime'] <= extended_end)
        ].copy()
    else:
        filtered_buckets = merged_buckets
    
    if filtered_buckets.empty:
        st.warning("No bucket data available for the selected time range")
        return
    
    # 显示四个对齐的子图
    fig = go.Figure()
    
    # 创建子图布局
    from plotly.subplots import make_subplots
    fig = make_subplots(
        rows=4, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        subplot_titles=(
            LANGUAGES[lang]['composite_stress_score'],
            LANGUAGES[lang]['trading_activity_chart'],
            LANGUAGES[lang]['liquidity_status_chart'],
            LANGUAGES[lang]['price_trend_chart']
        )
    )
    
    # 1. 综合压力评分图
    if 'stress_score' in filtered_buckets.columns:
        fig.add_trace(
            go.Scatter(
                x=filtered_buckets['datetime'],
                y=filtered_buckets['stress_score'],
                mode='lines',
                name='Stress Score',
                line=dict(color='red', width=2)
            ),
            row=1, col=1
        )
        
        # 添加异常阈值线（如果有）
        if 'is_stress_anomaly' in filtered_buckets.columns:
            threshold = filtered_buckets[filtered_buckets['is_stress_anomaly'] == True]['stress_score'].min()
            if pd.notna(threshold):
                fig.add_hline(
                    y=threshold,
                    line_dash="dash",
                    line_color="orange",
                    annotation_text=LANGUAGES[lang]['anomaly_threshold'],
                    row=1, col=1
                )
    
    # 高亮事件区间
    if pd.notna(start_time) and pd.notna(end_time):
        fig.add_vrect(
            x0=start_dt,
            x1=end_dt,
            fillcolor="rgba(255, 0, 0, 0.1)",
            line_width=0,
            annotation_text=LANGUAGES[lang]['event_interval'],
            annotation_position="top left"
        )
    
    # 2. 交易活跃度图
    if 'trade_count' in filtered_buckets.columns:
        fig.add_trace(
            go.Bar(
                x=filtered_buckets['datetime'],
                y=filtered_buckets['trade_count'],
                name='Trade Count',
                marker=dict(color='blue')
            ),
            row=2, col=1
        )
    
    if 'amount_sum' in filtered_buckets.columns:
        fig.add_trace(
            go.Scatter(
                x=filtered_buckets['datetime'],
                y=filtered_buckets['amount_sum'],
                mode='lines',
                name='Amount Sum',
                line=dict(color='green', width=2),
                yaxis='y2'
            ),
            row=2, col=1
        )
    
    # 3. 流动性状态图
    if 'spread' in filtered_buckets.columns:
        fig.add_trace(
            go.Scatter(
                x=filtered_buckets['datetime'],
                y=filtered_buckets['spread'],
                mode='lines',
                name='Spread',
                line=dict(color='purple', width=2)
            ),
            row=3, col=1
        )
    
    if 'total_depth' in filtered_buckets.columns:
        fig.add_trace(
            go.Scatter(
                x=filtered_buckets['datetime'],
                y=filtered_buckets['total_depth'],
                mode='lines',
                name='Total Depth',
                fill='tozeroy',
                line=dict(color='orange', width=1),
                yaxis='y2'
            ),
            row=3, col=1
        )
    
    # 4. 价格走势图
    if 'midpoint' in filtered_buckets.columns:
        fig.add_trace(
            go.Scatter(
                x=filtered_buckets['datetime'],
                y=filtered_buckets['midpoint'],
                mode='lines',
                name='Midpoint',
                line=dict(color='darkblue', width=2)
            ),
            row=4, col=1
        )
    
    fig.update_layout(
        height=1000,
        showlegend=True,
        title_text=LANGUAGES[lang]['layer_3_title']
    )
    
    st.plotly_chart(fig, use_container_width=True)

def display_sniper_detection_cards(lang):
    """显示狙击手检测卡片式视图 - 保持不变"""
    st.subheader(LANGUAGES[lang]['sniper_detection'])
    
    # 加载狙击手检测数据
    sniper_df = load_sniper_detection_data()
    detailed_cases = load_sniper_detailed_cases()
    
    if sniper_df.empty:
        st.warning(LANGUAGES[lang]['no_anomaly_data'])
        return
    
    # 显示狙击手统计信息
    st.subheader(LANGUAGES[lang]['sniper_statistics'])
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(LANGUAGES[lang]['sniper_count'], len(sniper_df))
    with col2:
        if 'anomaly_score' in sniper_df.columns:
            avg_score = sniper_df['anomaly_score'].mean()
            st.metric(LANGUAGES[lang]['avg_anomaly_score'], f"{avg_score:.4f}")
        else:
            st.metric(LANGUAGES[lang]['avg_anomaly_score'], "N/A")
    with col3:
        st.metric(LANGUAGES[lang]['verified_cases_count'], len(detailed_cases))
    
    # 狙击手分数分布图表
    st.subheader(LANGUAGES[lang]['sniper_score_distribution'])
    if 'anomaly_score' in sniper_df.columns:
        fig = go.Figure()
        fig.add_trace(go.Histogram(
            x=sniper_df['anomaly_score'],
            nbinsx=20,
            marker_color='purple'
        ))
        fig.update_layout(
            xaxis_title=LANGUAGES[lang]['avg_anomaly_score'],
            yaxis_title=LANGUAGES[lang]['frequency'],
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # 卡片式展示已验证案例
    if detailed_cases:
        st.subheader(LANGUAGES[lang]['verified_sniper_cases'])
        for case in detailed_cases:
            with st.container():
                # 卡片样式
                st.markdown(f"""
                <div style="border: 1px solid #e0e0e0; border-radius: 8px; padding: 16px; margin-bottom: 16px; background-color: #f9f9f9;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h3 style="margin-top: 0; color: #333;">{LANGUAGES[lang]['sniper_attack_case']}</h3>
                        <span style="background-color: #9c27b0; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px;">Type B</span>
                    </div>
                """, unsafe_allow_html=True)
                
                # 基本信息
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**{LANGUAGES[lang]['case_rank']}** #{case.get('rank')}")
                    st.write(f"**{LANGUAGES[lang]['session_id']}** {case.get('session_id')}")
                with col2:
                    st.write(f"**{LANGUAGES[lang]['duration_seconds']}** {case.get('duration_seconds')} {LANGUAGES[lang]['seconds_unit']}")
                    st.write(f"**{LANGUAGES[lang]['avg_anomaly_score']}** {case.get('anomaly_score'):.4f}")
                with col3:
                    profit = case.get('profit', 0)
                    st.write(f"**{LANGUAGES[lang]['profit']}** ${profit:.2f}")
                    # 根据利润显示不同颜色
                    if profit > 0:
                        st.markdown(f"<span style='color: #4caf50; font-weight: bold;'>{LANGUAGES[lang]['profit_positive']}</span>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<span style='color: #ff6b6b; font-weight: bold;'>{LANGUAGES[lang]['profit_negative']}</span>", unsafe_allow_html=True)
                
                # 详细信息（可展开）
                with st.expander(LANGUAGES[lang]['view_details']):
                    st.subheader(LANGUAGES[lang]['trade_details'])
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**{LANGUAGES[lang]['buy_operation']}")
                        st.write(f"- {LANGUAGES[lang]['amount_label']} ${case.get('buy', {}).get('amount', 0):.2f}")
                        st.write(f"- {LANGUAGES[lang]['price_label']} ${case.get('buy', {}).get('price', 0):.2f}")
                        st.write(f"- {LANGUAGES[lang]['time_label']} {case.get('buy', {}).get('time', 'N/A')}")
                        st.write(f"- {LANGUAGES[lang]['date_label']} {case.get('buy', {}).get('date', 'N/A')}")
                        if 'tx_hash' in case.get('buy', {}):
                            st.write(f"- {LANGUAGES[lang]['tx_hash']}: {case.get('buy', {}).get('tx_hash', 'N/A')}")
                    with col2:
                        st.write(f"**{LANGUAGES[lang]['sell_operation']}")
                        st.write(f"- {LANGUAGES[lang]['amount_label']} ${case.get('sell', {}).get('amount', 0):.2f}")
                        st.write(f"- {LANGUAGES[lang]['price_label']} ${case.get('sell', {}).get('price', 0):.2f}")
                        st.write(f"- {LANGUAGES[lang]['time_label']} {case.get('sell', {}).get('time', 'N/A')}")
                        st.write(f"- {LANGUAGES[lang]['date_label']} {case.get('sell', {}).get('date', 'N/A')}")
                        if 'tx_hash' in case.get('sell', {}):
                            st.write(f"- {LANGUAGES[lang]['tx_hash']}: {case.get('sell', {}).get('tx_hash', 'N/A')}")
                    
                    # 显示攻击窗口图片
                    image_path = case.get('image')
                    if image_path:
                        st.subheader(LANGUAGES[lang]['attack_window_visualization'])
                        from config import SNIPER_IMAGES_DIR
                        # 移除 image_path 中的 'images/' 前缀
                        if image_path.startswith('images/'):
                            image_path = image_path[7:]
                        full_image_path = SNIPER_IMAGES_DIR / image_path
                        if full_image_path.exists():
                            st.image(str(full_image_path), use_column_width=True)
                        else:
                            st.warning(f"{LANGUAGES[lang]['image_not_found']} {image_path}")
                
                st.markdown("</div>", unsafe_allow_html=True)
    
    # 卡片式展示狙击手候选
    st.subheader(LANGUAGES[lang]['sniper_candidates_list'])
    
    # 按可疑度排名排序
    if 'suspicious_rank' in sniper_df.columns:
        sniper_df = sniper_df.sort_values('suspicious_rank', ascending=True)
    
    # 分页显示
    page_size = 5
    total_pages = (len(sniper_df) + page_size - 1) // page_size
    
    # 使用会话状态管理页码
    if 'sniper_page' not in st.session_state:
        st.session_state.sniper_page = 1
    
    # 分页控件
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button(LANGUAGES[lang]['previous'], disabled=st.session_state.sniper_page == 1, key='sniper_prev'):
            st.session_state.sniper_page -= 1
    with col2:
        st.write(f"{LANGUAGES[lang]['page']}: {st.session_state.sniper_page} / {total_pages}")
    with col3:
        if st.button(LANGUAGES[lang]['next'], disabled=st.session_state.sniper_page == total_pages, key='sniper_next'):
            st.session_state.sniper_page += 1
    
    # 确保页码在有效范围内
    page = max(1, min(st.session_state.sniper_page, total_pages))
    st.session_state.sniper_page = page
    
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    page_df = sniper_df.iloc[start_idx:end_idx]
    
    # 显示候选卡片
    for idx, row in page_df.iterrows():
        with st.container():
            # 卡片样式
            st.markdown(f"""
            <div style="border: 1px solid #e0e0e0; border-radius: 8px; padding: 16px; margin-bottom: 16px; background-color: #f9f9f9;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h4 style="margin-top: 0; color: #333;">{LANGUAGES[lang]['sniper_candidate']}</h4>
                    <span style="background-color: #673ab7; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px;">{LANGUAGES[lang]['candidate_label']}</span>
                </div>
            """, unsafe_allow_html=True)
            
            # 基本信息
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"**{LANGUAGES[lang]['session_id']}** {row.get('session_id', 'N/A')}")
                st.write(f"**{LANGUAGES[lang]['suspicious_rank']}** #{row.get('suspicious_rank', 'N/A')}")
            with col2:
                st.write(f"**{LANGUAGES[lang]['num_trades']}** {row.get('num_trades', 'N/A')}")
                st.write(f"**{LANGUAGES[lang]['total_volume']}** ${row.get('total_volume', 0):.2f}")
            with col3:
                anomaly_score = row.get('anomaly_score', 0)
                st.write(f"**{LANGUAGES[lang]['avg_anomaly_score']}** {anomaly_score:.4f}")
                # 根据异常分数显示不同颜色
                if anomaly_score < -0.6:
                    st.markdown(f"<span style='color: #ff6b6b; font-weight: bold;'>{LANGUAGES[lang]['high_risk']}</span>", unsafe_allow_html=True)
                elif anomaly_score < -0.5:
                    st.markdown(f"<span style='color: #ff9800; font-weight: bold;'>{LANGUAGES[lang]['medium_risk']}</span>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<span style='color: #4caf50; font-weight: bold;'>{LANGUAGES[lang]['low_risk']}</span>", unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    # 分页控制
    st.write(f"{LANGUAGES[lang]['showing_records']} {start_idx + 1}-{min(end_idx, len(sniper_df))} {LANGUAGES[lang]['to']} {len(sniper_df)} {LANGUAGES[lang]['records']}")
