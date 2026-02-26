"""
权重优化模块

功能：
- 均值-方差优化
- 风险平价优化  
- 最大夏普率优化
- 风险预算优化
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from scipy.optimize import minimize


class WeightOptimizer:
    """权重优化器"""
    
    def __init__(self):
        pass
        
    def _calculate_covariance_matrix(self, fund_nav_dict: Dict[str, pd.DataFrame]) -> np.ndarray:
        """
        计算基金净值的协方差矩阵
        """
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
            return np.eye(len(fund_nav_dict))
            
        all_dates = sorted(list(all_dates))
        
        # 构建收益率矩阵
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
                    
            # 转换为收益率
            fund_returns = pd.Series(fund_returns).pct_change().dropna().values
            returns_matrix.append(fund_returns)
            
        if len(returns_matrix) == 0:
            return np.eye(len(fund_codes))
            
        # 计算协方差矩阵
        try:
            returns_array = np.array(returns_matrix)
            cov_matrix = np.cov(returns_array)
            return cov_matrix
        except:
            return np.eye(len(fund_codes))
    
    def mean_variance_optimization(self, expected_returns: np.ndarray, 
                                 cov_matrix: np.ndarray,
                                 risk_aversion: float = 1.0) -> np.ndarray:
        """
        均值-方差优化
        
        Args:
            expected_returns: 预期收益率向量
            cov_matrix: 协方差矩阵
            risk_aversion: 风险厌恶系数
            
        Returns:
            最优权重向量
        """
        n_assets = len(expected_returns)
        
        # 目标函数：最小化风险 - 风险厌恶 * 收益
        def objective(weights):
            portfolio_return = np.dot(weights, expected_returns)
            portfolio_risk = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            return portfolio_risk - risk_aversion * portfolio_return
        
        # 约束条件：权重和为1，权重非负
        constraints = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1}]
        bounds = [(0, 1) for _ in range(n_assets)]
        
        # 初始权重（等权重）
        initial_weights = np.ones(n_assets) / n_assets
        
        try:
            result = minimize(objective, initial_weights, 
                            method='SLSQP', bounds=bounds, constraints=constraints)
            if result.success:
                return result.x
            else:
                return initial_weights
        except:
            return initial_weights
    
    def risk_parity_optimization(self, cov_matrix: np.ndarray) -> np.ndarray:
        """
        风险平价优化
        """
        n_assets = cov_matrix.shape[0]
        
        def objective(weights):
            # 计算每个资产的风险贡献
            portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            marginal_contrib = np.dot(cov_matrix, weights) / portfolio_vol
            risk_contrib = weights * marginal_contrib
            
            # 最小化风险贡献的方差
            target = np.mean(risk_contrib)
            return np.sum((risk_contrib - target) ** 2)
        
        constraints = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1}]
        bounds = [(0, 1) for _ in range(n_assets)]
        initial_weights = np.ones(n_assets) / n_assets
        
        try:
            result = minimize(objective, initial_weights,
                            method='SLSQP', bounds=bounds, constraints=constraints)
            if result.success:
                return result.x
            else:
                return initial_weights
        except:
            return initial_weights
    
    def max_sharpe_ratio_optimization(self, expected_returns: np.ndarray,
                                    cov_matrix: np.ndarray,
                                    risk_free_rate: float = 0.02) -> np.ndarray:
        """
        最大夏普率优化
        """
        n_assets = len(expected_returns)
        
        def objective(weights):
            portfolio_return = np.dot(weights, expected_returns)
            portfolio_risk = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_risk
            return -sharpe_ratio  # 最小化负夏普率
        
        constraints = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1}]
        bounds = [(0, 1) for _ in range(n_assets)]
        initial_weights = np.ones(n_assets) / n_assets
        
        try:
            result = minimize(objective, initial_weights,
                            method='SLSQP', bounds=bounds, constraints=constraints)
            if result.success:
                return result.x
            else:
                return initial_weights
        except:
            return initial_weights
    
    def optimize_portfolio_weights(self, fund_scores: pd.DataFrame,
                                 fund_nav_dict: Dict[str, pd.DataFrame],
                                 optimization_method: str = 'risk_parity') -> Dict[str, float]:
        """
        优化投资组合权重
        
        Args:
            fund_scores: 基金打分结果
            fund_nav_dict: 基金净值数据
            optimization_method: 优化方法 ('mean_variance', 'risk_parity', 'max_sharpe')
            
        Returns:
            优化后的权重字典 {fund_code: weight}
        """
        if fund_scores.empty:
            return {}
            
        fund_codes = fund_scores['fund_code'].tolist()
        
        # 过滤有净值数据的基金
        valid_fund_codes = []
        valid_nav_dict = {}
        for code in fund_codes:
            if code in fund_nav_dict and not fund_nav_dict[code].empty:
                valid_fund_codes.append(code)
                valid_nav_dict[code] = fund_nav_dict[code]
                
        if len(valid_fund_codes) == 0:
            return {}
            
        # 计算预期收益率（使用历史年化收益作为代理）
        expected_returns = []
        for code in valid_fund_codes:
            nav_data = valid_nav_dict[code]
            if len(nav_data) >= 2:
                total_return = (nav_data['nav'].iloc[-1] / nav_data['nav'].iloc[0]) - 1
                days = (pd.to_datetime(nav_data['date'].iloc[-1]) - 
                       pd.to_datetime(nav_data['date'].iloc[0])).days
                annual_return = (1 + total_return) ** (365 / days) - 1 if days > 0 else 0
                expected_returns.append(annual_return)
            else:
                expected_returns.append(0.0)
                
        expected_returns = np.array(expected_returns)
        cov_matrix = self._calculate_covariance_matrix(valid_nav_dict)
        
        # 执行优化
        if optimization_method == 'mean_variance':
            weights = self.mean_variance_optimization(expected_returns, cov_matrix)
        elif optimization_method == 'max_sharpe':
            weights = self.max_sharpe_ratio_optimization(expected_returns, cov_matrix)
        else:  # risk_parity
            weights = self.risk_parity_optimization(cov_matrix)
            
        # 构建结果字典
        portfolio_weights = dict(zip(valid_fund_codes, weights))
        return portfolio_weights