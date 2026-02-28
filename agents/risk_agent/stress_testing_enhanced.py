"""
增强版极端行情模拟模块

功能：
- 扩展历史压力测试场景（2008、2015、2020、2022等）
- 增强蒙特卡洛模拟（支持相关性结构）
- 添加流动性风险测试
- 行业特定压力场景
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from scipy.stats import norm


class EnhancedStressTesting:
    """增强版压力测试引擎"""
    
    def __init__(self):
        # 扩展的历史极端事件场景
        self.historical_scenarios = {
            '2008_global_crisis': {
                'market_drop': -0.55,
                'volatility_spike': 3.5,
                'liquidity_dry_up': 0.7,
                'correlation_spike': 0.9
            },
            '2015_china_turbulence': {
                'market_drop': -0.35,
                'volatility_spike': 2.8,
                'liquidity_dry_up': 0.5,
                'correlation_spike': 0.8
            },
            '2020_pandemic_crash': {
                'market_drop': -0.38,
                'volatility_spike': 4.2,
                'liquidity_dry_up': 0.6,
                'correlation_spike': 0.85
            },
            '2022_rate_hike_cycle': {
                'market_drop': -0.25,
                'volatility_spike': 2.5,
                'liquidity_dry_up': 0.4,
                'correlation_spike': 0.75
            }
        }
        
        # 行业特定压力场景
        self.sector_scenarios = {
            'technology': {'sector_drop': -0.45, 'volatility_spike': 3.0},
            'healthcare': {'sector_drop': -0.30, 'volatility_spike': 2.5},
            'finance': {'sector_drop': -0.40, 'volatility_spike': 3.2},
            'consumer': {'sector_drop': -0.25, 'volatility_spike': 2.0},
            'energy': {'sector_drop': -0.50, 'volatility_spike': 3.5}
        }
        
    def apply_historical_scenario(self, portfolio_nav: pd.Series, 
                               scenario_name: str = '2008_global_crisis',
                               sector_exposure: Optional[Dict[str, float]] = None) -> pd.Series:
        """
        应用历史极端场景，考虑行业暴露
        
        Args:
            portfolio_nav: 组合净值序列
            scenario_name: 场景名称
            sector_exposure: 行业暴露字典 {sector: weight}
            
        Returns:
            模拟后的净值序列
        """
        if scenario_name not in self.historical_scenarios:
            return portfolio_nav
            
        scenario = self.historical_scenarios[scenario_name]
        market_drop = scenario['market_drop']
        
        # 基础市场下跌
        stressed_nav = portfolio_nav * (1 + market_drop)
        
        # 如果有行业暴露信息，添加行业特定影响
        if sector_exposure:
            sector_impact = 0.0
            for sector, weight in sector_exposure.items():
                if sector in self.sector_scenarios:
                    sector_drop = self.sector_scenarios[sector]['sector_drop']
                    sector_impact += weight * sector_drop
                    
            stressed_nav = stressed_nav * (1 + sector_impact)
            
        return stressed_nav
    
    def enhanced_monte_carlo_simulation(self, portfolio_nav: pd.Series,
                                     fund_nav_dict: Optional[Dict[str, pd.DataFrame]] = None,
                                     num_simulations: int = 1000,
                                     time_horizon: int = 252) -> Dict:
        """
        增强蒙特卡洛模拟，支持多资产相关性
        
        Args:
            portfolio_nav: 组合净值序列
            fund_nav_dict: 各基金净值数据（用于相关性建模）
            num_simulations: 模拟次数
            time_horizon: 时间范围（交易日）
            
        Returns:
            模拟结果统计
        """
        if len(portfolio_nav) < 2:
            return {}
            
        # 如果有单个基金数据，使用多资产模拟
        if fund_nav_dict and len(fund_nav_dict) > 1:
            return self._multi_asset_monte_carlo(fund_nav_dict, num_simulations, time_horizon)
            
        # 单资产模拟
        returns = portfolio_nav.pct_change().dropna()
        mean_return = returns.mean()
        std_return = returns.std()
        
        simulation_results = []
        paths = []
        
        for _ in range(num_simulations):
            # 生成随机路径
            simulated_returns = np.random.normal(mean_return, std_return, time_horizon)
            simulated_nav = [portfolio_nav.iloc[-1]]
            
            path = [simulated_nav[0]]
            for r in simulated_returns:
                next_nav = path[-1] * (1 + r)
                path.append(next_nav)
                
            paths.append(path)
            simulation_results.append(path[-1])
            
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
            'simulation_paths': paths[:100]  # 保存部分路径用于可视化
        }
        
        return results
    
    def _multi_asset_monte_carlo(self, fund_nav_dict: Dict[str, pd.DataFrame],
                                num_simulations: int, time_horizon: int) -> Dict:
        """
        多资产蒙特卡洛模拟
        """
        # 对齐日期并计算收益率
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
        fund_codes = list(fund_nav_dict.keys())
        
        # 构建收益率矩阵
        returns_matrix = []
        for fund_code in fund_codes:
            nav_data = fund_nav_dict[fund_code]
            fund_returns = []
            for date in all_dates:
                nav_on_date = nav_data[nav_data['date'] == date]
                if not nav_on_date.empty:
                    fund_returns.append(nav_on_date['nav'].iloc[0])
                else:
                    fund_returns.append(np.nan)
                    
            fund_returns = pd.Series(fund_returns).pct_change().dropna().values
            returns_matrix.append(fund_returns)
            
        if len(returns_matrix) == 0:
            return {}
            
        # 计算均值向量和协方差矩阵
        returns_array = np.array(returns_matrix)
        mean_returns = np.mean(returns_array, axis=1)
        cov_matrix = np.cov(returns_array)
        
        # Cholesky分解用于相关性模拟
        try:
            chol_matrix = np.linalg.cholesky(cov_matrix)
        except np.linalg.LinAlgError:
            # 如果协方差矩阵不是正定的，使用对角矩阵
            chol_matrix = np.diag(np.sqrt(np.diag(cov_matrix)))
            
        simulation_results = []
        paths = []
        
        for _ in range(num_simulations):
            # 生成相关随机变量
            random_normals = np.random.normal(0, 1, (len(fund_codes), time_horizon))
            correlated_returns = mean_returns.reshape(-1, 1) + np.dot(chol_matrix, random_normals)
            
            # 模拟各资产路径
            asset_paths = []
            for i, fund_code in enumerate(fund_codes):
                nav_path = [fund_nav_dict[fund_code]['nav'].iloc[-1]]
                for t in range(time_horizon):
                    next_nav = nav_path[-1] * (1 + correlated_returns[i, t])
                    nav_path.append(next_nav)
                asset_paths.append(nav_path)
                
            # 假设等权重组合
            portfolio_path = np.mean(asset_paths, axis=0)
            paths.append(portfolio_path.tolist())
            simulation_results.append(portfolio_path[-1])
            
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
            'simulation_paths': paths[:100]
        }
        
        return results
    
    def liquidity_risk_test(self, portfolio_nav: pd.Series,
                          liquidity_shock: float = 0.3) -> pd.Series:
        """
        流动性风险测试
        
        Args:
            portfolio_nav: 组合净值序列
            liquidity_shock: 流动性冲击程度（0-1）
            
        Returns:
            考虑流动性冲击的净值序列
        """
        if len(portfolio_nav) < 2:
            return portfolio_nav
            
        # 流动性冲击导致无法及时调整仓位，放大损失
        returns = portfolio_nav.pct_change().dropna()
        liquidity_adjusted_returns = returns.copy()
        
        # 在下跌期间放大损失
        for i in range(1, len(liquidity_adjusted_returns)):
            if liquidity_adjusted_returns.iloc[i-1] < 0:
                liquidity_adjusted_returns.iloc[i] *= (1 + liquidity_shock)
                
        # 重建净值序列
        stressed_nav = [portfolio_nav.iloc[0]]
        for r in liquidity_adjusted_returns:
            stressed_nav.append(stressed_nav[-1] * (1 + r))
            
        return pd.Series(stressed_nav, index=portfolio_nav.index)
    
    def run_comprehensive_stress_test(self, portfolio_nav: pd.Series,
                                    fund_nav_dict: Optional[Dict[str, pd.DataFrame]] = None,
                                    sector_exposure: Optional[Dict[str, float]] = None) -> Dict:
        """
        运行综合压力测试
        
        Args:
            portfolio_nav: 组合净值序列
            fund_nav_dict: 各基金净值数据
            sector_exposure: 行业暴露信息
            
        Returns:
            完整压力测试报告
        """
        stress_test_results = {}
        
        # 历史场景测试
        for scenario_name in self.historical_scenarios.keys():
            stressed_nav = self.apply_historical_scenario(
                portfolio_nav, scenario_name, sector_exposure
            )
            max_dd = (stressed_nav / stressed_nav.expanding().max() - 1).min()
            stress_test_results[f'{scenario_name}_max_drawdown'] = max_dd
            
        # 增强蒙特卡洛模拟
        mc_results = self.enhanced_monte_carlo_simulation(
            portfolio_nav, fund_nav_dict
        )
        stress_test_results['monte_carlo'] = mc_results
        
        # 流动性风险测试
        liquidity_nav = self.liquidity_risk_test(portfolio_nav)
        liquidity_max_dd = (liquidity_nav / liquidity_nav.expanding().max() - 1).min()
        stress_test_results['liquidity_risk_max_drawdown'] = liquidity_max_dd
        
        # 极端波动率测试
        extreme_vol_nav = self.extreme_volatility_test(portfolio_nav)
        extreme_vol_max_dd = (extreme_vol_nav / extreme_vol_nav.expanding().max() - 1).min()
        stress_test_results['extreme_volatility_max_drawdown'] = extreme_vol_max_dd
        
        return stress_test_results
    
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