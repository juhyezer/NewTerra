"""
중금속 데이터 시각화 Streamlit 대시보드
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import os
import warnings
warnings.filterwarnings('ignore')

# 시각화 모듈 import
from visualize_heavy_metal_dashboard import HeavyMetalVisualizer

# 페이지 설정
st.set_page_config(
    page_title="중금속 데이터 시각화 대시보드",
    page_icon="📊",
    layout="wide"
)

# 한글 폰트 설정
fontpath = os.path.join(os.path.dirname(__file__), 'NanumGothic.ttf')

# 폰트를 Matplotlib에 등록
if os.path.exists(fontpath):
    font = fm.FontProperties(fname=fontpath)
    fm.fontManager.addfont(fontpath)
    # 한글 폰트를 기본 폰트로 설정
    plt.rc('font', family='NanumGothic')
else:
    # 폰트 파일이 없을 경우 시스템 기본 한글 폰트 사용
    plt.rc('font', family='AppleGothic')

plt.rc('axes', unicode_minus=False)

# 제목
st.title("📊 중금속 데이터 시각화 대시보드")
st.markdown("---")

# 데이터 로드
@st.cache_data
def load_visualizer():
    """시각화 객체 로드 (캐싱)"""
    #excel_path = os.path.join(os.path.dirname(__file__), '중금속_통합_18-24년_연평균_요약.xlsx')
    return HeavyMetalVisualizer('중금속_통합_18-24년_연평균_요약.xlsx')

visualizer = load_visualizer()

# 메인 레이아웃: 왼쪽 메인 영역, 오른쪽 사이드바
col_main, col_sidebar = st.columns([3, 1])

with col_sidebar:
    st.header("📋 선택 옵션")
    
    # 시각화 타입 선택
    visualization_type = st.selectbox(
        "시각화 유형",
        ["전체 대한민국 연도별 추이", "지역별 연도별 추이", "지역별 월별 비교"]
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
    st.markdown("**데이터 정보**")
    st.markdown(f"- 지역 수: {len(available_regions)}개")
    st.markdown(f"- 연도 범위: {min(available_years)}~{max(available_years)}년")

with col_main:
    # 시각화 실행
    if visualization_type == "전체 대한민국 연도별 추이":
        st.header("🇰🇷 전체 대한민국 연도별 평균 중금속 추이")
        st.markdown("2018년부터 2024년까지 전국 평균 중금속 농도 변화를 보여줍니다.")
        
        fig = visualizer.plot_national_yearly_trend()
        st.pyplot(fig)
        plt.close(fig)
        
        # 통계 정보
        with st.expander("📈 통계 정보 보기"):
            yearly_avg = visualizer.df.groupby('연도')[['Pb', 'Cd', 'As']].mean().reset_index()
            st.dataframe(yearly_avg, use_container_width=True)

    elif visualization_type == "지역별 연도별 추이":
        st.header("📍 지역별 연도별 평균 중금속 추이")
        st.markdown("특정 지역의 연도별 평균 중금속 농도 변화를 보여줍니다. (2018~2024년)")
        
        # 선택된 지역 확인
        if selected_region and selected_region != "전체":
            fig = visualizer.plot_region_yearly_trend(selected_region)
            if fig:
                st.pyplot(fig)
                plt.close(fig)
                
                # 통계 정보
                with st.expander("📈 통계 정보 보기"):
                    region_df = visualizer.df[visualizer.df['지역'] == selected_region]
                    yearly_avg = region_df.groupby('연도')[['Pb', 'Cd', 'As']].mean().reset_index()
                    st.dataframe(yearly_avg, use_container_width=True)
        else:
            st.info("👈 오른쪽에서 지역을 선택해주세요.")

    elif visualization_type == "지역별 월별 비교":
        st.header("📅 지역별 월별 중금속 비교")
        st.markdown(f"특정 지역과 연도의 12개월 중금속 측정치를 비교합니다. (각 지역별로 7년치 데이터 제공)")
        
        # 선택된 지역과 연도 확인
        if selected_region and selected_region != "전체" and selected_year:
            fig = visualizer.plot_region_year_monthly(selected_region, selected_year)
            if fig:
                st.pyplot(fig)
                plt.close(fig)
                
                # 통계 정보
                with st.expander("📈 통계 정보 보기"):
                    filtered_df = visualizer.df[
                        (visualizer.df['지역'] == selected_region) & 
                        (visualizer.df['연도'] == selected_year)
                    ].sort_values('월_숫자')
                    st.dataframe(filtered_df[['월_숫자', 'Pb', 'Cd', 'As']], use_container_width=True)
        else:
            st.info("👈 오른쪽에서 지역과 연도를 선택해주세요.")

# 푸터
st.markdown("---")
st.markdown("**데이터 출처**: 중금속 통합 18-24년 연평균 요약 데이터")
st.markdown("**주의**: 결측치는 같은 지역, 같은 연도의 다른 달 수치들의 중앙값으로 채워졌습니다.")
