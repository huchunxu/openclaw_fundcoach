#!/usr/bin/env python3
"""
Backtest Engine 单元测试
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from agents.data_backtest.backtest_engine import BacktestEngine


class TestBacktestEngine(unittest.TestCase):
    """Backtest Engine 测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.engine = BacktestEngine()
        
        # 创建测试数据
        dates = pd.date_range(start='2023-01-01', end='2024-01-01', freq='D')
        np.random.seed(42)
        returns = np.random.normal(0.001, 0.02, len(dates))
        nav = [1.0]
        for r in returns[1:]:
            nav.append(nav[-1] * (1 + r))
        
        self.test_data = pd.DataFrame({
            'date': dates,
            'nav': nav,
            'daily_return': returns
        })
    
    def test_calculate_annualized_return(self):
        """测试年化收益率计算"""
        annual_return = self.engine.calculate_annualized_return(self.test_data)
        self.assertIsInstance(annual_return, float)
        self.assertGreaterEqual(annual_return, -1.0)
    
    def test_calculate_sharpe_ratio(self):
        """测试夏普率计算"""
        sharpe = self.engine.calculate_sharpe_ratio(self.test_data)
        self.assertIsInstance(sharpe, float)
    
    def test_calculate_max_drawdown(self):
        """测试最大回撤计算"""
        max_dd = self.engine.calculate_max_drawdown(self.test_data)
        self.assertIsInstance(max_dd, float)
        self.assertLessEqual(max_dd, 0.0)
        self.assertGreaterEqual(max_dd, -1.0)
    
    def test_calculate_volatility(self):
        """测试波动率计算"""
        vol = self.engine.calculate_volatility(self.test_data)
        self.assertIsInstance(vol, float)
        self.assertGreaterEqual(vol, 0.0)
    
    def test_run_backtest_single_fund(self):
        """测试单基金回测"""
        result = self.engine.run_backtest({'test_fund': self.test_data})
        self.assertIn('test_fund', result)
        self.assertIn('annualized_return', result['test_fund'])
        self.assertIn('sharpe_ratio', result['test_fund'])
        self.assertIn('max_drawdown', result['test_fund'])
        self.assertIn('volatility', result['test_fund'])
    
    def test_run_backtest_portfolio(self):
        """测试组合回测"""
        portfolio_data = {
            'fund1': self.test_data,
            'fund2': self.test_data.copy()
        }
        weights = {'fund1': 0.5, 'fund2': 0.5}
        result = self.engine.run_backtest(portfolio_data, weights)
        self.assertIn('portfolio', result)
        self.assertIn('annualized_return', result['portfolio'])
        self.assertIn('sharpe_ratio', result['portfolio'])
        self.assertIn('max_drawdown', result['portfolio'])
        self.assertIn('volatility', result['portfolio'])


if __name__ == '__main__':
    unittest.main()