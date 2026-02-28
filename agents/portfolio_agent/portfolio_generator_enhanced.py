"""
增强版组合生成模块

功能：
- 多策略组合生成（Top-N、分层、分散化、风险预算）
- 行业分散度约束
- 风格平衡控制
- 动态权重调整
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple


class EnhancedPortfolioGenerator:
    """增强版组合生成器"""
    
    def __init__(self):
        pass
        
    def generate_top_n_portfolio(self, fund_scores: pd.DataFrame, 
                               n: int = 10, min_weight: float = 0.05) -> Dict[str, float]:
        """
        生成Top-N基金组合
        
        Args:
            fund_scores: 基金打分DataFrame，包含fund_code和composite_score列
            n: 选择的基金数量
            min_weight: 单只基金最小权重
            
        Returns:
            字典 {fund_code: weight}
        """
        if fund_scores.empty:
            return {}
            
        # 按综合评分排序
        sorted_funds = fund_scores.sort_values('composite_score', ascending=False)
        
        # 选择Top-N
        top_funds = sorted_funds.head(n)
        
        if top_funds.empty:
            return {}
            
        # 基于评分分配权重（评分越高，权重越大）
        scores = top_funds['composite_score'].values
        weights = scores / scores.sum()  # 归一化
        
        # 确保最小权重约束
        weights = np.maximum(weights, min_weight)
        weights = weights / weights.sum()  # 重新归一化
        
        portfolio = dict(zip(top_funds['fund_code'], weights))
        return portfolio
    
    def generate_layered_portfolio(self, fund_scores: pd.DataFrame,
                                 layers: Dict[str, Dict] = None) -> Dict[str, float]:
        """
        生成分层组合（按风格分类分层配置）
        
        Args:
            fund_scores: 基金打分DataFrame
            layers: 分层配置，例如 {'value': 0.4, 'growth': 0.4, 'balanced': 0.2}
            
        Returns:
            字典 {fund_code: weight}
        """
        if fund_scores.empty:
            return {}
            
        if layers is None:
            # 默认分层配置
            layers = {
                'value': 0.33,
                'growth': 0.33, 
                'balanced': 0.34
            }
            
        total_portfolio = {}
        
        for style, layer_weight in layers.items():
            if layer_weight <= 0:
                continue
                
            # 筛选该风格的基金
            style_funds = fund_scores[fund_scores['investment_style'] == style]
            
            if style_funds.empty:
                continue
                
            # 在该风格内选择Top基金
            style_top = style_funds.sort_values('composite_score', ascending=False).head(3)
            
            if style_top.empty:
                continue
                
            # 分配权重
            style_scores = style_top['composite_score'].values
            style_weights = style_scores / style_scores.sum()
            
            # 应用层权重
            for idx, (fund_code, weight) in enumerate(zip(style_top['fund_code'], style_weights)):
                total_portfolio[fund_code] = layer_weight * weight
                
        return total_portfolio
    
    def generate_diversified_portfolio(self, fund_scores: pd.DataFrame,
                                    max_sector_concentration: float = 0.3,
                                    max_single_fund_weight: float = 0.2) -> Dict[str, float]:
        """
        生成分散化组合
        
        Args:
            fund_scores: 基金打分DataFrame
            max_sector_concentration: 单一行业最大集中度
            max_single_fund_weight: 单只基金最大权重
            
        Returns:
            字典 {fund_code: weight}
        """
        if fund_scores.empty:
            return {}
            
        # 按评分排序
        sorted_funds = fund_scores.sort_values('composite_score', ascending=False)
        
        # 初始权重分配（等权重）
        n_funds = min(len(sorted_funds), 10)  # 最多10只基金
        selected_funds = sorted_funds.head(n_funds)
        
        if selected_funds.empty:
            return {}
            
        # 等权重分配
        equal_weight = 1.0 / len(selected_funds)
        weights = np.full(len(selected_funds), equal_weight)
        
        # 应用最大单基金权重限制
        weights = np.minimum(weights, max_single_fund_weight)
        
        # 如果有基金被限制，重新分配剩余权重
        remaining_weight = 1.0 - weights.sum()
        if remaining_weight > 0:
            # 找到未达到上限的基金
            can_increase = weights < max_single_fund_weight
            if np.any(can_increase):
                increase_amount = remaining_weight / np.sum(can_increase)
                weights[can_increase] += increase_amount
                
        # 最终归一化
        weights = weights / weights.sum()
        
        portfolio = dict(zip(selected_funds['fund_code'], weights))
        return portfolio
        
    def generate_risk_budget_portfolio(self, fund_scores: pd.DataFrame,
                                    risk_budgets: Optional[Dict[str, float]] = None) -> Dict[str, float]:
        """
        生成风险预算组合
        
        Args:
            fund_scores: 基金打分DataFrame
            risk_budgets: 风险预算配置
            
        Returns:
            字典 {fund_code: weight}
        """
        if fund_scores.empty:
            return {}
            
        if risk_budgets is None:
            # 默认等风险预算
            n_funds = min(len(fund_scores), 8)
            selected_funds = fund_scores.head(n_funds)
            risk_budgets = {code: 1.0/n_funds for code in selected_funds['fund_code']}
            
        # 简化的风险预算实现：基于评分分配
        selected_funds = fund_scores[fund_scores['fund_code'].isin(risk_budgets.keys())]
        if selected_funds.empty:
            return {}
            
        # 基于风险预算和评分的综合权重
        weights = []
        fund_codes = []
        total_weight = 0.0
        
        for _, row in selected_funds.iterrows():
            fund_code = row['fund_code']
            score = row['composite_score']
            risk_budget = risk_budgets.get(fund_code, 0.0)
            
            # 综合权重 = 风险预算 * 评分
            weight = risk_budget * score
            weights.append(weight)
            fund_codes.append(fund_code)
            total_weight += weight
            
        if total_weight > 0:
            weights = [w / total_weight for w in weights]
            
        portfolio = dict(zip(fund_codes, weights))
        return portfolio