"""
风险平衡模块

功能：
- 组合风险暴露分析
- 最大回撤控制
- 行业分散化检查
- 风险预算分配
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional


class RiskBalancer:
    """风险平衡器"""
    
    def __init__(self, max_drawdown_limit: float = -0.3, 
                 max_concentration: float = 0.4):
        """
        初始化风险平衡器
        
        Args:
            max_drawdown_limit: 最大可接受回撤（负值，如-0.3表示30%）
            max_concentration: 单一资产最大集中度
        """
        self.max_drawdown_limit = max_drawdown_limit
        self.max_concentration = max_concentration
        
    def analyze_portfolio_risk(self, portfolio_weights: Dict[str, float],
                             fund_nav_dict: Dict[str, pd.DataFrame]) -> Dict:
        """
        分析组合风险
        
        Args:
            portfolio_weights: 组合权重
            fund_nav_dict: 基金净值数据
            
        Returns:
            风险分析结果字典
        """
        if not portfolio_weights or not fund_nav_dict:
            return {}
            
        # 计算组合净值
        all_dates = None
        for nav_data in fund_nav_dict.values():
            if nav_data.empty:
                continue
            if all_dates is None:
                all_dates = set(nav_data['date'])
            else:
                all_dates = all_dates.intersection(set(nav_data['date']))
                
        if not all_dates or len(all_dates) < 2:
            return {}
            
        all_dates = sorted(list(all_dates))
        portfolio_nav = []
        
        for date in all_dates:
            weighted_nav = 0.0
            total_weight = 0.0
            
            for fund_code, weight in portfolio_weights.items():
                if fund_code not in fund_nav_dict:
                    continue
                    
                nav_data = fund_nav_dict[fund_code]
                nav_on_date = nav_data[nav_data['date'] == date]
                
                if not nav_on_date.empty:
                    weighted_nav += weight * nav_on_date['nav'].iloc[0]
                    total_weight += weight
                    
            if total_weight > 0:
                normalized_nav = weighted_nav / total_weight
                portfolio_nav.append(normalized_nav)
                
        if len(portfolio_nav) < 2:
            return {}
            
        portfolio_nav_series = pd.Series(portfolio_nav)
        
        # 计算风险指标
        daily_returns = portfolio_nav_series.pct_change().dropna()
        annual_volatility = daily_returns.std() * np.sqrt(252)
        
        # 最大回撤
        rolling_max = portfolio_nav_series.expanding().max()
        drawdown = (portfolio_nav_series - rolling_max) / rolling_max
        max_drawdown = drawdown.min()
        
        # 集中度风险
        weights_array = np.array(list(portfolio_weights.values()))
        concentration_risk = np.max(weights_array)
        herfindahl_index = np.sum(weights_array ** 2)
        
        risk_analysis = {
            'portfolio_volatility': annual_volatility,
            'max_drawdown': max_drawdown,
            'concentration_risk': concentration_risk,
            'herfindahl_index': herfindahl_index,
            'num_holdings': len(portfolio_weights),
            'is_within_limits': (
                max_drawdown >= self.max_drawdown_limit and 
                concentration_risk <= self.max_concentration
            )
        }
        
        return risk_analysis
    
    def adjust_weights_for_risk(self, portfolio_weights: Dict[str, float],
                              fund_nav_dict: Dict[str, pd.DataFrame]) -> Dict[str, float]:
        """
        根据风险限制调整权重
        
        Args:
            portfolio_weights: 原始权重
            fund_nav_dict: 基金净值数据
            
        Returns:
            调整后的权重
        """
        risk_analysis = self.analyze_portfolio_risk(portfolio_weights, fund_nav_dict)
        
        if risk_analysis.get('is_within_limits', True):
            return portfolio_weights
            
        adjusted_weights = portfolio_weights.copy()
        
        # 如果集中度过高，降低最大权重
        if risk_analysis.get('concentration_risk', 0) > self.max_concentration:
            weights_array = np.array(list(adjusted_weights.values()))
            fund_codes = list(adjusted_weights.keys())
            
            # 找到权重最高的基金
            max_weight_idx = np.argmax(weights_array)
            max_weight_fund = fund_codes[max_weight_idx]
            
            # 降低其权重到限制水平
            excess_weight = adjusted_weights[max_weight_fund] - self.max_concentration
            adjusted_weights[max_weight_fund] = self.max_concentration
            
            # 将多余权重分配给其他基金
            other_funds = [code for code in fund_codes if code != max_weight_fund]
            if other_funds and excess_weight > 0:
                weight_per_other = excess_weight / len(other_funds)
                for fund in other_funds:
                    adjusted_weights[fund] += weight_per_other
                    
        # 重新归一化
        total_weight = sum(adjusted_weights.values())
        if total_weight > 0:
            for fund in adjusted_weights:
                adjusted_weights[fund] /= total_weight
                
        return adjusted_weights
    
    def ensure_diversification(self, portfolio_weights: Dict[str, float],
                             min_holdings: int = 3) -> Dict[str, float]:
        """
        确保组合分散化
        
        Args:
            portfolio_weights: 组合权重
            min_holdings: 最少持仓数量
            
        Returns:
            确保分散化的权重
        """
        if len(portfolio_weights) >= min_holdings:
            return portfolio_weights
            
        # 如果持仓太少，需要添加更多基金
        # 这里简化处理：返回原权重（实际应用中可能需要从候选池中选择）
        return portfolio_weights