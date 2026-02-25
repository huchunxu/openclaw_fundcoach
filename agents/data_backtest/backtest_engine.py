"""
回测引擎模块

功能：
- 计算年化收益率
- 计算夏普率  
- 计算最大回撤
- 计算波动率
- 支持多基金组合回测
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Union


class BacktestEngine:
    """回测引擎"""
    
    def __init__(self):
        pass
    
    def calculate_annual_return(self, returns: pd.Series) -> float:
        """
        计算年化收益率
        
        Args:
            returns: 日收益率序列
            
        Returns:
            年化收益率
        """
        if len(returns) == 0:
            return 0.0
            
        total_return = (1 + returns).prod()
        years = len(returns) / 252  # 假设252个交易日
        annual_return = total_return ** (1 / years) - 1
        return annual_return
    
    def calculate_sharpe_ratio(self, returns: pd.Series, risk_free_rate: float = 0.02) -> float:
        """
        计算夏普率
        
        Args:
            returns: 日收益率序列
            risk_free_rate: 无风险利率（年化）
            
        Returns:
            夏普率
        """
        if len(returns) == 0:
            return 0.0
            
        annual_return = self.calculate_annual_return(returns)
        annual_volatility = returns.std() * np.sqrt(252)
        sharpe_ratio = (annual_return - risk_free_rate) / annual_volatility
        return sharpe_ratio
    
    def calculate_max_drawdown(self, nav_series: pd.Series) -> float:
        """
        计算最大回撤
        
        Args:
            nav_series: 净值序列
            
        Returns:
            最大回撤（负值）
        """
        if len(nav_series) == 0:
            return 0.0
            
        rolling_max = nav_series.expanding().max()
        drawdowns = (nav_series - rolling_max) / rolling_max
        max_drawdown = drawdowns.min()
        return max_drawdown
    
    def calculate_volatility(self, returns: pd.Series) -> float:
        """
        计算年化波动率
        
        Args:
            returns: 日收益率序列
            
        Returns:
            年化波动率
        """
        if len(returns) == 0:
            return 0.0
            
        annual_volatility = returns.std() * np.sqrt(252)
        return annual_volatility
    
    def backtest_portfolio(self, fund_nav_data: Dict[str, pd.DataFrame], weights: List[float] = None) -> Dict:
        """
        回测投资组合
        
        Args:
            fund_nav_data: 基金净值数据字典 {fund_code: nav_dataframe}
            weights: 权重列表，如果为None则使用等权重
            
        Returns:
            回测结果字典
        """
        # 合并所有基金的净值数据
        combined_nav = None
        fund_codes = list(fund_nav_data.keys())
        
        for fund_code in fund_codes:
            nav_data = fund_nav_data[fund_code]
            if combined_nav is None:
                combined_nav = nav_data[['date', 'nav']].copy()
                combined_nav.columns = ['date', fund_code]
            else:
                temp_df = nav_data[['date', 'nav']].copy()
                temp_df.columns = ['date', fund_code]
                combined_nav = pd.merge(combined_nav, temp_df, on='date', how='inner')
        
        if combined_nav is None or len(combined_nav) == 0:
            return {}
        
        # 设置权重
        if weights is None:
            weights = [1.0 / len(fund_codes)] * len(fund_codes)
        
        # 计算组合净值
        portfolio_nav = 0
        for i, fund_code in enumerate(fund_codes):
            portfolio_nav += combined_nav[fund_code] * weights[i]
        
        combined_nav['portfolio_nav'] = portfolio_nav
        
        # 计算日收益率
        combined_nav['portfolio_return'] = combined_nav['portfolio_nav'].pct_change()
        
        # 计算各项指标
        returns = combined_nav['portfolio_return'].dropna()
        nav_series = combined_nav['portfolio_nav']
        
        results = {
            'annual_return': self.calculate_annual_return(returns),
            'sharpe_ratio': self.calculate_sharpe_ratio(returns),
            'max_drawdown': self.calculate_max_drawdown(nav_series),
            'volatility': self.calculate_volatility(returns),
            'total_days': len(returns),
            'start_date': combined_nav['date'].iloc[0],
            'end_date': combined_nav['date'].iloc[-1]
        }
        
        return results


if __name__ == "__main__":
    # 测试代码
    engine = BacktestEngine()
    
    # 创建示例数据
    dates = pd.date_range('2023-01-01', periods=252, freq='D')
    nav_values = [1.0]
    for i in range(1, 252):
        daily_return = np.random.normal(0.0005, 0.01)  # 日均收益0.05%，波动率1%
        nav_values.append(nav_values[-1] * (1 + daily_return))
    
    test_nav = pd.DataFrame({
        'date': dates,
        'nav': nav_values
    })
    
    returns = test_nav['nav'].pct_change().dropna()
    nav_series = test_nav['nav']
    
    print(f"年化收益率: {engine.calculate_annual_return(returns):.4f}")
    print(f"夏普率: {engine.calculate_sharpe_ratio(returns):.4f}")
    print(f"最大回撤: {engine.calculate_max_drawdown(nav_series):.4f}")
    print(f"波动率: {engine.calculate_volatility(returns):.4f}")