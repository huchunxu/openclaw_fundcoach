#!/usr/bin/env python3
"""
DevOps Agent 单元测试
"""

import unittest
import os
import tempfile
from agents.devops_agent import DevOpsAgent

class TestDevOpsAgent(unittest.TestCase):
    
    def setUp(self):
        self.repo_path = os.path.dirname(os.path.abspath(__file__)) + '/../'
        self.agent = DevOpsAgent(self.repo_path)
    
    def test_run_unit_tests(self):
        """测试运行单元测试"""
        result = self.agent.run_unit_tests()
        # 由于环境限制，我们只验证返回格式
        self.assertIn('status', result)
        self.assertIn('message', result)
    
    def test_run_integration_test(self):
        """测试运行集成测试"""
        result = self.agent.run_integration_test()
        # 验证返回格式
        self.assertIn('status', result)
        self.assertIn('message', result)
    
    def test_run_backtest_comparison(self):
        """测试回测对比"""
        old_strategy = {
            'annual_return': 0.10,
            'sharpe_ratio': 0.8,
            'max_drawdown': -0.20,
            'volatility': 0.15
        }
        new_strategy = {
            'annual_return': 0.12,
            'sharpe_ratio': 0.9,
            'max_drawdown': -0.18,
            'volatility': 0.14
        }
        
        result = self.agent.run_backtest_comparison(old_strategy, new_strategy)
        
        self.assertIn('comparison', result)
        self.assertIn('improvements', result)
        self.assertIn('regressions', result)
        self.assertIn('is_improved', result)
        
        # 验证改进项
        self.assertTrue(len(result['improvements']) > 0)
        self.assertEqual(len(result['regressions']), 0)
        self.assertTrue(result['is_improved'])
    
    def test_generate_pr_description(self):
        """测试生成PR描述"""
        improvements = ["年化收益提升 2.00%", "夏普率提升 0.100"]
        regressions = ["最大回撤恶化 1.00%"]
        comparison = {
            'annual_return_change': 0.02,
            'sharpe_ratio_change': 0.1,
            'max_drawdown_change': -0.01,
            'volatility_change': 0.005
        }
        risk_assessment = "策略风险可控"
        
        description = self.agent.generate_pr_description(
            improvements, regressions, comparison, risk_assessment
        )
        
        self.assertIsInstance(description, str)
        self.assertIn("年化收益提升", description)
        self.assertIn("夏普率提升", description)
        self.assertIn("最大回撤恶化", description)
        self.assertIn("策略风险可控", description)

if __name__ == '__main__':
    unittest.main()