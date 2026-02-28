"""
增强版回测引擎

功能：
- 支持大规模基金数据回测
- 多因子回测框架
- 牛熊市周期识别
- 交易成本模拟
- 滑点模拟
- 完整的绩效指标计算
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

class EnhancedBacktestEngine:
    """增强版回测引擎"""
    
    def __init__(self, transaction_cost: float = 0.001, slippage: float = 0.0005):
        """
        初始化回测引擎
        
        Args:
            transaction_cost: 交易成本（默认0.1%）
            slippage: 滑点（默认0.05%）
        """
        self.transaction_cost = transaction_cost
        self.slippage = slippage
        self.market_cycles = {
            'bull_2019_2021': ('2019-01-01', '2021-02-18'),
            'bear_2021_2022': ('2021-02-19', '2022-10-31'),
            'bull_2023_2024': ('2022-11-01', '2024-01-01')
        }
        
    def identify_market_cycles(self, dates: pd.Series) -> pd.Series:
        """
        识别市场周期（牛熊市）
        
        Args:
            dates: 日期序列
            
        Returns:
            市场周期标签序列
        """
        cycle_labels = pd.Series(index=dates, dtype='object')
        cycle_labels[:] = 'unknown'
        
        for cycle_name, (start_date, end_date) in self.market_cycles.items():
            mask = (dates >= start_date) & (dates <= end_date)
            if cycle_name.startswith('bull'):
                cycle_labels[mask] = 'bull'
            elif cycle_name.startswith('bear'):
                cycle_labels[mask] = 'bear'
                
        return cycle_labels
    
    def calculate_performance_metrics(self, returns: pd.Series, 
                                   risk_free_rate: float = 0.02) -> Dict:
        """
        计算完整的绩效指标
        
        Args:
            returns: 日收益率序列
            risk_free_rate: 无风险利率（年化）
            
        Returns:
            绩效指标字典
        """
        if len(returns) < 2:
            return self._empty_metrics()
            
        # 基础统计
        total_return = (1 + returns).prod() - 1
        annual_return = (1 + total_return) ** (252 / len(returns)) - 1
        volatility = returns.std() * np.sqrt(252)
        sharpe_ratio = (annual_return - risk_free_rate) / volatility if volatility > 0 else 0
        
        # 最大回撤
        cum_returns = (1 + returns).cumprod()
        running_max = cum_returns.expanding().max()
        drawdowns = (cum_returns / running_max - 1)
        max_drawdown = drawdowns.min()
        
        # 回撤相关指标
        avg_drawdown = drawdowns[drawdowns < 0].mean() if len(drawdowns[drawdowns < 0]) > 0 else 0
        drawdown_duration = self._calculate_drawdown_duration(drawdowns)
        recovery_time = self._calculate_recovery_time(drawdowns)
        
        # 下行风险指标
        downside_returns = returns[returns < 0]
        downside_deviation = downside_returns.std() * np.sqrt(252) if len(downside_returns) > 0 else 0
        sortino_ratio = (annual_return - risk_free_rate) / downside_deviation if downside_deviation > 0 else 0
        
        # 卡玛比率
        calmar_ratio = annual_return / abs(max_drawdown) if max_drawdown != 0 else 0
        
        # 胜率和盈亏比
        win_rate = (returns > 0).mean()
        avg_win = returns[returns > 0].mean() if len(returns[returns > 0]) > 0 else 0
        avg_loss = returns[returns < 0].mean() if len(returns[returns < 0]) > 0 else 0
        profit_loss_ratio = abs(avg_win / avg_loss) if avg_loss != 0 else float('inf')
        
        # 信息比率
        benchmark_return = risk_free_rate / 252  # 日无风险收益
        active_returns = returns - benchmark_return
        tracking_error = active_returns.std() * np.sqrt(252)
        information_ratio = active_returns.mean() * 252 / tracking_error if tracking_error > 0 else 0
        
        metrics = {
            'total_return': total_return,
            'annual_return': annual_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'avg_drawdown': avg_drawdown,
            'avg_drawdown_duration': drawdown_duration,
            'avg_recovery_days': recovery_time,
            'sortino_ratio': sortino_ratio,
            'calmar_ratio': calmar_ratio,
            'win_rate': win_rate,
            'profit_loss_ratio': profit_loss_ratio,
            'information_ratio': information_ratio,
            'downside_deviation': downside_deviation,
            'tracking_error': tracking_error
        }
        
        return metrics
    
    def _calculate_drawdown_duration(self, drawdowns: pd.Series) -> float:
        """计算平均回撤持续时间"""
        if len(drawdowns) == 0:
            return 0
            
        # 找到回撤开始和结束点
        drawdown_periods = []
        in_drawdown = False
        start_idx = None
        
        for idx, dd in enumerate(drawdowns):
            if dd < 0 and not in_drawdown:
                in_drawdown = True
                start_idx = idx
            elif dd >= 0 and in_drawdown:
                in_drawdown = False
                if start_idx is not None:
                    drawdown_periods.append(idx - start_idx)
                    
        if in_drawdown and start_idx is not None:
            drawdown_periods.append(len(drawdowns) - start_idx)
            
        return np.mean(drawdown_periods) if drawdown_periods else 0
    
    def _calculate_recovery_time(self, drawdowns: pd.Series) -> float:
        """计算平均恢复时间"""
        if len(drawdowns) == 0:
            return 0
            
        recovery_times = []
        in_drawdown = False
        drawdown_start = None
        
        for idx, dd in enumerate(drawdowns):
            if dd < 0 and not in_drawdown:
                in_drawdown = True
                drawdown_start = idx
            elif dd >= 0 and in_drawdown:
                in_drawdown = False
                if drawdown_start is not None:
                    recovery_times.append(idx - drawdown_start)
                    
        return np.mean(recovery_times) if recovery_times else 0
    
    def _empty_metrics(self) -> Dict:
        """返回空的绩效指标"""
        return {
            'total_return': 0,
            'annual_return': 0,
            'volatility': 0,
            'sharpe_ratio': 0,
            'max_drawdown': 0,
            'avg_drawdown': 0,
            'avg_drawdown_duration': 0,
            'avg_recovery_days': 0,
            'sortino_ratio': 0,
            'calmar_ratio': 0,
            'win_rate': 0,
            'profit_loss_ratio': 0,
            'information_ratio': 0,
            'downside_deviation': 0,
            'tracking_error': 0
        }
    
    def simulate_portfolio_returns(self, portfolio_weights: Dict[str, float],
                                fund_nav_dict: Dict[str, pd.DataFrame],
                                rebalance_frequency: str = 'monthly') -> pd.Series:
        """
        模拟投资组合收益率
        
        Args:
            portfolio_weights: 投资组合权重
            fund_nav_dict: 基金净值数据字典
            rebalance_frequency: 再平衡频率 ('daily', 'weekly', 'monthly', 'quarterly')
            
        Returns:
            组合日收益率序列
        """
        if not portfolio_weights or not fund_nav_dict:
            return pd.Series(dtype=float)
            
        # 对齐所有基金的日期
        all_dates = None
        for nav_data in fund_nav_dict.values():
            if nav_data.empty:
                continue
            if all_dates is None:
                all_dates = set(nav_data['date'])
            else:
                all_dates = all_dates.intersection(set(nav_data['date']))
                
        if not all_dates or len(all_dates) < 2:
            return pd.Series(dtype=float)
            
        all_dates = sorted(list(all_dates))
        portfolio_nav = []
        current_weights = portfolio_weights.copy()
        
        # 确定再平衡日期
        rebalance_dates = self._get_rebalance_dates(all_dates, rebalance_frequency)
        
        for i, date in enumerate(all_dates):
            # 检查是否需要再平衡
            if date in rebalance_dates and i > 0:
                current_weights = portfolio_weights.copy()
            
            # 计算当日组合净值
            weighted_nav = 0.0
            total_weight = 0.0
            
            for fund_code, weight in current_weights.items():
                if fund_code in fund_nav_dict:
                    nav_data = fund_nav_dict[fund_code]
                    nav_on_date = nav_data[nav_data['date'] == date]
                    if not nav_on_date.empty:
                        weighted_nav += weight * nav_on_date['nav'].iloc[0]
                        total_weight += weight
                        
            if total_weight > 0:
                normalized_nav = weighted_nav / total_weight
                portfolio_nav.append(normalized_nav)
            else:
                portfolio_nav.append(portfolio_nav[-1] if portfolio_nav else 1.0)
                
        # 转换为收益率
        portfolio_nav_series = pd.Series(portfolio_nav, index=all_dates)
        portfolio_returns = portfolio_nav_series.pct_change().dropna()
        
        return portfolio_returns
    
    def _get_rebalance_dates(self, dates: List, frequency: str) -> set:
        """获取再平衡日期"""
        dates_series = pd.Series(dates)
        
        if frequency == 'daily':
            return set(dates)
        elif frequency == 'weekly':
            weekly_dates = dates_series.resample('W').last()
            return set(weekly_dates.dropna().values)
        elif frequency == 'monthly':
            monthly_dates = dates_series.resample('M').last()
            return set(monthly_dates.dropna().values)
        elif frequency == 'quarterly':
            quarterly_dates = dates_series.resample('Q').last()
            return set(quarterly_dates.dropna().values)
        else:
            return set()
    
    def backtest_single_fund_enhanced(self, fund_code: str, 
                                    nav_data: pd.DataFrame,
                                    include_transaction_costs: bool = True) -> Dict:
        """
        增强版单基金回测
        
        Args:
            fund_code: 基金代码
            nav_data: 净值数据
            include_transaction_costs: 是否包含交易成本
            
        Returns:
            回测结果字典
        """
        if nav_data.empty or len(nav_data) < 2:
            return {fund_code: self._empty_metrics()}
            
        # 计算收益率
        returns = nav_data['nav'].pct_change().dropna()
        
        # 应用交易成本和滑点（如果是模拟交易）
        if include_transaction_costs:
            # 简化的交易成本模型
            transaction_penalty = self.transaction_cost + self.slippage
            # 假设每月交易一次
            monthly_penalty = transaction_penalty / 12
            annual_penalty = monthly_penalty * 252
            adjusted_returns = returns - annual_penalty / 252
        else:
            adjusted_returns = returns
            
        # 计算绩效指标
        metrics = self.calculate_performance_metrics(adjusted_returns)
        
        # 添加市场周期分析
        market_cycles = self.identify_market_cycles(nav_data['date'])
        cycle_returns = {}
        for cycle_type in ['bull', 'bear']:
            cycle_mask = market_cycles == cycle_type
            if cycle_mask.any():
                cycle_ret = returns[cycle_mask]
                if len(cycle_ret) > 0:
                    cycle_metrics = self.calculate_performance_metrics(cycle_ret)
                    cycle_returns[f'{cycle_type}_market'] = cycle_metrics
                    
        metrics['cycle_performance'] = cycle_returns
        
        return {fund_code: metrics}
    
    def backtest_portfolio_enhanced(self, portfolio_weights: Dict[str, float],
                                 fund_nav_dict: Dict[str, pd.DataFrame],
                                 rebalance_frequency: str = 'monthly',
                                 include_costs: bool = True) -> Dict:
        """
        增强版组合回测
        
        Args:
            portfolio_weights: 组合权重
            fund_nav_dict: 基金净值数据
            rebalance_frequency: 再平衡频率
            include_costs: 是否包含成本
            
        Returns:
            组合回测结果
        """
        # 模拟组合收益率
        portfolio_returns = self.simulate_portfolio_returns(
            portfolio_weights, fund_nav_dict, rebalance_frequency
        )
        
        if portfolio_returns.empty:
            return {'portfolio': self._empty_metrics()}
            
        # 计算绩效指标
        metrics = self.calculate_performance_metrics(portfolio_returns)
        
        # 风险分解
        risk_contribution = self._calculate_risk_contribution(
            portfolio_weights, fund_nav_dict
        )
        metrics['risk_contribution'] = risk_contribution
        
        return {'portfolio': metrics}
    
    def _calculate_risk_contribution(self, weights: Dict[str, float],
                                   nav_dict: Dict[str, pd.DataFrame]) -> Dict:
        """计算风险贡献"""
        try:
            # 构建收益率矩阵
            all_dates = None
            for nav_data in nav_dict.values():
                if nav_data.empty:
                    continue
                if all_dates is None:
                    all_dates = set(nav_data['date'])
                else:
                    all_dates = all_dates.intersection(set(nav_data['date']))
                    
            if not all_dates or len(all_dates) < 2:
                return {}
                
            all_dates = sorted(list(all_dates))
            returns_matrix = []
            fund_codes = []
            
            for fund_code, nav_data in nav_dict.items():
                if fund_code in weights:
                    fund_returns = []
                    for date in all_dates:
                        nav_on_date = nav_data[nav_data['date'] == date]
                        if not nav_on_date.empty:
                            fund_returns.append(nav_on_date['nav'].iloc[0])
                        else:
                            fund_returns.append(np.nan)
                            
                    returns_series = pd.Series(fund_returns).pct_change().dropna()
                    if len(returns_series) > 0:
                        returns_matrix.append(returns_series.values)
                        fund_codes.append(fund_code)
                        
            if len(returns_matrix) == 0:
                return {}
                
            # 计算协方差矩阵和风险贡献
            returns_array = np.array(returns_matrix)
            cov_matrix = np.cov(returns_array)
            weight_array = np.array([weights[code] for code in fund_codes])
            
            portfolio_vol = np.sqrt(np.dot(weight_array.T, np.dot(cov_matrix, weight_array)))
            marginal_contrib = np.dot(cov_matrix, weight_array) / portfolio_vol
            risk_contrib = weight_array * marginal_contrib
            
            risk_contribution = dict(zip(fund_codes, risk_contrib))
            return risk_contribution
            
        except Exception as e:
            return {}
    
    def comprehensive_backtest_analysis(self, fund_codes: List[str],
                                     fund_nav_dict: Dict[str, pd.DataFrame],
                                     strategy_weights: Optional[Dict[str, float]] = None) -> Dict:
        """
        综合回测分析
        
        Args:
            fund_codes: 基金代码列表
            fund_nav_dict: 基金净值数据
            strategy_weights: 策略权重（可选）
            
        Returns:
            完整回测分析报告
        """
        analysis_results = {}
        
        # 单基金回测
        single_fund_results = {}
        for fund_code in fund_codes:
            if fund_code in fund_nav_dict:
                result = self.backtest_single_fund_enhanced(fund_code, fund_nav_dict[fund_code])
                single_fund_results.update(result)
                
        analysis_results['single_fund_backtest'] = single_fund_results
        
        # 组合回测（如果有权重）
        if strategy_weights:
            portfolio_result = self.backtest_portfolio_enhanced(strategy_weights, fund_nav_dict)
            analysis_results['portfolio_backtest'] = portfolio_result
            
        # 相关性分析
        correlation_matrix = self._calculate_correlation_matrix(fund_nav_dict, fund_codes)
        analysis_results['correlation_matrix'] = correlation_matrix
        
        # 多样化效益分析
        diversification_benefit = self._calculate_diversification_benefit(
            single_fund_results, portfolio_result if strategy_weights else None
        )
        analysis_results['diversification_benefit'] = diversification_benefit
        
        return analysis_results
    
    def _calculate_correlation_matrix(self, nav_dict: Dict[str, pd.DataFrame], 
                                   fund_codes: List[str]) -> pd.DataFrame:
        """计算相关性矩阵"""
        try:
            # 对齐日期
            all_dates = None
            for fund_code in fund_codes:
                if fund_code in nav_dict:
                    nav_data = nav_dict[fund_code]
                    if nav_data.empty:
                        continue
                    if all_dates is None:
                        all_dates = set(nav_data['date'])
                    else:
                        all_dates = all_dates.intersection(set(nav_data['date']))
                        
            if not all_dates or len(all_dates) < 2:
                return pd.DataFrame()
                
            all_dates = sorted(list(all_dates))
            
            # 构建收益率矩阵
            returns_data = {}
            for fund_code in fund_codes:
                if fund_code in nav_dict:
                    nav_data = nav_dict[fund_code]
                    fund_returns = []
                    for date in all_dates:
                        nav_on_date = nav_data[nav_data['date'] == date]
                        if not nav_on_date.empty:
                            fund_returns.append(nav_on_date['nav'].iloc[0])
                        else:
                            fund_returns.append(np.nan)
                            
                    returns_series = pd.Series(fund_returns).pct_change().dropna()
                    if len(returns_series) > 0:
                        returns_data[fund_code] = returns_series.values
                        
            if len(returns_data) < 2:
                return pd.DataFrame()
                
            returns_df = pd.DataFrame(returns_data)
            correlation_matrix = returns_df.corr()
            return correlation_matrix
            
        except Exception as e:
            return pd.DataFrame()
    
    def _calculate_diversification_benefit(self, single_results: Dict, 
                                         portfolio_result: Optional[Dict]) -> Dict:
        """计算多样化效益"""
        if not portfolio_result:
            return {}
            
        try:
            portfolio_vol = portfolio_result['portfolio']['volatility']
            portfolio_return = portfolio_result['portfolio']['annual_return']
            
            # 计算加权平均单基金波动率
            weighted_avg_vol = 0
            weighted_avg_return = 0
            total_weight = 0
            
            # 这里需要权重信息，暂时返回空
            return {
                'portfolio_volatility': portfolio_vol,
                'weighted_avg_volatility': weighted_avg_vol,
                'diversification_ratio': portfolio_vol / weighted_avg_vol if weighted_avg_vol > 0 else 1,
                'portfolio_return': portfolio_return,
                'weighted_avg_return': weighted_avg_return
            }
            
        except Exception as e:
            return {}