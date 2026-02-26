"""
回撤控制检测模块

功能：
- 实时回撤监控
- 动态止损机制
- 回撤预警系统
- 风险预算分配
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple


class DrawdownController:
    """回撤控制器"""
    
    def __init__(self, max_drawdown_limit: float = -0.2,
                 warning_threshold: float = -0.15,
                 recovery_threshold: float = 0.05):
        """
        初始化回撤控制器
        
        Args:
            max_drawdown_limit: 最大可接受回撤（负值，如-0.2表示20%）
            warning_threshold: 预警阈值（如-0.15表示15%）
            recovery_threshold: 恢复阈值（从回撤中恢复的最小收益）
        """
        self.max_drawdown_limit = max_drawdown_limit
        self.warning_threshold = warning_threshold
        self.recovery_threshold = recovery_threshold
        self.drawdown_history = []
        
    def calculate_current_drawdown(self, nav_series: pd.Series) -> float:
        """
        计算当前回撤
        
        Args:
            nav_series: 净值序列
            
        Returns:
            当前回撤（负值）
        """
        if nav_series.empty:
            return 0.0
            
        current_nav = nav_series.iloc[-1]
        peak_nav = nav_series.max()
        
        if peak_nav <= 0:
            return 0.0
            
        current_drawdown = (current_nav - peak_nav) / peak_nav
        return current_drawdown
    
    def detect_drawdown_breaches(self, nav_series: pd.Series) -> Dict:
        """
        检测回撤突破
        
        Args:
            nav_series: 净值序列
            
        Returns:
            回撤突破检测结果
        """
        current_drawdown = self.calculate_current_drawdown(nav_series)
        
        breach_status = {
            'current_drawdown': current_drawdown,
            'is_warning_breached': current_drawdown <= self.warning_threshold,
            'is_limit_breached': current_drawdown <= self.max_drawdown_limit,
            'remaining_buffer': self.max_drawdown_limit - current_drawdown,
            'days_in_drawdown': self._calculate_days_in_drawdown(nav_series),
            'max_historical_drawdown': self._calculate_max_historical_drawdown(nav_series)
        }
        
        return breach_status
    
    def _calculate_days_in_drawdown(self, nav_series: pd.Series) -> int:
        """计算处于回撤状态的天数"""
        if nav_series.empty:
            return 0
            
        peak_idx = nav_series.idxmax()
        current_idx = nav_series.index[-1]
        
        if current_idx <= peak_idx:
            return 0
            
        # 从峰值后开始计算连续下跌天数
        post_peak_nav = nav_series[peak_idx:]
        days_in_drawdown = len(post_peak_nav) - 1
        return days_in_drawdown
    
    def _calculate_max_historical_drawdown(self, nav_series: pd.Series) -> float:
        """计算历史最大回撤"""
        if nav_series.empty or len(nav_series) < 2:
            return 0.0
            
        rolling_max = nav_series.expanding().max()
        drawdown = (nav_series - rolling_max) / rolling_max
        max_drawdown = drawdown.min()
        return max_drawdown
    
    def generate_risk_signals(self, nav_series: pd.Series) -> Dict[str, bool]:
        """
        生成风险信号
        
        Args:
            nav_series: 净值序列
            
        Returns:
            风险信号字典
        """
        breach_status = self.detect_drawdown_breaches(nav_series)
        
        signals = {
            'warning_signal': breach_status['is_warning_breached'],
            'stop_loss_signal': breach_status['is_limit_breached'],
            'recovery_signal': False,
            'extended_drawdown_signal': breach_status['days_in_drawdown'] > 60  # 超过60天
        }
        
        # 检查恢复信号
        if len(nav_series) >= 2:
            recent_return = (nav_series.iloc[-1] / nav_series.iloc[-2]) - 1
            if recent_return >= self.recovery_threshold:
                signals['recovery_signal'] = True
                
        return signals
    
    def dynamic_risk_budgeting(self, portfolio_weights: Dict[str, float],
                             fund_risk_scores: Dict[str, float]) -> Dict[str, float]:
        """
        动态风险预算分配
        
        Args:
            portfolio_weights: 当前组合权重
            fund_risk_scores: 基金风险评分（越高风险越大）
            
        Returns:
            调整后的权重
        """
        if not portfolio_weights or not fund_risk_scores:
            return portfolio_weights
            
        # 根据风险评分调整权重（风险越高，权重越低）
        adjusted_weights = {}
        total_adjusted_weight = 0.0
        
        for fund_code, weight in portfolio_weights.items():
            risk_score = fund_risk_scores.get(fund_code, 1.0)
            # 风险调整因子：风险评分越高，调整因子越小
            risk_adjustment_factor = 1.0 / (1.0 + risk_score)
            adjusted_weight = weight * risk_adjustment_factor
            adjusted_weights[fund_code] = adjusted_weight
            total_adjusted_weight += adjusted_weight
            
        # 归一化
        if total_adjusted_weight > 0:
            for fund_code in adjusted_weights:
                adjusted_weights[fund_code] /= total_adjusted_weight
                
        return adjusted_weights
    
    def monitor_portfolio_drawdown(self, portfolio_nav_series: pd.Series,
                                alert_callback: Optional[callable] = None) -> Dict:
        """
        监控组合回撤
        
        Args:
            portfolio_nav_series: 组合净值序列
            alert_callback: 预警回调函数
            
        Returns:
            监控结果
        """
        breach_status = self.detect_drawdown_breaches(portfolio_nav_series)
        risk_signals = self.generate_risk_signals(portfolio_nav_series)
        
        monitoring_result = {
            'breach_status': breach_status,
            'risk_signals': risk_signals,
            'timestamp': pd.Timestamp.now()
        }
        
        # 触发预警
        if alert_callback and (risk_signals['warning_signal'] or risk_signals['stop_loss_signal']):
            alert_callback(monitoring_result)
            
        return monitoring_result