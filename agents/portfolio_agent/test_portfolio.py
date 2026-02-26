#!/usr/bin/env python3
"""
Portfolio Agent 单元测试
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from .portfolio_generator import PortfolioGenerator
from .weight_optimizer import WeightOptimizer
from .risk_balancer import RiskBalancer


class TestPortfolioAgent(unittest.TestCase):
    """Portfolio Agent 测试类"""
    
    def setUp(self):
        """测试前准备"""
        # 创建测试基金打分数据
        self.test_fund_scores = pd.DataFrame({
            'fund_code': ['000001', '000002', '000003', '000004', '000005'],
            'composite_score': [0.9, 0.8, 0.7, 0.6, 0.5],
            'investment_style': ['value', 'growth', 'balanced', 'value', 'growth']
        })
        
        # 创建测试净值数据
        dates = pd.date_range(start='2023-01-01', end='2024-01-01', freq='D')
        np.random.seed(42)
        returns = np.random.normal(0.001, 0.02, len(dates))
        nav = [1.0]
        for r in returns[1:]:
            nav.append(nav[-1] * (1 + r))
            
        self.test_nav_data = pd.DataFrame({
            'date': dates,
            'nav': nav
        })
        
        self.test_fund_nav_dict = {
            '000001': self.test_nav_data,
            '000002': self.test_nav_data.copy(),
            '000003': self.test_nav_data.copy(),
            '000004': self.test_nav_data.copy(), 
            '000005': self.test_nav_data.copy()
        }
    
    def test_portfolio_generator(self):
        """测试组合生成器"""
        generator = PortfolioGenerator()
        
        # 测试Top-N组合
        top_n_portfolio = generator.generate_top_n_portfolio(self.test_fund_scores, n=3)
        self.assertEqual(len(top_n_portfolio), 3)
        self.assertAlmostEqual(sum(top_n_portfolio.values()), 1.0, places=6)
        
        # 测试分层组合
        layered_portfolio = generator.generate_layered_portfolio(self.test_fund_scores)
        self.assertGreater(len(layered_portfolio), 0)
        self.assertAlmostEqual(sum(layered_portfolio.values()), 1.0, places=6)
        
        # 测试分散化组合
        diversified_portfolio = generator.generate_diversified_portfolio(self.test_fund_scores)
        self.assertGreater(len(diversified_portfolio), 0)
        self.assertAlmostEqual(sum(diversified_portfolio.values()), 1.0, places=6)
    
    def test_weight_optimizer(self):
        """测试权重优化器"""
        optimizer = WeightOptimizer()
        
        # 测试风险平价优化
        risk_parity_weights = optimizer.optimize_portfolio_weights(
            self.test_fund_scores, self.test_fund_nav_dict, 'risk_parity'
        )
        self.assertGreater(len(risk_parity_weights), 0)
        self.assertAlmostEqual(sum(risk_parity_weights.values()), 1.0, places=6)
        
        # 测试最大夏普率优化
        max_sharpe_weights = optimizer.optimize_portfolio_weights(
            self.test_fund_scores, self.test_fund_nav_dict, 'max_sharpe'
        )
        self.assertGreater(len(max_sharpe_weights), 0)
        self.assertAlmostEqual(sum(max_sharpe_weights.values()), 1.0, places=6)
    
    def test_risk_balancer(self):
        """测试风险平衡器"""
        balancer = RiskBalancer()
        
        # 创建一个高集中度的组合
        high_concentration_portfolio = {'000001': 0.8, '000002': 0.2}
        
        # 分析风险
        risk_analysis = balancer.analyze_portfolio_risk(
            high_concentration_portfolio, self.test_fund_nav_dict
        )
        self.assertIn('concentration_risk', risk_analysis)
        self.assertIn('max_drawdown', risk_analysis)
        
        # 调整权重
        adjusted_weights = balancer.adjust_weights_for_risk(
            high_concentration_portfolio, self.test_fund_nav_dict
        )
        self.assertLessEqual(max(adjusted_weights.values()), 0.4)  # 应该低于40%集中度


if __name__ == '__main__':
    unittest.main()