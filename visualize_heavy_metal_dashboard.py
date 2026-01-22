"""
중금속 데이터 시각화 대시보드
Streamlit 확장 가능한 구조로 설계
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import Rectangle
import numpy as np
import warnings
#import os
warnings.filterwarnings('ignore')

# 한글 폰트 설정 (NanumGothic.ttf 사용)
fontpath = 'NanumGothic.ttf'


plt.rc('font', family='NanumGothic')
plt.rc('axes', unicode_minus=False)


class HeavyMetalVisualizer:
    """중금속 데이터 시각화 클래스"""
    
    def __init__(self, excel_path):
        """
        초기화 및 데이터 로드
        
        Parameters:
        -----------
        excel_path : str
            엑셀 파일 경로
        """
        self.excel_path = excel_path
        self.df = None
        self.standards = {}
        self.units = {}
        self._load_data()
        self._load_standards()
    
    def _load_data(self):
        """Sheet1 데이터 로드 및 전처리"""
        self.df = pd.read_excel(self.excel_path, sheet_name='Sheet1')
        
        # 월 컬럼 처리 (2018.01 형식을 연도와 월로 분리)
        if '월' in self.df.columns:
            def extract_month(x):
                """월 값에서 월 숫자 추출"""
                try:
                    x_str = str(x)
                    if '.' in x_str:
                        # 2018.01 형식
                        parts = x_str.split('.')
                        if len(parts) >= 2:
                            month_str = parts[1].strip()
                            if month_str.isdigit():
                                return int(month_str)
                    # 숫자만 있는 경우
                    if str(x).isdigit():
                        return int(x)
                    # 그 외의 경우 (예: '연평균' 등)는 NaN 반환
                    return np.nan
                except:
                    return np.nan
            
            self.df['월_숫자'] = self.df['월'].apply(extract_month)
            
            # '연평균' 등 월 정보가 없는 행은 제거 (월별 데이터만 사용)
            initial_count = len(self.df)
            self.df = self.df[self.df['월_숫자'].notna()].copy()
            removed_count = initial_count - len(self.df)
            if removed_count > 0:
                print(f"월 정보가 없는 행 {removed_count}개 제거됨 (예: '연평균' 행)")
        
        # 결측치 처리: 같은 지역, 같은 연도의 다른 달 수치들의 중앙값으로 채우기
        self._fill_missing_values()
        
        print(f"데이터 로드 완료: {len(self.df)}행")
        print(f"지역 수: {self.df['지역'].nunique()}")
        print(f"연도 범위: {self.df['연도'].min()} ~ {self.df['연도'].max()}")
    
    def _fill_missing_values(self):
        """결측치를 같은 지역, 같은 연도의 다른 달 수치들의 중앙값으로 채우기"""
        metals = ['Pb', 'Cd', 'As']
        
        for metal in metals:
            # 지역과 연도별로 그룹화하여 중앙값 계산
            median_by_region_year = self.df.groupby(['지역', '연도'])[metal].transform('median')
            
            # 결측치만 중앙값으로 채우기
            self.df[metal] = self.df[metal].fillna(median_by_region_year)
            
            filled_count = self.df[metal].isna().sum()
            if filled_count > 0:
                # 여전히 결측치가 있으면 전체 중앙값으로 채우기
                overall_median = self.df[metal].median()
                self.df[metal] = self.df[metal].fillna(overall_median)
                print(f"{metal} 결측치 처리 완료 (전체 중앙값 사용: {overall_median})")
    
    def _load_standards(self):
        """Sheet2에서 기준값과 단위 로드"""
        standards_df = pd.read_excel(self.excel_path, sheet_name='Sheet2')
        
        # 기준값 추출 (두 번째 행)
        if len(standards_df) >= 2:
            standards_row = standards_df.iloc[1]
            units_row = standards_df.iloc[0]
            
            self.standards = {
                'Pb': float(standards_row['Pb']),
                'Cd': float(standards_row['Cd']),
                'As': float(standards_row['As'])
            }
            
            self.units = {
                'Pb': str(units_row['Pb']),
                'Cd': str(units_row['Cd']),
                'As': str(units_row['As'])
            }
        
        print(f"기준값 로드 완료:")
        print(f"  Pb: {self.standards['Pb']} {self.units['Pb']}")
        print(f"  Cd: {self.standards['Cd']} {self.units['Cd']}")
        print(f"  As: {self.standards['As']} {self.units['As']}")
    
    
    def plot_national_yearly_trend(self, save_path=None):
        """
        전체 대한민국 연도별 평균 중금속 추이 시각화
        
        Parameters:
        -----------
        save_path : str, optional
            저장할 파일 경로
        """
        # 연도별 평균 계산
        yearly_avg = self.df.groupby('연도')[['Pb', 'Cd', 'As']].mean().reset_index()
        yearly_avg = yearly_avg.sort_values('연도')
        
        # 그래프 생성
        fig, axes = plt.subplots(3, 1, figsize=(12, 10))
        
        metals = ['Pb', 'Cd', 'As']
        metal_names = ['Pb (납)', 'Cd (카드뮴)', 'As (비소)']
        colors = ['#2C3E50', '#3498DB', '#E74C3C']
        
        for idx, (metal, name, color) in enumerate(zip(metals, metal_names, colors)):
            ax = axes[idx]
            
            # 연도별 평균 선 그래프
            ax.plot(yearly_avg['연도'], yearly_avg[metal], 
                   marker='o', linewidth=2.5, markersize=8, 
                   color=color, label=f'{name} 평균')
            
            # y축 범위 설정
            data_min = np.min(yearly_avg[metal].values)
            data_max = np.max(yearly_avg[metal].values)
            y_range = data_max - data_min
            ax.set_ylim(max(0, data_min - y_range * 0.1), data_max + y_range * 0.1)
            
            # 세밀한 y축 눈금 설정 (0.0001 단위까지 비교 가능)
            # 주요 눈금: 데이터 범위에 따라 자동 조정
            if data_max < 0.1:
                major_step = 0.01
                minor_step = 0.001
            elif data_max < 1.0:
                major_step = 0.1
                minor_step = 0.01
            else:
                major_step = max(0.1, y_range / 10)
                minor_step = major_step / 10
            
            y_min, y_max = ax.get_ylim()
            major_ticks = np.arange(0, y_max + major_step, major_step)
            minor_ticks = np.arange(0, y_max + minor_step, minor_step)
            ax.set_yticks(major_ticks)
            ax.set_yticks(minor_ticks, minor=True)
            ax.set_yticklabels([f'{x:.4f}' if x < 1.0 else f'{x:.2f}' for x in major_ticks])
            
            ax.set_xlabel('연도', fontsize=12, fontweight='bold')
            ax.set_ylabel(f'{name} 농도 ({self.units[metal]})', fontsize=12, fontweight='bold')
            ax.set_title(f'전체 대한민국 {name} 연도별 평균 추이', fontsize=14, fontweight='bold', pad=15)
            ax.legend(fontsize=10, loc='best')
            ax.grid(True, alpha=0.3, which='major')
            ax.grid(True, alpha=0.1, which='minor')
            ax.set_xticks(yearly_avg['연도'])
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"\n그래프가 '{save_path}'로 저장되었습니다.")
        else:
            plt.show()
        
        return fig
    
    def plot_region_yearly_trend(self, region, view_mode='전체연도', selected_year=None, save_path=None):
        """
        특정 지역의 연도별 평균 중금속 추이 시각화
        
        Parameters:
        -----------
        region : str
            지역명
        view_mode : str
            보기 모드 ('전체연도' 또는 '특정연도')
        selected_year : int, optional
            특정 연도 선택 (view_mode가 '특정연도'일 때 사용)
        save_path : str, optional
            저장할 파일 경로
        """
        # 해당 지역 데이터 필터링
        region_df = self.df[self.df['지역'] == region].copy()
        
        if len(region_df) == 0:
            print(f"경고: '{region}' 지역 데이터를 찾을 수 없습니다.")
            return None
        
        # 그래프 생성
        fig, axes = plt.subplots(3, 1, figsize=(12, 10))
        
        metals = ['Pb', 'Cd', 'As']
        metal_names = ['Pb (납)', 'Cd (카드뮴)', 'As (비소)']
        colors = ['#2C3E50', '#3498DB', '#E74C3C']
        
        if view_mode == '전체연도':
            # 전체연도 모드: X축은 연도(2018~2024), Y축은 해당 연도의 월별 데이터 전체 평균값
            yearly_avg = region_df.groupby('연도')[['Pb', 'Cd', 'As']].mean().reset_index()
            yearly_avg = yearly_avg.sort_values('연도')
            
            for idx, (metal, name, color) in enumerate(zip(metals, metal_names, colors)):
                ax = axes[idx]
                
                # 연도별 평균 선 그래프
                ax.plot(yearly_avg['연도'], yearly_avg[metal], 
                       marker='o', linewidth=2.5, markersize=8, 
                       color=color, label=f'{name} 평균')
                
                # y축 범위 설정
                data_min = np.min(yearly_avg[metal].values)
                data_max = np.max(yearly_avg[metal].values)
                y_range = data_max - data_min
                ax.set_ylim(max(0, data_min - y_range * 0.1), data_max + y_range * 0.1)
                
                # 세밀한 y축 눈금 설정
                if data_max < 0.1:
                    major_step = 0.01
                    minor_step = 0.001
                elif data_max < 1.0:
                    major_step = 0.1
                    minor_step = 0.01
                else:
                    major_step = max(0.1, y_range / 10)
                    minor_step = major_step / 10
                
                y_min, y_max = ax.get_ylim()
                major_ticks = np.arange(0, y_max + major_step, major_step)
                minor_ticks = np.arange(0, y_max + minor_step, minor_step)
                ax.set_yticks(major_ticks)
                ax.set_yticks(minor_ticks, minor=True)
                ax.set_yticklabels([f'{x:.4f}' if x < 1.0 else f'{x:.2f}' for x in major_ticks])
                
                ax.set_xlabel('연도', fontsize=12, fontweight='bold')
                ax.set_ylabel(f'{name} 농도 ({self.units[metal]})', fontsize=12, fontweight='bold')
                ax.set_title(f'{region} {name} 연도별 평균 추이 (전체연도)', fontsize=14, fontweight='bold', pad=15)
                ax.legend(fontsize=10, loc='best')
                ax.grid(True, alpha=0.3, which='major')
                ax.grid(True, alpha=0.1, which='minor')
                ax.set_xticks(yearly_avg['연도'])
        
        else:  # 특정연도 모드
            # 특정연도 모드: X축은 1월~12월, Y축은 월별 중금속 수치
            if selected_year is None:
                selected_year = region_df['연도'].max()
            
            filtered_df = region_df[region_df['연도'] == selected_year].copy()
            filtered_df = filtered_df.sort_values('월_숫자')
            
            if len(filtered_df) == 0:
                print(f"경고: '{region}' 지역의 {selected_year}년 데이터를 찾을 수 없습니다.")
                return None
            
            for idx, (metal, name, color) in enumerate(zip(metals, metal_names, colors)):
                ax = axes[idx]
                
                # 월별 데이터 선 그래프
                ax.plot(filtered_df['월_숫자'], filtered_df[metal], 
                       marker='o', linewidth=2.5, markersize=8, 
                       color=color, label=f'{name} 측정값')
                
                # y축 범위 설정
                data_min = np.min(filtered_df[metal].values)
                data_max = np.max(filtered_df[metal].values)
                y_range = data_max - data_min
                ax.set_ylim(max(0, data_min - y_range * 0.1), data_max + y_range * 0.1)
                
                # 세밀한 y축 눈금 설정
                if data_max < 0.1:
                    major_step = 0.01
                    minor_step = 0.001
                elif data_max < 1.0:
                    major_step = 0.1
                    minor_step = 0.01
                else:
                    major_step = max(0.1, y_range / 10)
                    minor_step = major_step / 10
                
                y_min, y_max = ax.get_ylim()
                major_ticks = np.arange(0, y_max + major_step, major_step)
                minor_ticks = np.arange(0, y_max + minor_step, minor_step)
                ax.set_yticks(major_ticks)
                ax.set_yticks(minor_ticks, minor=True)
                ax.set_yticklabels([f'{x:.4f}' if x < 1.0 else f'{x:.2f}' for x in major_ticks])
                
                ax.set_xlabel('월', fontsize=12, fontweight='bold')
                ax.set_ylabel(f'{name} 농도 ({self.units[metal]})', fontsize=12, fontweight='bold')
                ax.set_title(f'{region} {selected_year}년 {name} 월별 측정치', fontsize=14, fontweight='bold', pad=15)
                ax.set_xticks(range(1, 13))
                ax.set_xlim(0.5, 12.5)
                ax.legend(fontsize=10, loc='best')
                ax.grid(True, alpha=0.3, which='major')
                ax.grid(True, alpha=0.1, which='minor')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"\n그래프가 '{save_path}'로 저장되었습니다.")
        else:
            plt.show()
        
        return fig
    
    def plot_region_year_monthly(self, region, year, save_path=None):
        """
        특정 지역과 연도의 월별 중금속 비교 시각화
        
        Parameters:
        -----------
        region : str
            지역명
        year : int
            연도
        save_path : str, optional
            저장할 파일 경로
        """
        # 해당 지역과 연도 데이터 필터링
        filtered_df = self.df[(self.df['지역'] == region) & (self.df['연도'] == year)].copy()
        
        if len(filtered_df) == 0:
            print(f"경고: '{region}' 지역의 {year}년 데이터를 찾을 수 없습니다.")
            return None
        
        # 월별로 정렬
        filtered_df = filtered_df.sort_values('월_숫자')
        
        # 그래프 생성
        fig, axes = plt.subplots(3, 1, figsize=(12, 10))
        
        metals = ['Pb', 'Cd', 'As']
        metal_names = ['Pb (납)', 'Cd (카드뮴)', 'As (비소)']
        colors = ['#2C3E50', '#3498DB', '#E74C3C']
        
        for idx, (metal, name, color) in enumerate(zip(metals, metal_names, colors)):
            ax = axes[idx]
            
            # 월별 데이터 선 그래프
            ax.plot(filtered_df['월_숫자'], filtered_df[metal], 
                   marker='o', linewidth=2.5, markersize=8, 
                   color=color, label=f'{name} 측정값')
            
            # y축 범위 설정
            data_min = np.min(filtered_df[metal].values)
            data_max = np.max(filtered_df[metal].values)
            y_range = data_max - data_min
            ax.set_ylim(max(0, data_min - y_range * 0.1), data_max + y_range * 0.1)
            
            # 세밀한 y축 눈금 설정 (0.0001 단위까지 비교 가능)
            if data_max < 0.1:
                major_step = 0.01
                minor_step = 0.001
            elif data_max < 1.0:
                major_step = 0.1
                minor_step = 0.01
            else:
                major_step = max(0.1, y_range / 10)
                minor_step = major_step / 10
            
            y_min, y_max = ax.get_ylim()
            major_ticks = np.arange(0, y_max + major_step, major_step)
            minor_ticks = np.arange(0, y_max + minor_step, minor_step)
            ax.set_yticks(major_ticks)
            ax.set_yticks(minor_ticks, minor=True)
            ax.set_yticklabels([f'{x:.4f}' if x < 1.0 else f'{x:.2f}' for x in major_ticks])
            
            ax.set_xlabel('월', fontsize=12, fontweight='bold')
            ax.set_ylabel(f'{name} 농도 ({self.units[metal]})', fontsize=12, fontweight='bold')
            ax.set_title(f'{region} {year}년 {name} 월별 측정치', fontsize=14, fontweight='bold', pad=15)
            ax.set_xticks(range(1, 13))
            ax.set_xlim(0.5, 12.5)
            ax.legend(fontsize=10, loc='best')
            ax.grid(True, alpha=0.3, which='major')
            ax.grid(True, alpha=0.1, which='minor')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"\n그래프가 '{save_path}'로 저장되었습니다.")
        else:
            plt.show()
        
        return fig
    
    def get_available_regions(self):
        """사용 가능한 지역 목록 반환"""
        return sorted(self.df['지역'].unique().tolist())
    
    def get_available_years(self):
        """사용 가능한 연도 목록 반환"""
        return sorted(self.df['연도'].unique().tolist())
    
    def analyze_national_yearly_trend(self):
        """전체 대한민국 연도별 추이 AI 해석"""
        yearly_avg = self.df.groupby('연도')[['Pb', 'Cd', 'As']].mean().reset_index()
        yearly_avg = yearly_avg.sort_values('연도')
        
        analysis = {
            'Pb': self._analyze_metal_trend(yearly_avg, 'Pb', '납'),
            'Cd': self._analyze_metal_trend(yearly_avg, 'Cd', '카드뮴'),
            'As': self._analyze_metal_trend(yearly_avg, 'As', '비소')
        }
        
        return analysis
    
    def analyze_region_yearly_trend(self, region):
        """지역별 연도별 추이 AI 해석"""
        region_df = self.df[self.df['지역'] == region].copy()
        if len(region_df) == 0:
            return None
        
        yearly_avg = region_df.groupby('연도')[['Pb', 'Cd', 'As']].mean().reset_index()
        yearly_avg = yearly_avg.sort_values('연도')
        
        analysis = {
            'region': region,
            'Pb': self._analyze_metal_trend(yearly_avg, 'Pb', '납'),
            'Cd': self._analyze_metal_trend(yearly_avg, 'Cd', '카드뮴'),
            'As': self._analyze_metal_trend(yearly_avg, 'As', '비소')
        }
        
        return analysis
    
    def analyze_region_monthly(self, region, year):
        """지역별 월별 비교 AI 해석"""
        filtered_df = self.df[(self.df['지역'] == region) & (self.df['연도'] == year)].copy()
        if len(filtered_df) == 0:
            return None
        
        filtered_df = filtered_df.sort_values('월_숫자')
        
        analysis = {
            'region': region,
            'year': year,
            'Pb': self._analyze_metal_monthly(filtered_df, 'Pb', '납'),
            'Cd': self._analyze_metal_monthly(filtered_df, 'Cd', '카드뮴'),
            'As': self._analyze_metal_monthly(filtered_df, 'As', '비소')
        }
        
        return analysis
    
    def _analyze_metal_trend(self, data, metal, metal_name):
        """중금속 연도별 추세 분석"""
        values = data[metal].values
        years = data['연도'].values
        
        # 최신값과 기준값 비교
        latest_value = values[-1]
        standard = self.standards[metal]
        
        # 추세 분석 (선형 회귀 기울기)
        if len(years) > 1:
            slope = np.polyfit(range(len(years)), values, 1)[0]
            trend = "증가" if slope > 0 else "감소" if slope < 0 else "안정"
        else:
            slope = 0
            trend = "안정"
        
        # 변화율 계산
        if len(values) > 1:
            change_rate = ((values[-1] - values[0]) / values[0]) * 100 if values[0] != 0 else 0
        else:
            change_rate = 0
        
        # 위험 수준 판단
        risk_level = "정상"
        if latest_value > standard * 1.5:
            risk_level = "매우 위험"
        elif latest_value > standard * 1.2:
            risk_level = "위험"
        elif latest_value > standard:
            risk_level = "주의"
        
        # 경고 메시지 생성
        warnings = []
        recommendations = []
        
        if risk_level in ["위험", "매우 위험"]:
            warnings.append(f"{metal_name}({metal}) 농도가 기준치를 크게 초과하고 있습니다.")
            recommendations.append(f"해당 지역의 {metal_name} 오염원을 즉시 조사하고 관리가 필요합니다.")
        
        if trend == "증가" and slope > 0:
            warnings.append(f"{metal_name}({metal}) 농도가 지속적으로 증가하는 추세입니다.")
            recommendations.append(f"증가 원인 파악을 위한 정밀 조사가 필요합니다.")
        
        if change_rate > 20:
            warnings.append(f"최근 {metal_name}({metal}) 농도가 {abs(change_rate):.1f}% 크게 변화했습니다.")
            recommendations.append(f"급격한 변화 원인을 분석하고 대응 방안을 마련해야 합니다.")
        
        if risk_level == "정상" and trend == "안정":
            recommendations.append(f"{metal_name}({metal}) 농도는 안정적으로 관리되고 있습니다.")
        
        # 해석 텍스트 생성
        interpretation = f"""
