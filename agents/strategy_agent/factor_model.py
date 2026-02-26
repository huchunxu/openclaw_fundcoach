"""
因子建模模块

功能：
- 价值因子计算
- 成长因子计算  
- 动量因子计算
- 质量因子计算
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional


class FactorModel:
    """因子模型类"""
    
    def __init__(self):
        self.factors = {}
        
    def calculate_value_factor(self, fund_data: Dict) -> float:
        """
        计算价值因子
        基于基金的基本面数据（如市盈率、市净率等）
        """
        # 简化实现：基于基金规模和成立时间的代理指标
        fund_size = fund_data.get('fund_size', 0)
        establish_date = fund_data.get('establish_date', '2020-01-01')
        
        # 规模越大，价值因子越高（简化逻辑）
        value_score = min(fund_size / 10.0, 1.0)  # 归一化到0-1
        
        return value_score
    
    def calculate_growth_factor(self, nav_history: pd.DataFrame) -> float:
        """
        计算成长因子
        基于历史净值的增长趋势
        """
        if nav_history.empty or len(nav_history) < 2:
            return 0.0
            
        # 计算年化增长率
        start_nav = nav_history['nav'].iloc[0]
        end_nav = nav_history['nav'].iloc[-1]
        days = (pd.to_datetime(nav_history['date'].iloc[-1]) - 
                pd.to_datetime(nav_history['date'].iloc[0])).days
        
        if days <= 0:
            return 0.0
            
        annual_growth = (end_nav / start_nav) ** (365 / days) - 1
        # 归一化到0-1范围
        growth_score = min(max(annual_growth / 0.3, 0.0), 1.0)
        
        return growth_score
    
    def calculate_momentum_factor(self, nav_history: pd.DataFrame, period: int = 90) -> float:
        """
        计算动量因子
        基于近期净值表现
        """
        if nav_history.empty or len(nav_history) < period:
            return 0.0
            
        # 取最近period天的数据
        recent_data = nav_history.tail(period)
        if len(recent_data) < 2:
            return 0.0
            
        start_nav = recent_data['nav'].iloc[0]
        end_nav = recent_data['nav'].iloc[-1]
        momentum_return = (end_nav / start_nav) - 1
        
        # 归一化到0-1范围
        momentum_score = min(max(momentum_return / 0.2, 0.0), 1.0)
        
        return momentum_score
    
    def calculate_quality_factor(self, backtest_results: Dict) -> float:
        """
        计算质量因子
        基于风险调整后的收益指标
        """
        sharpe_ratio = backtest_results.get('sharpe_ratio', 0)
        max_drawdown = backtest_results.get('max_drawdown', 0)
        
        # 夏普率越高越好，最大回撤越小越好
        sharpe_score = min(max(sharpe_ratio / 2.0, 0.0), 1.0)
        drawdown_score = min(max(-max_drawdown, 0.0), 1.0)
        
        quality_score = (sharpe_score + drawdown_score) / 2.0
        return quality_score
    
    def calculate_all_factors(self, fund_code: str, fund_data: Dict, 
                            nav_history: pd.DataFrame, backtest_results: Dict) -> Dict[str, float]:
        """
        计算所有因子
        """
        factors = {
            'value': self.calculate_value_factor(fund_data),
            'growth': self.calculate_growth_factor(nav_history),
            'momentum': self.calculate_momentum_factor(nav_history),
            'quality': self.calculate_quality_factor(backtest_results)
        }
        
        return factors