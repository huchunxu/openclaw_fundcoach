#!/usr/bin/env python3
"""
Strategy Agent - 因子建模和基金打分系统
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
import logging

class StrategyAgent:
    """策略智能体：负责因子建模、基金打分和风格分类"""
    
    def __init__(self):
        self.factors = {
            'return_1y': 0.25,      # 一年收益
            'sharpe_ratio': 0.25,   # 夏普率
            'max_drawdown': 0.20,   # 最大回撤（负向）
            'volatility': 0.15,     # 波动率（负向）
            'consistency': 0.15     # 收益一致性
        }
        self.logger = logging.getLogger(__name__)
    
    def calculate_factors(self, fund_data: Dict) -> Dict[str, float]:
        """计算基金的各项因子值"""
        returns = np.array(fund_data['returns'])
        
        # 一年收益
        return_1y = returns[-252:].mean() * 252 if len(returns) >= 252 else returns.mean() * 252
        
        # 夏普率
        sharpe_ratio = return_1y / (returns.std() * np.sqrt(252)) if returns.std() > 0 else 0
        
        # 最大回撤
        cumulative = np.cumprod(1 + returns)
        running_max = np.maximum.accumulate(cumulative)
        drawdowns = (cumulative - running_max) / running_max
        max_drawdown = drawdowns.min()
        
        # 波动率
        volatility = returns.std() * np.sqrt(252)
        
        # 收益一致性（正收益月份比例）
        consistency = np.mean(returns > 0)
        
        return {
            'return_1y': return_1y,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'volatility': volatility,
            'consistency': consistency
        }
    
    def score_fund(self, factors: Dict[str, float]) -> float:
        """基于因子计算基金综合得分"""
        # 标准化因子（假设已有标准化逻辑）
        normalized_factors = self._normalize_factors(factors)
        
        # 计算加权得分
        score = 0.0
        for factor, weight in self.factors.items():
            if factor in ['max_drawdown', 'volatility']:
                # 负向因子：值越小越好
                score += weight * (1 - normalized_factors[factor])
            else:
                # 正向因子：值越大越好
                score += weight * normalized_factors[factor]
        
        return score
    
    def _normalize_factors(self, factors: Dict[str, float]) -> Dict[str, float]:
        """标准化因子值到0-1范围"""
        # 简化标准化，实际应用中需要更复杂的归一化方法
        normalized = {}
        for factor, value in factors.items():
            if factor == 'max_drawdown':
                # 回撤范围假设为-0.5到0
                normalized[factor] = min(1.0, max(0.0, (value + 0.5) / 0.5))
            elif factor == 'volatility':
                # 波动率范围假设为0到0.5
                normalized[factor] = min(1.0, max(0.0, value / 0.5))
            elif factor == 'sharpe_ratio':
                # 夏普率范围假设为-1到3
                normalized[factor] = min(1.0, max(0.0, (value + 1) / 4))
            else:
                # 其他因子简单处理
                normalized[factor] = min(1.0, max(0.0, value))
        
        return normalized
    
    def classify_style(self, fund_data: Dict) -> str:
        """基金风格分类"""
        # 基于收益特征进行简单分类
        returns = np.array(fund_data['returns'])
        annual_return = returns.mean() * 252
        volatility = returns.std() * np.sqrt(252)
        
        if annual_return > 0.15 and volatility > 0.25:
            return "aggressive_growth"
        elif annual_return > 0.08 and volatility <= 0.25:
            return "balanced"
        elif annual_return <= 0.08 and volatility <= 0.15:
            return "conservative"
        else:
            return "mixed"
    
    def analyze_fund_pool(self, fund_pool: Dict) -> Dict:
        """分析整个基金池"""
        results = {}
        for fund_code, fund_data in fund_pool.items():
            factors = self.calculate_factors(fund_data)
            score = self.score_fund(factors)
            style = self.classify_style(fund_data)
            
            results[fund_code] = {
                'factors': factors,
                'score': score,
                'style': style
            }
        
        return results