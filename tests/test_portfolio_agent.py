#!/usr/bin/env python3
"""
Portfolio Agent 单元测试
"""

import unittest
import numpy as np
from agents.portfolio_agent import PortfolioAgent

class TestPortfolioAgent(unittest.TestCase):
    
    def setUp(self):
        self.agent = PortfolioAgent()
        # 创建测试数据
        np.random.seed(42)
        self.fund_scores = {
            '000001': 0.85,
            '000002': 0.72,
            '000003': 0.91,
            '000004': 0.68,
            '000005': 0.79
        }
        self.fund_returns = {
            '000001': np.random.normal(0.001, 0.02, 500).tolist(),
            '000002': np.random.normal(0.002, 0.015, 500).tolist(),
            '000003': np.random.normal(0.0015, 0.018, 500).tolist()
        }
        self.fund_styles = {
            '000001': 'balanced',
            '000002': 'conservative', 
            '000003': 'aggressive_growth'
        }
    
    def test_generate_top_n_portfolio(self):
        """测试Top-N组合生成"""
        weights = self.agent.generate_top_n_portfolio(self.fund_scores, n=3)
        
        self.assertEqual(len(weights), 3)
        self.assertAlmostEqual(sum(weights.values()), 1.0, places=10)
        
        # 检查是否选择了得分最高的基金
        top_codes = sorted(self.fund_scores.items(), key=lambda x: x[1], reverse=True)[:3]
        expected_codes = [code for code, score in top_codes]
        self.assertEqual(set(weights.keys()), set(expected_codes))
    
    def test_optimize_weights(self):
        """测试权重优化"""
        weights = self.agent.optimize_weights(self.fund_returns)
        
        self.assertEqual(len(weights), len(self.fund_returns))
        self.assertAlmostEqual(sum(weights.values()), 1.0, places=10)
        
        # 检查权重非负
        for weight in weights.values():
            self.assertGreaterEqual(weight, 0.0)
    
    def test_balance_risk(self):
        """测试风险平衡"""
        initial_weights = {'000001': 0.6, '000002': 0.4}
        balanced_weights = self.agent.balance_risk(initial_weights, self.fund_styles)
        
        self.assertAlmostEqual(sum(balanced_weights.values()), 1.0, places=10)
    
    def test_create_diversified_portfolio(self):
        """测试多元化组合创建"""
        # 创建模拟的fund_pool和strategy_results
        fund_pool = {code: {'returns': returns} for code, returns in self.fund_returns.items()}
        strategy_results = {}
        for code in self.fund_returns.keys():
            strategy_results[code] = {
                'score': self.fund_scores.get(code, 0.5),
                'style': self.fund_styles.get(code, 'mixed')
            }
        
        portfolio = self.agent.create_diversified_portfolio(fund_pool, strategy_results)
        
        self.assertEqual(len(portfolio), len(fund_pool))
        self.assertAlmostEqual(sum(portfolio.values()), 1.0, places=10)

if __name__ == '__main__':
    unittest.main()