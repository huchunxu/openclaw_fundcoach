"""
回测引擎模块

功能：
- 计算年化收益率
- 计算夏普率  
- 计算最大回撤
- 计算波动率
- 支持多基金组合回测
- 牛熊周期覆盖验证
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Union, Optional
import warnings
warnings.filterwarnings('ignore')


class BacktestEngine:
    """回测引擎"""
    
    def __init__(self, risk_free_rate: float = 0.02):
        """
        初始化回测引擎
        
        Args:
            risk_free_rate: 无风险利率，默认2%
        """
        self.risk_free_rate = risk_free_rate
        
    def calculate_annual_return(self, nav_series: pd.Series, dates: pd.Series) -> float:
        """
        计算年化收益率
        
        Args:
            nav_series: 净值序列
            dates: 日期序列
            
        Returns:
            年化收益率
        """
        if len(nav_series) < 2:
            return 0.0
            
        total_return = (nav_series.iloc[-1] / nav_series.iloc[0]) - 1
        start_date = pd.to_datetime(dates.iloc[0])
        end_date = pd.to_datetime(dates.iloc[-1])
        days = (end_date - start_date).days
        
        if days <= 0:
            return 0.0
            
        annual_return = (1 + total_return) ** (365 / days) - 1
        return annual_return
    
    def calculate_sharpe_ratio(self, nav_series: pd.Series, dates: pd.Series) -> float:
        """
        计算夏普率
        
        Args:
            nav_series: 净值序列  
            dates: 日期序列
            
        Returns:
            夏普率
        """
        if len(nav_series) < 2:
            return 0.0
            
        # 计算日收益率
        daily_returns = nav_series.pct_change().dropna()
        
        if len(daily_returns) == 0:
            return 0.0
            
        # 年化收益率
        annual_return = self.calculate_annual_return(nav_series, dates)
        
        # 年化波动率
        annual_volatility = daily_returns.std() * np.sqrt(252)
        
        if annual_volatility == 0:
            return 0.0
            
        sharpe_ratio = (annual_return - self.risk_free_rate) / annual_volatility
        return sharpe_ratio
    
    def calculate_max_drawdown(self, nav_series: pd.Series) -> float:
        """
        计算最大回撤
        
        Args:
            nav_series: 净值序列
            
        Returns:
            最大回撤（负值）
        """
        if len(nav_series) < 2:
            return 0.0
            
        # 计算累计最大净值
        rolling_max = nav_series.expanding().max()
        # 计算回撤
        drawdown = (nav_series - rolling_max) / rolling_max
        max_drawdown = drawdown.min()
        return max_drawdown
    
    def calculate_volatility(self, nav_series: pd.Series) -> float:
        """
        计算年化波动率
        
        Args:
            nav_series: 净值序列
            
        Returns:
            年化波动率
        """
        if len(nav_series) < 2:
            return 0.0
            
        daily_returns = nav_series.pct_change().dropna()
        if len(daily_returns) == 0:
            return 0.0
            
        annual_volatility = daily_returns.std() * np.sqrt(252)
        return annual_volatility
    
    def backtest_single_fund(self, fund_code: str, nav_data: pd.DataFrame) -> Dict:
        """
        单只基金回测
        
        Args:
            fund_code: 基金代码
            nav_data: 基金净值数据（包含date, nav列）
            
        Returns:
            回测结果字典
        """
        if nav_data.empty or 'nav' not in nav_data.columns:
            return {}
            
        nav_series = nav_data['nav'].dropna()
        dates = nav_data['date']
        
        if len(nav_series) < 2:
            return {}
        
        results = {
            'fund_code': fund_code,
            'total_days': len(nav_series),
            'start_date': dates.iloc[0].strftime('%Y-%m-%d'),
            'end_date': dates.iloc[-1].strftime('%Y-%m-%d'),
            'final_nav': float(nav_series.iloc[-1]),
            'annual_return': self.calculate_annual_return(nav_series, dates),
            'sharpe_ratio': self.calculate_sharpe_ratio(nav_series, dates),
            'max_drawdown': self.calculate_max_drawdown(nav_series),
            'volatility': self.calculate_volatility(nav_series)
        }
        
        return results
    
    def backtest_portfolio(self, portfolio_weights: Dict[str, float], 
                          fund_nav_dict: Dict[str, pd.DataFrame]) -> Dict:
        """
        投资组合回测
        
        Args:
            portfolio_weights: 组合权重字典 {fund_code: weight}
            fund_nav_dict: 基金净值数据字典 {fund_code: DataFrame}
            
        Returns:
            组合回测结果
        """
        # 对齐所有基金的日期
        all_dates = None
        for fund_code, nav_data in fund_nav_dict.items():
            if nav_data.empty:
                continue
            if all_dates is None:
                all_dates = set(nav_data['date'])
            else:
                all_dates = all_dates.intersection(set(nav_data['date']))
        
        if not all_dates or len(all_dates) < 2:
            return {}
        
        all_dates = sorted(list(all_dates))
        
        # 构建组合净值
        portfolio_nav = []
        valid_dates = []
        
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
                # 归一化权重
                normalized_nav = weighted_nav / total_weight
                portfolio_nav.append(normalized_nav)
                valid_dates.append(date)
        
        if len(portfolio_nav) < 2:
            return {}
        
        nav_series = pd.Series(portfolio_nav)
        dates_series = pd.Series(valid_dates)
        
        results = {
            'portfolio_type': 'weighted',
            'total_days': len(nav_series),
            'start_date': dates_series.iloc[0].strftime('%Y-%m-%d'),
            'end_date': dates_series.iloc[-1].strftime('%Y-%m-%d'),
            'annual_return': self.calculate_annual_return(nav_series, dates_series),
            'sharpe_ratio': self.calculate_sharpe_ratio(nav_series, dates_series),
            'max_drawdown': self.calculate_max_drawdown(nav_series),
            'volatility': self.calculate_volatility(nav_series),
            'component_funds': list(portfolio_weights.keys()),
            'weights': portfolio_weights
        }
        
        return results
    
    def validate_bull_bear_coverage(self, dates: pd.Series) -> Dict:
        """
        验证是否覆盖完整牛熊周期
        
        Args:
            dates: 日期序列
            
        Returns:
            覆盖情况字典
        """
        if dates.empty:
            return {'covered': False, 'reason': 'No dates provided'}
        
        start_date = pd.to_datetime(dates.min())
        end_date = pd.to_datetime(dates.max())
        total_years = (end_date - start_date).days / 365.25
        
        # 简单判断：至少3年数据，且跨越多个市场周期
        covered = total_years >= 3.0
        
        return {
            'covered': covered,
            'total_years': total_years,
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'reason': 'Sufficient data coverage' if covered else 'Insufficient data period'
        }


if __name__ == "__main__":
    # 测试代码
    engine = BacktestEngine()
    
    # 创建测试数据
    dates = pd.date_range(start='2023-01-01', end='2026-02-25', freq='D')
    # 模拟净值数据（简单随机游走）
    np.random.seed(42)
    returns = np.random.normal(0.0005, 0.01, len(dates))
    nav = [1.0]
    for r in returns[1:]:
        nav.append(nav[-1] * (1 + r))
    
    test_data = pd.DataFrame({
        'date': dates,
        'nav': nav
    })
    
    # 测试单基金回测
    results = engine.backtest_single_fund('000001', test_data)
    print("Single fund backtest results:")
    for key, value in results.items():
        print(f"  {key}: {value}")
    
    # 测试牛熊周期覆盖
    coverage = engine.validate_bull_bear_coverage(test_data['date'])
    print("\nBull/bear cycle coverage:")
    print(f"  Covered: {coverage['covered']}")
    print(f"  Total years: {coverage['total_years']:.2f}")