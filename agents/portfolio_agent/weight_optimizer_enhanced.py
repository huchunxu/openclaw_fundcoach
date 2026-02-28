"""
增强版权重优化模块

功能：
- 增强均值-方差优化（支持约束条件）
- 改进风险平价优化（考虑交易成本）
- 最大夏普率优化（带约束）
- Black-Litterman框架支持
- 多目标优化（收益、风险、分散度）
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from scipy.optimize import minimize


class EnhancedWeightOptimizer:
    """增强版权重优化器"""
    
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
    
    def enhanced_mean_variance_optimization(self, expected_returns: np.ndarray, 
                                         cov_matrix: np.ndarray,
                                         risk_aversion: float = 1.0,
                                         max_weight: float = 0.3,
                                         min_weight: float = 0.05) -> np.ndarray:
        """
        增强均值-方差优化
        
        Args:
            expected_returns: 预期收益率向量
            cov_matrix: 协方差矩阵
            risk_aversion: 风险厌恶系数
            max_weight: 单资产最大权重
            min_weight: 单资产最小权重
            
        Returns:
            最优权重向量
        """
        n_assets = len(expected_returns)
        
        # 目标函数：最小化风险 - 风险厌恶 * 收益
        def objective(weights):
            portfolio_return = np.dot(weights, expected_returns)
            portfolio_risk = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            return portfolio_risk - risk_aversion * portfolio_return
        
        # 约束条件：权重和为1
        constraints = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1}]
        
        # 权重边界约束
        bounds = [(min_weight, max_weight) for _ in range(n_assets)]
        
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
    
    def enhanced_risk_parity_optimization(self, cov_matrix: np.ndarray,
                                        transaction_costs: Optional[np.ndarray] = None) -> np.ndarray:
        """
        增强风险平价优化（考虑交易成本）
        """
        n_assets = cov_matrix.shape[0]
        
        def objective(weights):
            # 计算每个资产的风险贡献
            portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            marginal_contrib = np.dot(cov_matrix, weights) / portfolio_vol
            risk_contrib = weights * marginal_contrib
            
            # 最小化风险贡献的方差
            target = np.mean(risk_contrib)
            risk_parity_loss = np.sum((risk_contrib - target) ** 2)
            
            # 添加交易成本惩罚（如果提供）
            if transaction_costs is not None:
                transaction_cost_penalty = np.dot(transaction_costs, weights)
                return risk_parity_loss + transaction_cost_penalty
            else:
                return risk_parity_loss
        
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
    
    def black_litterman_optimization(self, market_weights: np.ndarray,
                                   cov_matrix: np.ndarray,
                                   views: Optional[Dict] = None,
                                   confidence: float = 0.5) -> np.ndarray:
        """
        Black-Litterman框架优化
        
        Args:
            market_weights: 市场均衡权重
            cov_matrix: 协方差矩阵
            views: 投资观点 {'asset_index': expected_return}
            confidence: 观点置信度
            
        Returns:
            BL优化后的权重
        """
        n_assets = len(market_weights)
        
        # 计算市场隐含收益率
        delta = 2.5  # 风险厌恶系数
        implied_returns = delta * np.dot(cov_matrix, market_weights)
        
        if views is None or len(views) == 0:
            # 无观点时使用市场权重
            return market_weights
            
        # 构建观点矩阵
        P = np.zeros((len(views), n_assets))
        Q = np.zeros(len(views))
        
        for i, (asset_idx, view_return) in enumerate(views.items()):
            P[i, asset_idx] = 1
            Q[i] = view_return
            
        # 计算观点不确定性矩阵
        omega = np.diag(np.diag(np.dot(np.dot(P, cov_matrix), P.T))) * (1 - confidence) / confidence
        
        # Black-Litterman公式
        try:
            pi_bl = implied_returns + np.dot(
                np.dot(np.dot(cov_matrix, P.T),
                      np.linalg.inv(np.dot(np.dot(P, cov_matrix), P.T) + omega)),
                (Q - np.dot(P, implied_returns))
            )
            
            # 使用BL收益率进行均值-方差优化
            optimized_weights = self.enhanced_mean_variance_optimization(
                pi_bl, cov_matrix, risk_aversion=delta
            )
            return optimized_weights
            
        except:
            # 如果BL失败，回退到市场权重
            return market_weights
    
    def multi_objective_optimization(self, expected_returns: np.ndarray,
                                  cov_matrix: np.ndarray,
                                  weights: Optional[np.ndarray] = None) -> np.ndarray:
        """
        多目标优化（收益、风险、分散度）
        """
        n_assets = len(expected_returns)
        
        def objective(weights):
            # 收益目标（最大化）
            portfolio_return = np.dot(weights, expected_returns)
            
            # 风险目标（最小化）
            portfolio_risk = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            
            # 分散度目标（最大化熵）
            entropy = -np.sum(weights * np.log(weights + 1e-8))
            
            # 综合目标函数
            # 收益权重: 0.4, 风险权重: 0.4, 分散度权重: 0.2
            combined_score = -(
                0.4 * portfolio_return - 
                0.4 * portfolio_risk + 
                0.2 * entropy
            )
            
            return combined_score
        
        constraints = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1}]
        bounds = [(0, 1) for _ in range(n_assets)]
        
        if weights is None:
            initial_weights = np.ones(n_assets) / n_assets
        else:
            initial_weights = weights
            
        try:
            result = minimize(objective, initial_weights,
                            method='SLSQP', bounds=bounds, constraints=constraints)
            if result.success:
                return result.x
            else:
                return initial_weights
        except:
            return initial_weights
    
    def optimize_portfolio_weights_enhanced(self, fund_scores: pd.DataFrame,
                                         fund_nav_dict: Dict[str, pd.DataFrame],
                                         optimization_method: str = 'enhanced_risk_parity',
                                         **kwargs) -> Dict[str, float]:
        """
        增强投资组合权重优化
        
        Args:
            fund_scores: 基金打分结果
            fund_nav_dict: 基金净值数据
            optimization_method: 优化方法
            **kwargs: 额外参数
            
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
            
        # 计算预期收益率
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
        if optimization_method == 'enhanced_mean_variance':
            weights = self.enhanced_mean_variance_optimization(
                expected_returns, cov_matrix, **kwargs
            )
        elif optimization_method == 'black_litterman':
            market_weights = np.ones(len(valid_fund_codes)) / len(valid_fund_codes)
            weights = self.black_litterman_optimization(
                market_weights, cov_matrix, **kwargs
            )
        elif optimization_method == 'multi_objective':
            weights = self.multi_objective_optimization(
                expected_returns, cov_matrix, **kwargs
            )
        else:  # enhanced_risk_parity
            weights = self.enhanced_risk_parity_optimization(
                cov_matrix, **kwargs
            )
            
        # 构建结果字典
        portfolio_weights = dict(zip(valid_fund_codes, weights))
        return portfolio_weights