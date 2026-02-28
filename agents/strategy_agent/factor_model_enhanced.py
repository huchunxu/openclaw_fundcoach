"""
增强版因子建模模块

功能：
- 价值因子计算（基于基金规模、费率等）
- 成长因子计算（基于历史净值增长趋势）
- 动量因子计算（基于不同时间周期的表现）
- 质量因子计算（基于风险调整收益）
- 波动率因子计算（基于历史波动性）
- 最大回撤因子计算
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta


class EnhancedFactorModel:
    """增强版因子模型类"""
    
    def __init__(self):
        self.factors = {}
        
    def calculate_value_factor(self, fund_data: Dict) -> float:
        """
        计算价值因子
        基于基金规模、费率、成立时间等基本面指标
        """
        fund_size = fund_data.get('fund_size', 0)
        establish_date = fund_data.get('establish_date', '2020-01-01')
        
        # 规模因子：适度规模的基金可能更稳定（50-200亿为最佳）
        if 50 <= fund_size <= 200:
            size_score = 1.0
        elif fund_size < 10 or fund_size > 500:
            size_score = 0.3
        else:
            size_score = 0.7
            
        # 成立时间因子：成熟基金（3年以上）更有经验
        try:
            est_date = pd.to_datetime(establish_date)
            years_since_establish = (datetime.now() - est_date).days / 365.25
            if years_since_establish >= 3:
                age_score = 1.0
            elif years_since_establish >= 1:
                age_score = 0.7
            else:
                age_score = 0.4
        except:
            age_score = 0.5
            
        value_score = (size_score + age_score) / 2.0
        return value_score
    
    def calculate_growth_factor(self, nav_history: pd.DataFrame) -> float:
        """
        计算成长因子
        基于多时间周期的历史净值增长趋势
        """
        if nav_history.empty or len(nav_history) < 30:
            return 0.0
            
        nav_series = nav_history.set_index('date')['nav'].sort_index()
        
        # 计算不同时间周期的增长率
        periods = {
            '1m': 30,
            '3m': 90, 
            '6m': 180,
            '1y': 365
        }
        
        growth_scores = []
        for period_name, days in periods.items():
            if len(nav_series) >= days:
                start_idx = -days
                end_idx = -1
                if start_idx >= -len(nav_series):
                    start_nav = nav_series.iloc[start_idx]
                    end_nav = nav_series.iloc[end_idx]
                    if start_nav > 0:
                        period_return = (end_nav / start_nav) - 1
                        annualized_return = (1 + period_return) ** (365 / days) - 1
                        # 归一化到0-1范围（假设30%年化为优秀）
                        score = min(max(annualized_return / 0.3, 0.0), 1.0)
                        growth_scores.append(score)
        
        if not growth_scores:
            return 0.0
            
        # 加权平均，近期表现权重更高
        weights = [0.4, 0.3, 0.2, 0.1]  # 1m, 3m, 6m, 1y
        weighted_score = 0.0
        total_weight = 0.0
        
        for i, score in enumerate(growth_scores):
            if i < len(weights):
                weighted_score += weights[i] * score
                total_weight += weights[i]
        
        if total_weight > 0:
            return weighted_score / total_weight
        else:
            return np.mean(growth_scores)
    
    def calculate_momentum_factor(self, nav_history: pd.DataFrame) -> float:
        """
        计算动量因子
        基于短期和中期动量，考虑动量持续性
        """
        if nav_history.empty or len(nav_history) < 60:
            return 0.0
            
        nav_series = nav_history.set_index('date')['nav'].sort_index()
        
        # 短期动量（20天）
        if len(nav_series) >= 20:
            short_term_return = (nav_series.iloc[-1] / nav_series.iloc[-20]) - 1
        else:
            short_term_return = 0.0
            
        # 中期动量（60天）
        if len(nav_series) >= 60:
            medium_term_return = (nav_series.iloc[-1] / nav_series.iloc[-60]) - 1
        else:
            medium_term_return = 0.0
            
        # 动量一致性：短期和中期动量方向一致时得分更高
        if short_term_return > 0 and medium_term_return > 0:
            consistency_bonus = 0.2
        elif short_term_return < 0 and medium_term_return < 0:
            consistency_bonus = -0.2
        else:
            consistency_bonus = 0.0
            
        # 主要基于中期动量（更稳定）
        momentum_score = min(max(medium_term_return / 0.2, 0.0), 1.0)
        final_score = min(max(momentum_score + consistency_bonus, 0.0), 1.0)
        
        return final_score
    
    def calculate_quality_factor(self, backtest_results: Dict) -> float:
        """
        计算质量因子
        基于夏普率、信息比率、最大回撤等风险调整指标
        """
        sharpe_ratio = backtest_results.get('sharpe_ratio', 0)
        max_drawdown = backtest_results.get('max_drawdown', 0)
        volatility = backtest_results.get('volatility', 1)
        
        # 夏普率标准化（优秀>1.5，良好>1.0）
        if sharpe_ratio >= 1.5:
            sharpe_score = 1.0
        elif sharpe_ratio >= 1.0:
            sharpe_score = 0.8
        elif sharpe_ratio >= 0.5:
            sharpe_score = 0.6
        elif sharpe_ratio >= 0:
            sharpe_score = 0.4
        else:
            sharpe_score = 0.2
            
        # 最大回撤标准化（越小越好）
        abs_max_dd = abs(max_drawdown)
        if abs_max_dd <= 0.15:
            drawdown_score = 1.0
        elif abs_max_dd <= 0.25:
            drawdown_score = 0.8
        elif abs_max_dd <= 0.35:
            drawdown_score = 0.6
        elif abs_max_dd <= 0.5:
            drawdown_score = 0.4
        else:
            drawdown_score = 0.2
            
        # 波动率标准化（适中波动率最佳）
        if 0.1 <= volatility <= 0.25:
            vol_score = 1.0
        elif volatility < 0.1 or volatility > 0.4:
            vol_score = 0.4
        else:
            vol_score = 0.7
            
        quality_score = (sharpe_score + drawdown_score + vol_score) / 3.0
        return quality_score
    
    def calculate_volatility_factor(self, nav_history: pd.DataFrame) -> float:
        """
        计算波动率因子
        基于历史净值的波动性（低波动通常更受青睐）
        """
        if nav_history.empty or len(nav_history) < 30:
            return 0.5  # 默认中等波动
            
        nav_series = nav_history.set_index('date')['nav'].sort_index()
        returns = nav_series.pct_change().dropna()
        
        if len(returns) < 10:
            return 0.5
            
        annualized_vol = returns.std() * np.sqrt(252)
        
        # 低波动性得分更高（反向因子）
        if annualized_vol <= 0.1:
            vol_factor = 1.0
        elif annualized_vol <= 0.2:
            vol_factor = 0.8
        elif annualized_vol <= 0.3:
            vol_factor = 0.6
        elif annualized_vol <= 0.4:
            vol_factor = 0.4
        else:
            vol_factor = 0.2
            
        return vol_factor
    
    def calculate_consistency_factor(self, nav_history: pd.DataFrame) -> float:
        """
        计算一致性因子
        基于月度收益的一致性（胜率、连续盈利能力）
        """
        if nav_history.empty or len(nav_history) < 60:
            return 0.5
            
        nav_series = nav_history.set_index('date')['nav'].sort_index()
        monthly_returns = nav_series.resample('M').last().pct_change().dropna()
        
        if len(monthly_returns) < 6:
            return 0.5
            
        # 胜率（正收益月份比例）
        win_rate = (monthly_returns > 0).mean()
        
        # 连续盈利能力（最长连续正收益月数）
        positive_streaks = []
        current_streak = 0
        for ret in monthly_returns:
            if ret > 0:
                current_streak += 1
            else:
                if current_streak > 0:
                    positive_streaks.append(current_streak)
                    current_streak = 0
        if current_streak > 0:
            positive_streaks.append(current_streak)
            
        max_streak = max(positive_streaks) if positive_streaks else 0
        
        # 胜率得分
        if win_rate >= 0.7:
            win_score = 1.0
        elif win_rate >= 0.6:
            win_score = 0.8
        elif win_rate >= 0.5:
            win_score = 0.6
        else:
            win_score = 0.4
            
        # 连续性得分
        if max_streak >= 6:
            streak_score = 1.0
        elif max_streak >= 4:
            streak_score = 0.8
        elif max_streak >= 2:
            streak_score = 0.6
        else:
            streak_score = 0.4
            
        consistency_score = (win_score + streak_score) / 2.0
        return consistency_score
    
    def calculate_all_factors(self, fund_code: str, fund_data: Dict, 
                            nav_history: pd.DataFrame, backtest_results: Dict) -> Dict[str, float]:
        """
        计算所有增强因子
        """
        factors = {
            'value': self.calculate_value_factor(fund_data),
            'growth': self.calculate_growth_factor(nav_history),
            'momentum': self.calculate_momentum_factor(nav_history),
            'quality': self.calculate_quality_factor(backtest_results),
            'volatility': self.calculate_volatility_factor(nav_history),
            'consistency': self.calculate_consistency_factor(nav_history)
        }
        
        return factors