**{metal_name}({metal}) 분석 결과:**

- **현재 농도**: {latest_value:.4f} {self.units[metal]}
- **기준치**: {standard:.4f} {self.units[metal]}
- **추세**: {trend} ({slope:.6f} {self.units[metal]}/년)
- **위험 수준**: {risk_level}
- **변화율**: {change_rate:+.1f}%
"""
        
        return {
            'metal': metal,
            'metal_name': metal_name,
            'latest_value': latest_value,
            'standard': standard,
            'trend': trend,
            'slope': slope,
            'change_rate': change_rate,
            'risk_level': risk_level,
            'warnings': warnings,
            'recommendations': recommendations,
            'interpretation': interpretation
        }
    
    def _analyze_metal_monthly(self, data, metal, metal_name):
        """중금속 월별 데이터 분석"""
        values = data[metal].values
        months = data['월_숫자'].values
        
        # 평균값과 기준값 비교
        avg_value = np.mean(values)
        max_value = np.max(values)
        min_value = np.min(values)
        standard = self.standards[metal]
        
        # 변동성 분석 (표준편차)
        std_value = np.std(values)
        cv = (std_value / avg_value * 100) if avg_value != 0 else 0  # 변동계수
        
        # 위험 수준 판단
        risk_level = "정상"
        if max_value > standard * 1.5:
            risk_level = "매우 위험"
        elif max_value > standard * 1.2:
            risk_level = "위험"
        elif max_value > standard:
            risk_level = "주의"
        
        # 경고 메시지 생성
        warnings = []
        recommendations = []
        
        if risk_level in ["위험", "매우 위험"]:
            warnings.append(f"{metal_name}({metal}) 농도가 일부 월에 기준치를 크게 초과했습니다.")
            recommendations.append(f"해당 월의 {metal_name} 오염원을 조사하고 관리가 필요합니다.")
        
        if cv > 30:
            warnings.append(f"{metal_name}({metal}) 농도가 월별로 크게 변동하고 있습니다.")
            recommendations.append(f"계절적 요인이나 특정 시기의 오염원을 분석해야 합니다.")
        
        # 최고값이 있는 월 찾기
        max_month_idx = np.argmax(values)
        max_month = int(months[max_month_idx])
        
        if max_value > standard:
            recommendations.append(f"{max_month}월에 {metal_name}({metal}) 농도가 가장 높았습니다. 해당 시기의 특별 관리가 필요합니다.")
        
        if risk_level == "정상":
            recommendations.append(f"{metal_name}({metal}) 농도는 전반적으로 안정적으로 관리되고 있습니다.")
        
        # 해석 텍스트 생성
        interpretation = f"""
