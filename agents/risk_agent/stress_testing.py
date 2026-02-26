"""
极端行情模拟模块

功能：
- 历史压力测试场景
- 蒙特卡洛模拟
- 极端市场条件测试
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional


class StressTesting:
    """压力测试引擎"""
    
    def __init__(self):
        # 历史极端事件场景
        self.historical_scenarios = {
            '2008_crisis': {'market_drop': -0.5, 'volatility_spike': 3.0},
            '2015_turbulence': {'market_drop': -0.3, 'volatility_spike': 2.5},
            '2020_pandemic': {'market_drop': -0.35, 'volatility_spike': 4.0}
        }
        
    def apply_historical_scenario(self, portfolio_nav: pd.Series, 
                               scenario_name: str = '2008_crisis') -> pd.Series:
        """
        应用历史极端场景
        
        Args:
            portfolio_nav: 组合净值序列
            scenario_name: 场景名称
            
        Returns:
            模拟后的净值序列
        """
        if scenario_name not in self.historical_scenarios:
            return portfolio_nav
            
        scenario = self.historical_scenarios[scenario_name]
        market_drop = scenario['market_drop']
        
        # 简化模拟：应用市场下跌
        stressed_nav = portfolio_nav * (1 + market_drop)
        return stressed_nav
    
    def monte_carlo_simulation(self, portfolio_nav: pd.Series, 
                             num_simulations: int = 1000,
                             time_horizon: int = 252) -> Dict:
        """
        蒙特卡洛模拟
        
        Args:
            portfolio_nav: 组合净值序列
            num_simulations: 模拟次数
            time_horizon: 时间范围（交易日）
            
        Returns:
            模拟结果统计
        """
        if len(portfolio_nav) < 2:
            return {}
            
        # 计算历史收益率和波动率
        returns = portfolio_nav.pct_change().dropna()
        mean_return = returns.mean()
        std_return = returns.std()
        
        simulation_results = []
        
        for _ in range(num_simulations):
            # 生成随机路径
            simulated_returns = np.random.normal(mean_return, std_return, time_horizon)
            simulated_nav = [portfolio_nav.iloc[-1]]
            
            for r in simulated_returns:
                simulated_nav.append(simulated_nav[-1] * (1 + r))
                
            simulation_results.append(simulated_nav[-1])
            
        # 计算统计指标
        final_values = np.array(simulation_results)
        var_95 = np.percentile(final_values, 5)
        var_99 = np.percentile(final_values, 1)
        expected_shortfall_95 = final_values[final_values <= var_95].mean()
        
        results = {
            'mean_final_value': final_values.mean(),
            'std_final_value': final_values.std(),
            'var_95': var_95,
            'var_99': var_99,
            'expected_shortfall_95': expected_shortfall_95,
            'simulation_paths': simulation_results[:100]  # 保存部分路径用于可视化
        }
        
        return results
    
    def extreme_volatility_test(self, portfolio_nav: pd.Series,
                              volatility_multiplier: float = 3.0) -> pd.Series:
        """
        极端波动率测试
        
        Args:
            portfolio_nav: 组合净值序列
            volatility_multiplier: 波动率放大倍数
            
        Returns:
            高波动率下的净值序列
        """
        if len(portfolio_nav) < 2:
            return portfolio_nav
            
        returns = portfolio_nav.pct_change().dropna()
        amplified_returns = returns * volatility_multiplier
        
        stressed_nav = [portfolio_nav.iloc[0]]
        for r in amplified_returns:
            stressed_nav.append(stressed_nav[-1] * (1 + r))
            
        return pd.Series(stressed_nav, index=portfolio_nav.index)
    
    def run_comprehensive_stress_test(self, portfolio_nav: pd.Series) -> Dict:
        """
        运行综合压力测试
        
        Args:
            portfolio_nav: 组合净值序列
            
        Returns:
            完整压力测试报告
        """
        stress_test_results = {}
        
        # 历史场景测试
        for scenario_name in self.historical_scenarios.keys():
            stressed_nav = self.apply_historical_scenario(portfolio_nav, scenario_name)
            max_dd = (stressed_nav / stressed_nav.expanding().max() - 1).min()
            stress_test_results[f'{scenario_name}_max_drawdown'] = max_dd
            
        # 蒙特卡洛模拟
        mc_results = self.monte_carlo_simulation(portfolio_nav)
        stress_test_results['monte_carlo'] = mc_results
        
        # 极端波动率测试
        extreme_vol_nav = self.extreme_volatility_test(portfolio_nav)
        extreme_vol_max_dd = (extreme_vol_nav / extreme_vol_nav.expanding().max() - 1).min()
        stress_test_results['extreme_volatility_max_drawdown'] = extreme_vol_max_dd
        
        return stress_test_results