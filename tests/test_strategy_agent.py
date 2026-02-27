#!/usr/bin/env python3
"""
Strategy Agent 单元测试
"""

import unittest
import numpy as np
from agents.strategy_agent import StrategyAgent

class TestStrategyAgent(unittest.TestCase):
    
    def setUp(self):
        self.agent = StrategyAgent()
        # 创建测试数据
        np.random.seed(42)
        self.test_returns = np.random.normal(0.001, 0.02, 500).tolist()
        self.fund_data = {'returns': self.test_returns}
    
    def test_calculate_factors(self):
        """测试因子计算"""
        factors = self.agent.calculate_factors(self.fund_data)
        
        self.assertIn('return_1y', factors)
        self.assertIn('sharpe_ratio', factors)
        self.assertIn('max_drawdown', factors)
        self.assertIn('volatility', factors)
        self.assertIn('consistency', factors)
        
        # 检查因子值的合理性
        self.assertGreaterEqual(factors['return_1y'], -1.0)
        self.assertLessEqual(factors['return_1y'], 1.0)
        self.assertGreaterEqual(factors['sharpe_ratio'], -5.0)
        self.assertLessEqual(factors['sharpe_ratio'], 5.0)
        self.assertGreaterEqual(factors['max_drawdown'], -1.0)
        self.assertLessEqual(factors['max_drawdown'], 0.0)
    
    def test_score_fund(self):
        """测试基金打分"""
        factors = self.agent.calculate_factors(self.fund_data)
        score = self.agent.score_fund(factors)
        
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)
    
    def test_classify_style(self):
        """测试风格分类"""
        style = self.agent.classify_style(self.fund_data)
        self.assertIn(style, ['aggressive_growth', 'balanced', 'conservative', 'mixed'])
    
    def test_analyze_fund_pool(self):
        """测试基金池分析"""
        fund_pool = {
            '000001': self.fund_data,
            '000002': {'returns': np.random.normal(0.002, 0.015, 500).tolist()}
        }
        
        results = self.agent.analyze_fund_pool(fund_pool)
        
        self.assertEqual(len(results), 2)
        for fund_code, result in results.items():
            self.assertIn('factors', result)
            self.assertIn('score', result)
            self.assertIn('style', result)

if __name__ == '__main__':
    unittest.main()