**{metal_name}({metal}) 월별 분석 결과:**

- **평균 농도**: {avg_value:.4f} {self.units[metal]}
- **최대 농도**: {max_value:.4f} {self.units[metal]} ({max_month}월)
- **최소 농도**: {min_value:.4f} {self.units[metal]}
- **기준치**: {standard:.4f} {self.units[metal]}
- **변동성**: {cv:.1f}% (표준편차: {std_value:.4f})
- **위험 수준**: {risk_level}
"""
        
        return {
            'metal': metal,
            'metal_name': metal_name,
            'avg_value': avg_value,
            'max_value': max_value,
            'min_value': min_value,
            'max_month': max_month,
            'standard': standard,
            'std_value': std_value,
            'cv': cv,
            'risk_level': risk_level,
            'warnings': warnings,
            'recommendations': recommendations,
            'interpretation': interpretation
        }


def main():
    """메인 실행 함수"""
    # 파일 경로
    excel_path = '중금속_통합_18-24년_연평균_요약.xlsx'
    
    # 시각화 객체 생성
    visualizer = HeavyMetalVisualizer(excel_path)
    
    # 1. 전체 대한민국 연도별 평균 추이
    print("\n" + "="*60)
    print("1. 전체 대한민국 연도별 평균 중금속 추이")
    print("="*60)
    visualizer.plot_national_yearly_trend('전체_대한민국_연도별_평균_추이.png')
    
    # 2. 특정 지역 연도별 평균 추이 (예: 서울특별시)
    print("\n" + "="*60)
    print("2. 특정 지역 연도별 평균 중금속 추이 (서울특별시)")
    print("="*60)
    visualizer.plot_region_yearly_trend('서울특별시', '서울특별시_연도별_평균_추이.png')
    
    # 3. 특정 지역과 연도의 월별 비교 (예: 서울특별시 2023년)
    print("\n" + "="*60)
    print("3. 특정 지역과 연도의 월별 중금속 비교 (서울특별시 2023년)")
    print("="*60)
    visualizer.plot_region_year_monthly('서울특별시', 2023, '서울특별시_2023년_월별_비교.png')
    
    print("\n" + "="*60)
    print("시각화 완료!")
    print("="*60)


if __name__ == '__main__':
    main()
