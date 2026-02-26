"""
基金打分系统

功能：
- 多因子综合评分
- 权重配置
- 标准化处理
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from .factor_model import FactorModel


class FundScoringSystem:
    """基金打分系统"""
    
    def __init__(self, factor_weights: Optional[Dict[str, float]] = None):
        """
        初始化打分系统
        
        Args:
            factor_weights: 因子权重配置，默认等权重
        """
        if factor_weights is None:
            self.factor_weights = {
                'value': 0.25,
                'growth': 0.25, 
                'momentum': 0.25,
                'quality': 0.25
            }
        else:
            self.factor_weights = factor_weights
            
        # 验证权重和为1
        total_weight = sum(self.factor_weights.values())
        if abs(total_weight - 1.0) > 1e-6:
            # 归一化权重
            for key in self.factor_weights:
                self.factor_weights[key] /= total_weight
                
        self.factor_model = FactorModel()
        
    def normalize_factors(self, factors_df: pd.DataFrame) -> pd.DataFrame:
        """
        标准化因子值（Z-score标准化）
        """
        normalized_df = factors_df.copy()
        for column in factors_df.columns:
            if column != 'fund_code':
                mean_val = factors_df[column].mean()
                std_val = factors_df[column].std()
                if std_val > 1e-8:
                    normalized_df[column] = (factors_df[column] - mean_val) / std_val
                else:
                    normalized_df[column] = 0.0
                    
        return normalized_df
    
    def calculate_composite_score(self, factors: Dict[str, float]) -> float:
        """
        计算综合评分
        """
        score = 0.0
        for factor_name, weight in self.factor_weights.items():
            factor_value = factors.get(factor_name, 0.0)
            score += weight * factor_value
            
        return score
    
    def score_single_fund(self, fund_code: str, fund_data: Dict, 
                         nav_history: pd.DataFrame, backtest_results: Dict) -> Dict:
        """
        对单只基金进行打分
        """
        # 计算所有因子
        factors = self.factor_model.calculate_all_factors(
            fund_code, fund_data, nav_history, backtest_results
        )
        
        # 计算综合评分
        composite_score = self.calculate_composite_score(factors)
        
        result = {
            'fund_code': fund_code,
            'composite_score': composite_score,
            'factors': factors,
            'factor_weights': self.factor_weights
        }
        
        return result
    
    def score_multiple_funds(self, fund_data_dict: Dict[str, Dict], 
                           nav_history_dict: Dict[str, pd.DataFrame],
                           backtest_results_dict: Dict[str, Dict]) -> pd.DataFrame:
        """
        对多只基金进行打分
        """
        scores = []
        
        for fund_code in fund_data_dict.keys():
            if (fund_code in nav_history_dict and 
                fund_code in backtest_results_dict):
                
                score_result = self.score_single_fund(
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