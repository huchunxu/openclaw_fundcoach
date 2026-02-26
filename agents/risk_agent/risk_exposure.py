"""
风险暴露分析模块

功能：
- 因子风险暴露分析
- 行业集中度分析
- 风格漂移检测
- 相关性风险分析
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional


class RiskExposureAnalyzer:
    """风险暴露分析器"""
    
    def __init__(self):
        pass
        
    def analyze_factor_exposure(self, portfolio_weights: Dict[str, float],
                              fund_factors: Dict[str, Dict[str, float]]) -> Dict[str, float]:
        """
        分析因子风险暴露
        
        Args:
            portfolio_weights: 组合权重
            fund_factors: 基金因子数据 {fund_code: {factor_name: factor_value}}
            
        Returns:
            组合层面的因子暴露
        """
        if not portfolio_weights or not fund_factors:
            return {}
            
        # 获取所有因子名称
        all_factors = set()
        for factors in fund_factors.values():
            all_factors.update(factors.keys())
            
        portfolio_factor_exposure = {}
        
        for factor in all_factors:
            exposure = 0.0
            total_weight = 0.0
            
            for fund_code, weight in portfolio_weights.items():
                if fund_code in fund_factors and factor in fund_factors[fund_code]:
                    exposure += weight * fund_factors[fund_code][factor]
                    total_weight += weight
                    
            if total_weight > 0:
                portfolio_factor_exposure[factor] = exposure / total_weight
                
        return portfolio_factor_exposure
    
    def analyze_sector_concentration(self, portfolio_weights: Dict[str, float],
                                 fund_sectors: Dict[str, str]) -> Dict:
        """
        分析行业集中度
        
        Args:
            portfolio_weights: 组合权重
            fund_sectors: 基金行业分类 {fund_code: sector}
            
        Returns:
            行业集中度分析结果
        """
        if not portfolio_weights or not fund_sectors:
            return {}
            
        sector_weights = {}
        
        for fund_code, weight in portfolio_weights.items():
            if fund_code in fund_sectors:
                sector = fund_sectors[fund_code]
                sector_weights[sector] = sector_weights.get(sector, 0) + weight
                
        # 计算集中度指标
        weights_array = np.array(list(sector_weights.values()))
        herfindahl_index = np.sum(weights_array ** 2)
        max_sector_concentration = np.max(weights_array) if len(weights_array) > 0 else 0
        
        concentration_analysis = {
            'sector_weights': sector_weights,
            'herfindahl_index': herfindahl_index,
            'max_sector_concentration': max_sector_concentration,
            'num_sectors': len(sector_weights),
            'is_diversified': herfindahl_index < 0.3  # 简单阈值判断
        }
        
        return concentration_analysis
    
    def detect_style_drift(self, current_portfolio: Dict[str, float],
                         benchmark_portfolio: Dict[str, float],
                         threshold: float = 0.1) -> Dict:
        """
        检测风格漂移
        
        Args:
            current_portfolio: 当前组合权重
            benchmark_portfolio: 基准组合权重
            threshold: 漂移阈值
            
        Returns:
            风格漂移检测结果
        """
        # 计算权重差异
        all_funds = set(current_portfolio.keys()) | set(benchmark_portfolio.keys())
        drift_metrics = {}
        
        total_drift = 0.0
        drifted_funds = []
        
        for fund in all_funds:
            current_weight = current_portfolio.get(fund, 0.0)
            benchmark_weight = benchmark_portfolio.get(fund, 0.0)
            weight_diff = abs(current_weight - benchmark_weight)
            
            if weight_diff > threshold:
                drifted_funds.append({
                    'fund_code': fund,
                    'current_weight': current_weight,
                    'benchmark_weight': benchmark_weight,
                    'drift_amount': weight_diff
                })
                
            total_drift += weight_diff
            
        drift_analysis = {
            'total_drift': total_drift,
            'drifted_funds': drifted_funds,
            'has_significant_drift': total_drift > threshold * 2,
            'num_drifted_funds': len(drifted_funds)
        }
        
        return drift_analysis
    
    def analyze_correlation_risk(self, fund_nav_dict: Dict[str, pd.DataFrame]) -> Dict:
        """
        分析相关性风险
        
        Args:
            fund_nav_dict: 基金净值数据
            
        Returns:
            相关性风险分析
        """
        if len(fund_nav_dict) < 2:
            return {'avg_correlation': 0.0, 'max_correlation': 0.0, 'correlation_matrix': {}}
            
        # 对齐日期
        all_dates = None
        for nav_data in fund_nav_dict.values():
            if nav_data.empty:
                continue
            if all_dates is None:
                all_dates = set(nav_data['date'])
            else:
                all_dates = all_dates.intersection(set(nav_data['date']))
                
        if not all_dates or len(all_dates) < 2:
            return {'avg_correlation': 0.0, 'max_correlation': 0.0, 'correlation_matrix': {}}
            
        all_dates = sorted(list(all_dates))
        returns_matrix = []
        fund_codes = list(fund_nav_dict.keys())
        
        for fund_code in fund_codes:
            nav_data = fund_nav_dict[fund_code]
            fund_returns = []
            
            for date in all_dates:
                nav_on_date = nav_data[nav_data['date'] == date]
                if not nav_on_date.empty:
                    fund_returns.append(nav_on_date['nav'].iloc[0])
                else:
                    fund_returns.append(np.nan)
                    
            fund_returns_series = pd.Series(fund_returns).pct_change().dropna()
            returns_matrix.append(fund_returns_series.values)
            
        if len(returns_matrix) < 2:
            return {'avg_correlation': 0.0, 'max_correlation': 0.0, 'correlation_matrix': {}}
            
        # 计算相关性矩阵
        try:
            returns_df = pd.DataFrame(returns_matrix).T
            correlation_matrix = returns_df.corr().values
            
            # 提取上三角元素（排除对角线）
            mask = np.triu(np.ones_like(correlation_matrix, dtype=bool), k=1)
            upper_triangle = correlation_matrix[mask]
            
            if len(upper_triangle) > 0:
                avg_correlation = np.mean(upper_triangle)
                max_correlation = np.max(upper_triangle)
            else:
                avg_correlation = 0.0
                max_correlation = 0.0
                
            correlation_analysis = {
                'avg_correlation': avg_correlation,
                'max_correlation': max_correlation,
                'correlation_matrix': dict(zip(
                    [(fund_codes[i], fund_codes[j]) for i in range(len(fund_codes)) 
                     for j in range(i+1, len(fund_codes))],
                    upper_triangle.tolist() if len(upper_triangle) > 0 else []
                )),
                'is_highly_correlated': avg_correlation > 0.7
            }
            
            return correlation_analysis
            
        except Exception as e:
            return {'avg_correlation': 0.0, 'max_correlation': 0.0, 'correlation_matrix': {}}
    
    def comprehensive_risk_exposure_analysis(self, portfolio_weights: Dict[str, float],
                                          fund_factors: Dict[str, Dict[str, float]],
                                          fund_sectors: Dict[str, str],
                                          fund_nav_dict: Dict[str, pd.DataFrame],
                                          benchmark_portfolio: Optional[Dict[str, float]] = None) -> Dict:
        """
        综合风险暴露分析
        """
        analysis_results = {}
        
        # 因子暴露分析
        analysis_results['factor_exposure'] = self.analyze_factor_exposure(
            portfolio_weights, fund_factors
        )
        
        # 行业集中度分析
        analysis_results['sector_concentration'] = self.analyze_sector_concentration(
            portfolio_weights, fund_sectors
        )
        
        # 相关性风险分析
        analysis_results['correlation_risk'] = self.analyze_correlation_risk(fund_nav_dict)
        
        # 风格漂移检测（如果有基准组合）
        if benchmark_portfolio:
            analysis_results['style_drift'] = self.detect_style_drift(
                portfolio_weights, benchmark_portfolio
            )
            
        return analysis_results