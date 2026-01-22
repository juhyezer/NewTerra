"""
국내 중금속 농도 모니터링 시스템
메인 홈페이지 - 국내 지도 포함
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import folium
from streamlit_folium import st_folium
import os
import warnings
import numpy as np
warnings.filterwarnings('ignore')

# 시각화 모듈 import
from visualize_heavy_metal_dashboard import HeavyMetalVisualizer

# 페이지 설정
st.set_page_config(
    page_title="국내 중금속 농도 모니터링 시스템",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 한글 폰트 설정
fontpath = os.path.join(os.path.dirname(__file__), 'NanumGothic.ttf')
if os.path.exists(fontpath):
    font = fm.FontProperties(fname=fontpath)
    fm.fontManager.addfont(fontpath)
    plt.rc('font', family='NanumGothic')
else:
    plt.rc('font', family='AppleGothic')
plt.rc('axes', unicode_minus=False)

# CSS 스타일링 (화우 사이트와 유사한 디자인)
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1a1a1a;
        margin-bottom: 0.5rem;
        text-align: center;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .nav-container {
        display: flex;
        justify-content: center;
        gap: 2rem;
        margin: 2rem 0;
        padding: 1rem;
        background-color: #f8f9fa;
        border-radius: 10px;
    }
    .nav-item {
        font-size: 1.1rem;
        color: #333;
        text-decoration: none;
        padding: 0.5rem 1.5rem;
        border-radius: 5px;
        transition: all 0.3s;
    }
    .nav-item:hover {
        background-color: #e9ecef;
        color: #000;
    }
    .highlight-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin: 2rem 0;
    }
    .stat-box {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
        margin: 1rem;
    }
    .stat-number {
        font-size: 2rem;
        font-weight: bold;
        color: #667eea;
    }
    .stat-label {
        font-size: 0.9rem;
        color: #666;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# 데이터 로드 함수
@st.cache_data
def load_data():
    """중금속 데이터 로드"""
    excel_path = os.path.join(os.path.dirname(__file__), '중금속_통합_18-24년_연평균_요약.xlsx')
    if os.path.exists(excel_path):
        df = pd.read_excel(excel_path, sheet_name='Sheet1')
        return df
    return None

# 시각화 객체 로드 함수
@st.cache_data
def load_visualizer():
    """시각화 객체 로드 (캐싱)"""
    excel_path = os.path.join(os.path.dirname(__file__), '중금속_통합_18-24년_연평균_요약.xlsx')
    if os.path.exists(excel_path):
        return HeavyMetalVisualizer(excel_path)
    return None

# 지역별 좌표 정보 (한국 주요 도시)
region_coords = {
    '서울특별시': [37.5665, 126.9780],
    '부산광역시': [35.1796, 129.0756],
    '대구광역시': [35.8714, 128.6014],
    '인천광역시': [37.4563, 126.7052],
    '광주광역시': [35.1595, 126.8526],
    '대전광역시': [36.3504, 127.3845],
    '울산광역시': [35.5384, 129.3114],
    '세종특별자치시': [36.4800, 127.2890],
    '경기도': [37.4138, 127.5183],
    '강원도': [37.8228, 128.1555],
    '충청북도': [36.8000, 127.7000],
    '충청남도': [36.5184, 126.8000],
    '전라북도': [35.7175, 127.1530],
    '전라남도': [34.8679, 126.9910],
    '경상북도': [36.4919, 128.8889],
    '경상남도': [35.4606, 128.2132],
    '제주특별자치도': [33.4996, 126.5312]
}

# 메인 헤더
st.markdown('<div class="main-header">국내 중금속 농도 모니터링 시스템</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">대한민국 전역의 중금속 농도를 실시간으로 모니터링하고 분석합니다</div>', unsafe_allow_html=True)

# 네비게이션
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("🏠 홈", use_container_width=True, type="primary"):
        st.switch_page("Home.py")
with col2:
    if st.button("🎯 비전과 목표", use_container_width=True):
        st.switch_page("pages/1_비전과목표.py")
with col3:
    if st.button("💡 인사이트", use_container_width=True):
        st.switch_page("pages/2_인사이트.py")
with col4:
    if st.button("📊 데이터", use_container_width=True):
        st.switch_page("pages/3_데이터.py")

st.markdown("---")

# 데이터 로드
df = load_data()
visualizer = load_visualizer()

if visualizer is not None:
    # 최신 데이터 통계
    latest_year = visualizer.df['연도'].max() if '연도' in visualizer.df.columns else None
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="stat-box">
            <div class="stat-number">{}</div>
            <div class="stat-label">모니터링 지역</div>
        </div>
        """.format(visualizer.df['지역'].nunique() if '지역' in visualizer.df.columns else 0), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="stat-box">
            <div class="stat-number">{}</div>
            <div class="stat-label">데이터 연도 범위</div>
        </div>
        """.format(f"{visualizer.df['연도'].min()}-{visualizer.df['연도'].max()}" if '연도' in visualizer.df.columns else "N/A"), unsafe_allow_html=True)
    
    with col3:
        avg_pb = visualizer.df['Pb'].mean() if 'Pb' in visualizer.df.columns else 0
        st.markdown("""
        <div class="stat-box">
            <div class="stat-number">{:.4f}</div>
            <div class="stat-label">평균 납(Pb) 농도</div>
        </div>
        """.format(avg_pb), unsafe_allow_html=True)
    
    with col4:
        avg_cd = visualizer.df['Cd'].mean() if 'Cd' in visualizer.df.columns else 0
        st.markdown("""
        <div class="stat-box">
            <div class="stat-number">{:.4f}</div>
            <div class="stat-label">평균 카드뮴(Cd) 농도</div>
        </div>
        """.format(avg_cd), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 메인 레이아웃: 왼쪽 메인 영역, 오른쪽 사이드바
    col_main, col_sidebar = st.columns([3, 1])
    
    with col_sidebar:
        st.markdown("""
        <div style="background-color: #f8f9fa; padding: 1.5rem; border-radius: 10px; margin-bottom: 1rem;">
            <h3 style="color: #333; margin-bottom: 1rem;">📋 선택 옵션</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # 시각화 타입 선택
        visualization_type = st.selectbox(
            "시각화 유형",
            ["전체 대한민국 연도별 추이", "지역별 연도별 추이", "지역별 월별 비교"],
            key="viz_type"
        )
        
        st.markdown("---")
        
        # 지역 선택 (지역별 시각화에서 사용)
        available_regions = visualizer.get_available_regions()
        selected_region = st.selectbox(
            "📍 지역 선택",
            ["전체"] + available_regions,
            key="region_selector"
        )
        
        st.markdown("---")
        
        # 연도 선택 (월별 비교에서 사용)
        available_years = visualizer.get_available_years()
        selected_year = st.selectbox(
            "📅 연도 선택",
            available_years,
            key="year_selector"
        )
        
        st.markdown("---")
        st.markdown("""
        <div style="background-color: #ffffff; padding: 1rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <h4 style="color: #333; margin-bottom: 0.5rem;">데이터 정보</h4>
            <p style="color: #666; margin: 0.3rem 0;">- 지역 수: {}개</p>
            <p style="color: #666; margin: 0.3rem 0;">- 연도 범위: {}~{}년</p>
        </div>
        """.format(len(available_regions), min(available_years), max(available_years)), unsafe_allow_html=True)
    
    with col_main:
        # 시각화 실행
        if visualization_type == "전체 대한민국 연도별 추이":
            st.markdown("""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 10px; color: white; margin-bottom: 1.5rem;">
                <h2 style="color: white; margin: 0;">🇰🇷 전체 대한민국 연도별 평균 중금속 추이</h2>
                <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0;">2018년부터 2024년까지 전국 평균 중금속 농도 변화를 보여줍니다.</p>
            </div>
            """, unsafe_allow_html=True)
            
            fig = visualizer.plot_national_yearly_trend()
            st.pyplot(fig)
            plt.close(fig)
            
            # AI 해석 버튼
            col_btn1, col_btn2 = st.columns([1, 4])
            with col_btn1:
                ai_analyze_national = st.button("🤖 AI 해석", key="ai_national", use_container_width=True, type="primary")
            
            # AI 해석 결과 표시
            if ai_analyze_national:
                with st.spinner("AI가 그래프를 분석 중입니다..."):
                    analysis = visualizer.analyze_national_yearly_trend()
                    
                    st.markdown("---")
                    st.markdown("""
                    <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 1.5rem; border-radius: 10px; color: white; margin-bottom: 1.5rem;">
                        <h2 style="color: white; margin: 0;">🤖 AI 분석 결과</h2>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    for metal_key in ['Pb', 'Cd', 'As']:
                        metal_analysis = analysis[metal_key]
                        
                        # 위험 수준에 따른 색상
                        risk_colors = {
                            "매우 위험": "#dc3545",
                            "위험": "#fd7e14",
                            "주의": "#ffc107",
                            "정상": "#28a745"
                        }
                        risk_color = risk_colors.get(metal_analysis['risk_level'], "#6c757d")
                        
                        st.markdown(f"""
                        <div style="background-color: #ffffff; padding: 1.5rem; border-radius: 10px; border-left: 5px solid {risk_color}; margin-bottom: 1rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                            <h3 style="color: #333; margin-top: 0;">{metal_analysis['metal_name']}({metal_key}) 분석</h3>
                            {metal_analysis['interpretation']}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # 경고 및 권장사항
                        if metal_analysis['warnings']:
                            st.markdown("""
                            <div style="background-color: #fff3cd; padding: 1rem; border-radius: 8px; border-left: 4px solid #ffc107; margin-bottom: 1rem;">
                                <h4 style="color: #856404; margin-top: 0;">⚠️ 경고 사항</h4>
                            </div>
                            """, unsafe_allow_html=True)
                            for warning in metal_analysis['warnings']:
                                st.markdown(f"- ⚠️ {warning}")
                        
                        if metal_analysis['recommendations']:
                            st.markdown("""
                            <div style="background-color: #d1ecf1; padding: 1rem; border-radius: 8px; border-left: 4px solid #0c5460; margin-bottom: 1.5rem;">
                                <h4 style="color: #0c5460; margin-top: 0;">💡 관리 대안</h4>
                            </div>
                            """, unsafe_allow_html=True)
                            for rec in metal_analysis['recommendations']:
                                st.markdown(f"- 💡 {rec}")
                        
                        st.markdown("---")
            
            # 통계 정보
            with st.expander("📈 통계 정보 보기"):
                yearly_avg = visualizer.df.groupby('연도')[['Pb', 'Cd', 'As']].mean().reset_index()
                st.dataframe(yearly_avg, use_container_width=True)
        
        elif visualization_type == "지역별 연도별 추이":
            st.markdown("""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 10px; color: white; margin-bottom: 1.5rem;">
                <h2 style="color: white; margin: 0;">📍 지역별 연도별 평균 중금속 추이</h2>
                <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0;">특정 지역의 연도별 평균 중금속 농도 변화를 보여줍니다. (2018~2024년)</p>
            </div>
            """, unsafe_allow_html=True)
            
            # 선택된 지역 확인
            if selected_region and selected_region != "전체":
                fig = visualizer.plot_region_yearly_trend(selected_region)
                if fig:
                    st.pyplot(fig)
                    plt.close(fig)
                    
                    # AI 해석 버튼
                    col_btn1, col_btn2 = st.columns([1, 4])
                    with col_btn1:
                        ai_analyze_region = st.button("🤖 AI 해석", key="ai_region", use_container_width=True, type="primary")
                    
                    # AI 해석 결과 표시
                    if ai_analyze_region:
                        with st.spinner("AI가 그래프를 분석 중입니다..."):
                            analysis = visualizer.analyze_region_yearly_trend(selected_region)
                            
                            if analysis:
                                st.markdown("---")
                                st.markdown(f"""
                                <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 1.5rem; border-radius: 10px; color: white; margin-bottom: 1.5rem;">
                                    <h2 style="color: white; margin: 0;">🤖 AI 분석 결과 - {analysis['region']}</h2>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                for metal_key in ['Pb', 'Cd', 'As']:
                                    metal_analysis = analysis[metal_key]
                                    
                                    # 위험 수준에 따른 색상
                                    risk_colors = {
                                        "매우 위험": "#dc3545",
                                        "위험": "#fd7e14",
                                        "주의": "#ffc107",
                                        "정상": "#28a745"
                                    }
                                    risk_color = risk_colors.get(metal_analysis['risk_level'], "#6c757d")
                                    
                                    st.markdown(f"""
                                    <div style="background-color: #ffffff; padding: 1.5rem; border-radius: 10px; border-left: 5px solid {risk_color}; margin-bottom: 1rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                                        <h3 style="color: #333; margin-top: 0;">{metal_analysis['metal_name']}({metal_key}) 분석</h3>
                                        {metal_analysis['interpretation']}
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                    # 경고 및 권장사항
                                    if metal_analysis['warnings']:
                                        st.markdown("""
                                        <div style="background-color: #fff3cd; padding: 1rem; border-radius: 8px; border-left: 4px solid #ffc107; margin-bottom: 1rem;">
                                            <h4 style="color: #856404; margin-top: 0;">⚠️ 경고 사항</h4>
                                        </div>
                                        """, unsafe_allow_html=True)
                                        for warning in metal_analysis['warnings']:
                                            st.markdown(f"- ⚠️ {warning}")
                                    
                                    if metal_analysis['recommendations']:
                                        st.markdown("""
                                        <div style="background-color: #d1ecf1; padding: 1rem; border-radius: 8px; border-left: 4px solid #0c5460; margin-bottom: 1.5rem;">
                                            <h4 style="color: #0c5460; margin-top: 0;">💡 관리 대안</h4>
                                        </div>
                                        """, unsafe_allow_html=True)
                                        for rec in metal_analysis['recommendations']:
                                            st.markdown(f"- 💡 {rec}")
                                    
                                    st.markdown("---")
                    
                    # 통계 정보
                    with st.expander("📈 통계 정보 보기"):
                        region_df = visualizer.df[visualizer.df['지역'] == selected_region]
                        yearly_avg = region_df.groupby('연도')[['Pb', 'Cd', 'As']].mean().reset_index()
                        st.dataframe(yearly_avg, use_container_width=True)
            else:
                st.info("👈 오른쪽에서 지역을 선택해주세요.")
        
        elif visualization_type == "지역별 월별 비교":
            st.markdown("""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 10px; color: white; margin-bottom: 1.5rem;">
                <h2 style="color: white; margin: 0;">📅 지역별 월별 중금속 비교</h2>
                <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0;">특정 지역과 연도의 12개월 중금속 측정치를 비교합니다. (각 지역별로 7년치 데이터 제공)</p>
            </div>
            """, unsafe_allow_html=True)
            
            # 선택된 지역과 연도 확인
            if selected_region and selected_region != "전체" and selected_year:
                fig = visualizer.plot_region_year_monthly(selected_region, selected_year)
                if fig:
                    st.pyplot(fig)
                    plt.close(fig)
                    
                    # AI 해석 버튼
                    col_btn1, col_btn2 = st.columns([1, 4])
                    with col_btn1:
                        ai_analyze_monthly = st.button("🤖 AI 해석", key="ai_monthly", use_container_width=True, type="primary")
                    
                    # AI 해석 결과 표시
                    if ai_analyze_monthly:
                        with st.spinner("AI가 그래프를 분석 중입니다..."):
                            analysis = visualizer.analyze_region_monthly(selected_region, selected_year)
                            
                            if analysis:
                                st.markdown("---")
                                st.markdown(f"""
                                <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 1.5rem; border-radius: 10px; color: white; margin-bottom: 1.5rem;">
                                    <h2 style="color: white; margin: 0;">🤖 AI 분석 결과 - {analysis['region']} {analysis['year']}년</h2>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                for metal_key in ['Pb', 'Cd', 'As']:
                                    metal_analysis = analysis[metal_key]
                                    
                                    # 위험 수준에 따른 색상
                                    risk_colors = {
                                        "매우 위험": "#dc3545",
                                        "위험": "#fd7e14",
                                        "주의": "#ffc107",
                                        "정상": "#28a745"
                                    }
                                    risk_color = risk_colors.get(metal_analysis['risk_level'], "#6c757d")
                                    
                                    st.markdown(f"""
                                    <div style="background-color: #ffffff; padding: 1.5rem; border-radius: 10px; border-left: 5px solid {risk_color}; margin-bottom: 1rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                                        <h3 style="color: #333; margin-top: 0;">{metal_analysis['metal_name']}({metal_key}) 분석</h3>
                                        {metal_analysis['interpretation']}
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                    # 경고 및 권장사항
                                    if metal_analysis['warnings']:
                                        st.markdown("""
                                        <div style="background-color: #fff3cd; padding: 1rem; border-radius: 8px; border-left: 4px solid #ffc107; margin-bottom: 1rem;">
                                            <h4 style="color: #856404; margin-top: 0;">⚠️ 경고 사항</h4>
                                        </div>
                                        """, unsafe_allow_html=True)
                                        for warning in metal_analysis['warnings']:
                                            st.markdown(f"- ⚠️ {warning}")
                                    
                                    if metal_analysis['recommendations']:
                                        st.markdown("""
                                        <div style="background-color: #d1ecf1; padding: 1rem; border-radius: 8px; border-left: 4px solid #0c5460; margin-bottom: 1.5rem;">
                                            <h4 style="color: #0c5460; margin-top: 0;">💡 관리 대안</h4>
                                        </div>
                                        """, unsafe_allow_html=True)
                                        for rec in metal_analysis['recommendations']:
                                            st.markdown(f"- 💡 {rec}")
                                    
                                    st.markdown("---")
                    
                    # 통계 정보
                    with st.expander("📈 통계 정보 보기"):
                        filtered_df = visualizer.df[
                            (visualizer.df['지역'] == selected_region) & 
                            (visualizer.df['연도'] == selected_year)
                        ].sort_values('월_숫자')
                        st.dataframe(filtered_df[['월_숫자', 'Pb', 'Cd', 'As']], use_container_width=True)
            else:
                st.info("👈 오른쪽에서 지역과 연도를 선택해주세요.")
        
else:
    st.warning("데이터 파일을 찾을 수 없습니다. '중금속_통합_18-24년_연평균_요약.xlsx' 파일이 필요합니다.")

# 푸터
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <p>국내 중금속 농도 모니터링 시스템</p>
    <p style="font-size: 0.9rem;">© 2024 All Rights Reserved</p>
</div>
""", unsafe_allow_html=True)
