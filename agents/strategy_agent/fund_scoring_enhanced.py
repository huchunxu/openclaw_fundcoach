"""
增强版基金打分系统

功能：
- 多因子综合评分（支持动态权重）
- 风险调整后的收益评分
- 行业分散度考虑
- 基金经理稳定性因子
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta


class EnhancedFundScoringSystem:
    """增强版基金打分系统"""
    
    def __init__(self, factor_weights: Optional[Dict[str, float]] = None, 
                 risk_free_rate: float = 0.02):
        """
        初始化增强打分系统
        
        Args:
            factor_weights: 因子权重配置
            risk_free_rate: 无风险利率（年化）
        """
        if factor_weights is None:
            # 默认权重配置，更注重风险调整后收益
            self.factor_weights = {
                'risk_adjusted_return': 0.30,  # 风险调整后收益
                'consistency': 0.20,           # 收益一致性
                'drawdown_control': 0.20,      # 回撤控制
                'growth_quality': 0.15,        # 成长质量
                'fund_stability': 0.15         # 基金稳定性
            }
        else:
            self.factor_weights = factor_weights
            
        # 验证权重和为1
        total_weight = sum(self.factor_weights.values())
        if abs(total_weight - 1.0) > 1e-6:
            for key in self.factor_weights:
                self.factor_weights[key] /= total_weight
                
        self.risk_free_rate = risk_free_rate
        
    def calculate_risk_adjusted_return_factor(self, backtest_results: Dict) -> float:
        """
        计算风险调整后收益因子
        综合夏普率、索提诺比率等指标
        """
        sharpe_ratio = backtest_results.get('sharpe_ratio', 0)
        sortino_ratio = backtest_results.get('sortino_ratio', 0)
        calmar_ratio = backtest_results.get('calmar_ratio', 0)
        
        # 标准化各比率到合理范围
        sharpe_norm = min(max(sharpe_ratio / 2.0, 0.0), 1.0)
        sortino_norm = min(max(sortino_ratio / 2.5, 0.0), 1.0)
        calmar_norm = min(max(calmar_ratio / 1.5, 0.0), 1.0)
        
        # 加权平均
        risk_adj_score = (sharpe_norm * 0.4 + sortino_norm * 0.4 + calmar_norm * 0.2)
        return risk_adj_score
    
    def calculate_consistency_factor(self, nav_history: pd.DataFrame) -> float:
        """
        计算收益一致性因子
        基于月度/季度收益的稳定性
        """
        if nav_history.empty or len(nav_history) < 30:
            return 0.0
            
        # 按月计算收益
        nav_history['date'] = pd.to_datetime(nav_history['date'])
        nav_history = nav_history.set_index('date').sort_index()
        monthly_returns = nav_history['nav'].resample('M').last().pct_change().dropna()
        
        if len(monthly_returns) < 3:
            return 0.0
            
        # 计算正收益月份比例
        positive_months_ratio = (monthly_returns > 0).mean()
        
        # 计算收益的标准差（越小越一致）
        return_std = monthly_returns.std()
        consistency_from_std = max(0, 1 - return_std * 5)  # 标准差越大，一致性越低
        
        # 综合一致性得分
        consistency_score = (positive_months_ratio * 0.6 + consistency_from_std * 0.4)
        return min(max(consistency_score, 0.0), 1.0)
    
    def calculate_drawdown_control_factor(self, backtest_results: Dict) -> float:
        """
        计算回撤控制因子
        """
        max_drawdown = backtest_results.get('max_drawdown', 0)
        avg_drawdown = backtest_results.get('avg_drawdown', 0)
        recovery_time = backtest_results.get('avg_recovery_days', 365)
        
        # 最大回撤控制（目标：<-25%）
        max_dd_score = max(0, 1 + max_drawdown / 0.25)  # max_drawdown为负值
        
        # 平均回撤控制
        avg_dd_score = max(0, 1 + avg_drawdown / 0.15)
        
        # 恢复时间控制（目标：<180天）
        recovery_score = max(0, 1 - recovery_time / 180)
        
        drawdown_score = (max_dd_score * 0.5 + avg_dd_score * 0.3 + recovery_score * 0.2)
        return min(max(drawdown_score, 0.0), 1.0)
    
    def calculate_growth_quality_factor(self, nav_history: pd.DataFrame, 
                                     backtest_results: Dict) -> float:
        """
        计算成长质量因子
        结合增长性和稳定性
        """
        annual_return = backtest_results.get('annual_return', 0)
        volatility = backtest_results.get('volatility', 1)
        
        # 增长性得分（年化收益>10%为优秀）
        growth_score = min(max(annual_return / 0.15, 0.0), 1.0)
        
        # 稳定性得分（波动率<20%为优秀）
        stability_score = max(0, 1 - volatility / 0.2)
        
        # 成长质量 = 增长性 * 稳定性
        growth_quality_score = growth_score * stability_score
        return min(max(growth_quality_score, 0.0), 1.0)
    
    def calculate_fund_stability_factor(self, fund_data: Dict) -> float:
        """
        计算基金稳定性因子
        基于基金规模、成立时间、基金经理稳定性等
        """
        fund_size = fund_data.get('fund_size', 0)  # 亿元
        establish_date_str = fund_data.get('establish_date', '2020-01-01')
        
        try:
            establish_date = datetime.strptime(establish_date_str, '%Y-%m-%d')
            days_since_establish = (datetime.now() - establish_date).days
            years_since_establish = days_since_establish / 365.25
        except:
            years_since_establish = 1.0
        
        # 规模稳定性（50-200亿为最佳）
        if 50 <= fund_size <= 200:
            size_score = 1.0
        elif fund_size < 10 or fund_size > 500:
            size_score = 0.3
        else:
            size_score = 0.7
        
        # 成立时间稳定性（>3年为稳定）
        time_score = min(max(years_since_establish / 5.0, 0.0), 1.0)
        
        stability_score = (size_score * 0.6 + time_score * 0.4)
        return min(max(stability_score, 0.0), 1.0)
    
    def calculate_all_enhanced_factors(self, fund_code: str, fund_data: Dict,
                                    nav_history: pd.DataFrame, 
                                    backtest_results: Dict) -> Dict[str, float]:
        """
        计算所有增强因子
        """
        factors = {
            'risk_adjusted_return': self.calculate_risk_adjusted_return_factor(backtest_results),
            'consistency': self.calculate_consistency_factor(nav_history),
            'drawdown_control': self.calculate_drawdown_control_factor(backtest_results),
            'growth_quality': self.calculate_growth_quality_factor(nav_history, backtest_results),
            'fund_stability': self.calculate_fund_stability_factor(fund_data)
        }
        
        return factors
    
    def calculate_composite_score(self, factors: Dict[str, float]) -> float:
        """
        计算综合评分
        """
        score = 0.0
        for factor_name, weight in self.factor_weights.items():
            factor_value = factors.get(factor_name, 0.0)
            score += weight * factor_value
            
        return score
    
    def score_single_fund_enhanced(self, fund_code: str, fund_data: Dict, 
                                 nav_history: pd.DataFrame, backtest_results: Dict) -> Dict:
        """
        对单只基金进行增强打分
        """
        # 计算所有增强因子
        factors = self.calculate_all_enhanced_factors(
            fund_code, fund_data, nav_history, backtest_results
        )
        
        # 计算综合评分
        composite_score = self.calculate_composite_score(factors)
        
        result = {
            'fund_code': fund_code,
            'composite_score': composite_score,
            'factors': factors,
            'factor_weights': self.factor_weights,
            'scoring_version': 'enhanced_v1'
        }
        
        return result
    
    def score_multiple_funds_enhanced(self, fund_data_dict: Dict[str, Dict], 
                                   nav_history_dict: Dict[str, pd.DataFrame],
                                   backtest_results_dict: Dict[str, Dict]) -> pd.DataFrame:
        """
        对多只基金进行增强打分
        """
        scores = []
        
        for fund_code in fund_data_dict.keys():
            if (fund_code in nav_history_dict and 
                fund_code in backtest_results_dict):
                
                score_result = self.score_single_fund_enhanced(
                    fund_code,
                    fund_data_dict[fund_code],
                    nav_history_dict[fund_code],
                    backtest_results_dict[fund_code]
                )
                scores.append(score_result)
        
        # 转换为DataFrame
        if not scores:
            return pd.DataFrame()
            
        score_df = pd.DataFrame(scores)
        return score_df