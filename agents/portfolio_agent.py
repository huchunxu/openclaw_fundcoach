#!/usr/bin/env python3
"""
Portfolio Agent - 组合生成和权重优化
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
import logging

class PortfolioAgent:
    """组合智能体：负责组合生成、权重优化和风险平衡"""
    
    def __init__(self):
        self.risk_tolerance = 0.5  # 默认风险容忍度
        self.logger = logging.getLogger(__name__)
    
    def generate_top_n_portfolio(self, fund_scores: Dict[str, float], n: int = 5) -> Dict[str, float]:
        """生成Top-N基金组合"""
        # 按得分排序
        sorted_funds = sorted(fund_scores.items(), key=lambda x: x[1], reverse=True)
        top_funds = sorted_funds[:n]
        
        # 等权重分配
        weights = {}
        for fund_code, score in top_funds:
            weights[fund_code] = 1.0 / len(top_funds)
        
        return weights
    
    def optimize_weights(self, fund_returns: Dict[str, List[float]], 
                        risk_tolerance: float = None) -> Dict[str, float]:
        """基于风险容忍度优化权重"""
        if risk_tolerance is None:
            risk_tolerance = self.risk_tolerance
        
        # 转换为numpy数组
        fund_codes = list(fund_returns.keys())
        returns_matrix = np.array([fund_returns[code] for code in fund_codes]).T
        
        # 计算协方差矩阵
        cov_matrix = np.cov(returns_matrix.T)
        
        # 简化的均值-方差优化（实际应用中需要更复杂的优化算法）
        n_assets = len(fund_codes)
        
        # 如果风险容忍度高，偏向高收益；如果低，偏向低风险
        if risk_tolerance > 0.7:
            # 高风险偏好：等权重
            weights = np.ones(n_assets) / n_assets
        elif risk_tolerance < 0.3:
            # 低风险偏好：最小方差组合
            try:
                inv_cov = np.linalg.inv(cov_matrix)
                ones = np.ones(n_assets)
                weights = inv_cov @ ones
                weights = weights / np.sum(weights)
            except np.linalg.LinAlgError:
                # 如果协方差矩阵不可逆，使用等权重
                weights = np.ones(n_assets) / n_assets
        else:
            # 中等风险：混合策略
            equal_weight = np.ones(n_assets) / n_assets
            try:
                inv_cov = np.linalg.inv(cov_matrix)
                ones = np.ones(n_assets)
                min_var_weight = inv_cov @ ones
                min_var_weight = min_var_weight / np.sum(min_var_weight)
                weights = 0.5 * equal_weight + 0.5 * min_var_weight
            except np.linalg.LinAlgError:
                weights = equal_weight
        
        # 确保权重非负
        weights = np.maximum(weights, 0)
        weights = weights / np.sum(weights)
        
        return {fund_codes[i]: weights[i] for i in range(n_assets)}
    
    def balance_risk(self, portfolio_weights: Dict[str, float], 
                    fund_styles: Dict[str, str]) -> Dict[str, float]:
        """风险平衡：确保风格分散"""
        # 按风格分组
        style_groups = {}
        for fund_code, style in fund_styles.items():
            if fund_code in portfolio_weights:
                if style not in style_groups:
                    style_groups[style] = []
                style_groups[style].append(fund_code)
        
        # 如果某个风格过于集中，进行调整
        balanced_weights = portfolio_weights.copy()
        total_weight = sum(portfolio_weights.values())
        
        for style, funds in style_groups.items():
            style_weight = sum(portfolio_weights.get(fund, 0) for fund in funds)
            if style_weight / total_weight > 0.6:  # 风格集中度超过60%
                # 重新分配权重，降低该风格的权重
                reduction_factor = 0.8
                for fund in funds:
                    balanced_weights[fund] *= reduction_factor
        
        # 重新标准化权重
        total_balanced = sum(balanced_weights.values())
        if total_balanced > 0:
            balanced_weights = {k: v/total_balanced for k, v in balanced_weights.items()}
        
        return balanced_weights
    
    def create_diversified_portfolio(self, fund_pool: Dict, strategy_results: Dict,
                                   risk_tolerance: float = None) -> Dict[str, float]:
        """创建多元化投资组合"""
        # 获取基金得分
        fund_scores = {code: result['score'] for code, result in strategy_results.items()}
        
        # 生成初始组合
        initial_weights = self.generate_top_n_portfolio(fund_scores, n=5)
        
        # 获取基金收益数据用于优化
        fund_returns = {}
        for code in initial_weights.keys():
            if code in fund_pool:
                fund_returns[code] = fund_pool[code]['returns']
        
        if len(fund_returns) > 1:
            # 优化权重
            optimized_weights = self.optimize_weights(fund_returns, risk_tolerance)
            
            # 风险平衡
            fund_styles = {code: result['style'] for code, result in strategy_results.items()}
            final_weights = self.balance_risk(optimized_weights, fund_styles)
        else:
            final_weights = initial_weights
        
        return final_weights