"""
增强版风险暴露分析模块

功能：
- 完整的因子暴露分析
- 行业/风格集中度监控  
- 相关性风险评估
- 风险贡献分解
- 流动性风险分析
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from scipy.stats import pearsonr


class EnhancedRiskExposureAnalyzer:
    """增强版风险暴露分析器"""
    
    def __init__(self):
        # 行业分类映射
        self.sector_mapping = {
            'technology': '科技',
            'healthcare': '医疗', 
            'finance': '金融',
            'consumer': '消费',
            'energy': '能源',
            'industrial': '工业',
            'materials': '材料',
            'utilities': '公用事业',
            'real_estate': '房地产',
            'communication': '通信'
        }
        
        # 风格分类
        self.style_categories = ['value', 'growth', 'balanced']
        
    def analyze_factor_exposure(self, portfolio_weights: Dict[str, float], 
                              fund_factors_dict: Dict[str, Dict[str, float]]) -> Dict:
        """
        分析因子暴露
        
        Args:
            portfolio_weights: 组合权重
            fund_factors_dict: 基金因子数据
            
        Returns:
            因子暴露分析结果
        """
        if not portfolio_weights or not fund_factors_dict:
            return {}
            
        # 计算组合层面的因子暴露
        portfolio_factor_exposure = {}
        total_weight = sum(portfolio_weights.values())
        
        if total_weight == 0:
            return {}
            
        # 获取所有因子名称
        all_factors = set()
        for factors in fund_factors_dict.values():
            all_factors.update(factors.keys())
            
        for factor in all_factors:
            weighted_exposure = 0.0
            valid_weight = 0.0
            
            for fund_code, weight in portfolio_weights.items():
                if fund_code in fund_factors_dict:
                    factor_value = fund_factors_dict[fund_code].get(factor, 0.0)
                    weighted_exposure += weight * factor_value
                    valid_weight += weight
                    
            if valid_weight > 0:
                portfolio_factor_exposure[factor] = weighted_exposure / valid_weight
                
        # 计算因子暴露风险指标
        factor_risk_metrics = {}
        if portfolio_factor_exposure:
            factor_values = list(portfolio_factor_exposure.values())
            factor_risk_metrics = {
                'factor_exposure_mean': np.mean(factor_values),
                'factor_exposure_std': np.std(factor_values),
                'max_factor_exposure': max(factor_values),
                'min_factor_exposure': min(factor_values),
                'factor_concentration': max(factor_values) / sum(abs(v) for v in factor_values) if sum(abs(v) for v in factor_values) > 0 else 0
            }
            
        return {
            'portfolio_factor_exposure': portfolio_factor_exposure,
            'factor_risk_metrics': factor_risk_metrics
        }
    
    def analyze_sector_concentration(self, portfolio_weights: Dict[str, float],
                                  fund_sectors: Dict[str, str]) -> Dict:
        """
        分析行业集中度
        
        Args:
            portfolio_weights: 组合权重
            fund_sectors: 基金行业分类
            
        Returns:
            行业集中度分析结果
        """
        if not portfolio_weights or not fund_sectors:
            return {}
            
        # 按行业汇总权重
        sector_weights = {}
        total_weight = sum(portfolio_weights.values())
        
        if total_weight == 0:
            return {}
            
        for fund_code, weight in portfolio_weights.items():
            if fund_code in fund_sectors:
                sector = fund_sectors[fund_code]
                if sector not in sector_weights:
                    sector_weights[sector] = 0.0
                sector_weights[sector] += weight
                
        # 归一化行业权重
        for sector in sector_weights:
            sector_weights[sector] /= total_weight
            
        # 计算集中度指标
        sector_weights_list = list(sector_weights.values())
        if sector_weights_list:
            max_sector_concentration = max(sector_weights_list)
            herfindahl_index = sum(w**2 for w in sector_weights_list)
            entropy = -sum(w * np.log(w) for w in sector_weights_list if w > 0)
            
            concentration_metrics = {
                'max_sector_concentration': max_sector_concentration,
                'herfindahl_index': herfindahl_index,
                'entropy': entropy,
                'num_sectors': len(sector_weights),
                'sector_diversification_score': 1 - herfindahl_index  # 越高越分散
            }
        else:
            concentration_metrics = {
                'max_sector_concentration': 0,
                'herfindahl_index': 0,
                'entropy': 0,
                'num_sectors': 0,
                'sector_diversification_score': 0
            }
            
        return {
            'sector_weights': sector_weights,
            'concentration_metrics': concentration_metrics
        }
    
    def analyze_style_concentration(self, portfolio_weights: Dict[str, float],
                                 fund_styles: Dict[str, str]) -> Dict:
        """
        分析投资风格集中度
        
        Args:
            portfolio_weights: 组合权重  
            fund_styles: 基金风格分类
            
        Returns:
            风格集中度分析结果
        """
        if not portfolio_weights or not fund_styles:
            return {}
            
        # 按风格汇总权重
        style_weights = {}
        total_weight = sum(portfolio_weights.values())
        
        if total_weight == 0:
            return {}
            
        for fund_code, weight in portfolio_weights.items():
            if fund_code in fund_styles:
                style = fund_styles[fund_code]
                if style not in style_weights:
                    style_weights[style] = 0.0
                style_weights[style] += weight
                
        # 归一化风格权重
        for style in style_weights:
            style_weights[style] /= total_weight
            
        # 计算风格集中度
        style_weights_list = list(style_weights.values())
        if style_weights_list:
            max_style_concentration = max(style_weights_list)
            style_herfindahl = sum(w**2 for w in style_weights_list)
            style_diversification_score = 1 - style_herfindahl
        else:
            max_style_concentration = 0
            style_diversification_score = 0
            
        return {
            'style_weights': style_weights,
            'max_style_concentration': max_style_concentration,
            'style_diversification_score': style_diversification_score
        }
    
    def analyze_correlation_risk(self, portfolio_weights: Dict[str, float],
                               fund_nav_dict: Dict[str, pd.DataFrame]) -> Dict:
        """
        分析相关性风险
        
        Args:
            portfolio_weights: 组合权重
            fund_nav_dict: 基金净值数据
            
        Returns:
            相关性风险分析结果
        """
        if not portfolio_weights or not fund_nav_dict:
            return {}
            
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
            return {'avg_correlation': 0.5, 'max_correlation': 1.0, 'correlation_risk_score': 0.5}
            
        all_dates = sorted(list(all_dates))
        
        # 构建收益率矩阵
        returns_matrix = []
        fund_codes_in_portfolio = [code for code in portfolio_weights.keys() if code in fund_nav_dict]
        
        if len(fund_codes_in_portfolio) < 2:
            return {'avg_correlation': 0.0, 'max_correlation': 0.0, 'correlation_risk_score': 0.0}
            
        for fund_code in fund_codes_in_portfolio:
            nav_data = fund_nav_dict[fund_code]
            fund_returns = []
            
            for date in all_dates:
                nav_on_date = nav_data[nav_data['date'] == date]
                if not nav_on_date.empty:
                    fund_returns.append(nav_on_date['nav'].iloc[0])
                else:
                    fund_returns.append(np.nan)
                    
            # 转换为收益率
            fund_returns_series = pd.Series(fund_returns).pct_change().dropna()
            if len(fund_returns_series) > 0:
                returns_matrix.append(fund_returns_series.values)
                
        if len(returns_matrix) < 2:
            return {'avg_correlation': 0.0, 'max_correlation': 0.0, 'correlation_risk_score': 0.0}
            
        # 计算相关性矩阵
        try:
            returns_array = np.array(returns_matrix)
            corr_matrix = np.corrcoef(returns_array)
            
            # 提取上三角相关系数（排除对角线）
            n = corr_matrix.shape[0]
            correlations = []
            for i in range(n):
                for j in range(i+1, n):
                    correlations.append(corr_matrix[i, j])
                    
            if correlations:
                avg_correlation = np.mean(correlations)
                max_correlation = np.max(correlations)
                # 相关性风险得分：相关性越高，风险越大
                correlation_risk_score = avg_correlation
            else:
                avg_correlation = 0.0
                max_correlation = 0.0
                correlation_risk_score = 0.0
                
        except:
            avg_correlation = 0.5
            max_correlation = 1.0
            correlation_risk_score = 0.5
            
        return {
            'avg_correlation': avg_correlation,
            'max_correlation': max_correlation,
            'correlation_risk_score': correlation_risk_score
        }
    
    def analyze_liquidity_risk(self, portfolio_weights: Dict[str, float],
                             fund_basic_info: Dict[str, Dict]) -> Dict:
        """
        分析流动性风险
        
        Args:
            portfolio_weights: 组合权重
            fund_basic_info: 基金基本信息（包含规模等）
            
        Returns:
            流动性风险分析结果
        """
        if not portfolio_weights or not fund_basic_info:
            return {}
            
        liquidity_scores = []
        weighted_liquidity_score = 0.0
        total_weight = 0.0
        
        for fund_code, weight in portfolio_weights.items():
            if fund_code in fund_basic_info:
                fund_info = fund_basic_info[fund_code]
                fund_size = fund_info.get('fund_size', 0)  # 亿元
                
                # 基金规模越大，流动性越好
                if fund_size >= 100:
                    liquidity_score = 1.0
                elif fund_size >= 50:
                    liquidity_score = 0.8
                elif fund_size >= 20:
                    liquidity_score = 0.6
                elif fund_size >= 10:
                    liquidity_score = 0.4
                else:
                    liquidity_score = 0.2
                    
                weighted_liquidity_score += weight * liquidity_score
                total_weight += weight
                liquidity_scores.append(liquidity_score)
                
        if total_weight > 0:
            portfolio_liquidity_score = weighted_liquidity_score / total_weight
            liquidity_risk_score = 1 - portfolio_liquidity_score  # 流动性越差，风险越高
        else:
            portfolio_liquidity_score = 0.0
            liquidity_risk_score = 1.0
            
        return {
            'portfolio_liquidity_score': portfolio_liquidity_score,
            'liquidity_risk_score': liquidity_risk_score,
            'individual_liquidity_scores': dict(zip(portfolio_weights.keys(), liquidity_scores))
        }
    
    def comprehensive_risk_exposure_analysis(self, portfolio_weights: Dict[str, float],
                                          fund_factors_dict: Dict[str, Dict[str, float]],
                                          fund_sectors: Dict[str, str],
                                          fund_nav_dict: Dict[str, pd.DataFrame],
                                          fund_basic_info: Optional[Dict[str, Dict]] = None) -> Dict:
        """
        综合风险暴露分析
        
        Args:
            portfolio_weights: 组合权重
            fund_factors_dict: 基金因子数据
            fund_sectors: 基金行业分类
            fund_nav_dict: 基金净值数据
            fund_basic_info: 基金基本信息
            
        Returns:
            完整的风险暴露分析报告
        """
        analysis_results = {}
        
        # 因子暴露分析
        factor_exposure_result = self.analyze_factor_exposure(portfolio_weights, fund_factors_dict)
        analysis_results['factor_exposure'] = factor_exposure_result
        
        # 行业集中度分析
        sector_concentration_result = self.analyze_sector_concentration(portfolio_weights, fund_sectors)
        analysis_results['sector_concentration'] = sector_concentration_result
        
        # 风格集中度分析
        # 从因子数据中提取风格信息
        fund_styles = {}
        for fund_code, factors in fund_factors_dict.items():
            value_score = factors.get('value', 0)
            growth_score = factors.get('growth', 0)
            if abs(value_score - growth_score) < 0.2:
                fund_styles[fund_code] = 'balanced'
            elif value_score > growth_score:
                fund_styles[fund_code] = 'value'
            else:
                fund_styles[fund_code] = 'growth'
                
        style_concentration_result = self.analyze_style_concentration(portfolio_weights, fund_styles)
        analysis_results['style_concentration'] = style_concentration_result
        
        # 相关性风险分析
        correlation_risk_result = self.analyze_correlation_risk(portfolio_weights, fund_nav_dict)
        analysis_results['correlation_risk'] = correlation_risk_result
        
        # 流动性风险分析（如果有基本信息）
        if fund_basic_info:
            liquidity_risk_result = self.analyze_liquidity_risk(portfolio_weights, fund_basic_info)
            analysis_results['liquidity_risk'] = liquidity_risk_result
            
        # 综合风险评分
        risk_scores = []
        
        # 因子集中度风险
        if 'factor_risk_metrics' in factor_exposure_result:
            factor_concentration = factor_exposure_result['factor_risk_metrics'].get('factor_concentration', 0)
            risk_scores.append(factor_concentration)
            
        # 行业集中度风险
        if 'concentration_metrics' in sector_concentration_result:
            sector_concentration = sector_concentration_result['concentration_metrics'].get('max_sector_concentration', 0)
            risk_scores.append(sector_concentration)
            
        # 风格集中度风险
        style_concentration = style_concentration_result.get('max_style_concentration', 0)
        risk_scores.append(style_concentration)
        
        # 相关性风险
        correlation_risk = correlation_risk_result.get('correlation_risk_score', 0.5)
        risk_scores.append(correlation_risk)
        
        # 流动性风险
        if 'liquidity_risk' in analysis_results:
            liquidity_risk = analysis_results['liquidity_risk'].get('liquidity_risk_score', 0.5)
            risk_scores.append(liquidity_risk)
            
        if risk_scores:
            comprehensive_risk_score = np.mean(risk_scores)
        else:
            comprehensive_risk_score = 0.5
            
        analysis_results['comprehensive_risk_score'] = comprehensive_risk_score
        
        return analysis_results