#!/usr/bin/env python3
"""
Risk Agent 单元测试
"""

import unittest
import numpy as np
from agents.risk_agent import RiskAgent

class TestRiskAgent(unittest.TestCase):
    
    def setUp(self):
        self.agent = RiskAgent()
        # 创建测试数据
        np.random.seed(42)
        self.portfolio_weights = {
            '000001': 0.4,
            '000002': 0.35,
            '000003': 0.25
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
    
    def test_calculate_portfolio_metrics(self):
        """测试组合风险指标计算"""
        metrics = self.agent.calculate_portfolio_metrics(self.portfolio_weights, self.fund_returns)
        
        self.assertIn('annual_return', metrics)
        self.assertIn('volatility', metrics)
        self.assertIn('sharpe_ratio', metrics)
        self.assertIn('max_drawdown', metrics)
        
        # 检查指标合理性
        self.assertGreaterEqual(metrics['annual_return'], -1.0)
        self.assertLessEqual(metrics['annual_return'], 1.0)
        self.assertGreaterEqual(metrics['volatility'], 0.0)
        self.assertLessEqual(metrics['volatility'], 1.0)
        self.assertGreaterEqual(metrics['max_drawdown'], -1.0)
        self.assertLessEqual(metrics['max_drawdown'], 0.0)
    
    def test_run_stress_test(self):
        """测试压力测试"""
        stress_results = self.agent.run_stress_test(self.portfolio_weights, self.fund_returns)
        
        expected_scenarios = ['market_crash', 'volatility_spike', 'liquidity_crisis', 'sector_rotation']
        for scenario in expected_scenarios:
            self.assertIn(scenario, stress_results)
            self.assertIn('description', stress_results[scenario])
    
    def test_analyze_risk_exposure(self):
        """测试风险暴露分析"""
        exposure = self.agent.analyze_risk_exposure(self.portfolio_weights, self.fund_styles)
        
        self.assertIn('style_exposure', exposure)
        self.assertIn('industry_concentration', exposure)
        self.assertIn('factor_exposure', exposure)
        
        # 检查风格暴露
        total_style_weight = sum(exposure['style_exposure'].values())
        self.assertAlmostEqual(total_style_weight, 1.0, places=10)
    
    def test_check_risk_limits(self):
        """测试风险限制检查"""
        # 创建一个高风险的测试场景
        risk_metrics = {
            'annual_return': 0.15,
            'volatility': 0.35,
            'sharpe_ratio': 0.4,
            'max_drawdown': -0.3
        }
        stress_results = {
            'market_crash': {'max_drawdown': -0.4}
        }
        
        risk_check = self.agent.check_risk_limits(risk_metrics, stress_results)
        
        self.assertIn('alerts', risk_check)
        self.assertIn('risk_level', risk_check)
        self.assertEqual(risk_check['risk_level'], 'high')
    
    def test_generate_risk_report(self):
        """测试风险报告生成"""
        fund_pool = {code: {'returns': returns} for code, returns in self.fund_returns.items()}
        strategy_results = {code: {'style': style} for code, style in self.fund_styles.items()}
        
        report = self.agent.generate_risk_report(self.portfolio_weights, fund_pool, strategy_results)
        
        self.assertIn('risk_metrics', report)
        self.assertIn('stress_test', report)
        self.assertIn('exposure_analysis', report)
        self.assertIn('risk_assessment', report)

if __name__ == '__main__':
    unittest.main()