#!/usr/bin/env python3
"""
Risk Agent 单元测试
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from .stress_testing import StressTesting
from .risk_exposure import RiskExposureAnalyzer
from .drawdown_control import DrawdownController


class TestRiskAgent(unittest.TestCase):
    """Risk Agent 测试类"""
    
    def setUp(self):
        """测试前准备"""
        # 创建测试净值数据
        dates = pd.date_range(start='2023-01-01', end='2024-01-01', freq='D')
        np.random.seed(42)
        returns = np.random.normal(0.001, 0.02, len(dates))
        nav = [1.0]
        for r in returns[1:]:
            nav.append(nav[-1] * (1 + r))
            
        self.test_nav_series = pd.Series(nav, index=dates)
        
        # 创建测试组合权重
        self.test_portfolio_weights = {
            '000001': 0.4,
            '000002': 0.3,
            '000003': 0.3
        }
        
        # 创建测试基金因子数据
        self.test_fund_factors = {
            '000001': {'value': 0.8, 'growth': 0.6, 'momentum': 0.7, 'quality': 0.9},
            '000002': {'value': 0.5, 'growth': 0.9, 'momentum': 0.8, 'quality': 0.7},
            '000003': {'value': 0.7, 'growth': 0.7, 'momentum': 0.6, 'quality': 0.8}
        }
        
        # 创建测试基金行业数据
        self.test_fund_sectors = {
            '000001': 'technology',
            '000002': 'healthcare', 
            '000003': 'finance'
        }
        
        # 创建测试净值字典
        self.test_fund_nav_dict = {
            '000001': pd.DataFrame({'date': dates, 'nav': nav}),
            '000002': pd.DataFrame({'date': dates, 'nav': nav}),
            '000003': pd.DataFrame({'date': dates, 'nav': nav})
        }
    
    def test_stress_testing(self):
        """测试压力测试"""
        stress_tester = StressTesting()
        
        # 测试历史场景应用
        stressed_nav = stress_tester.apply_historical_scenario(self.test_nav_series, '2008_crisis')
        self.assertEqual(len(stressed_nav), len(self.test_nav_series))
        self.assertLess(stressed_nav.iloc[-1], self.test_nav_series.iloc[-1])
        
        # 测试蒙特卡洛模拟
        mc_results = stress_tester.monte_carlo_simulation(self.test_nav_series, num_simulations=10)
        self.assertIn('var_95', mc_results)
        self.assertIn('var_99', mc_results)
        
        # 测试综合压力测试
        comprehensive_results = stress_tester.run_comprehensive_stress_test(self.test_nav_series)
        self.assertIn('2008_crisis_max_drawdown', comprehensive_results)
        self.assertIn('monte_carlo', comprehensive_results)
    
    def test_risk_exposure_analysis(self):
        """测试风险暴露分析"""
        analyzer = RiskExposureAnalyzer()
        
        # 测试因子暴露分析
        factor_exposure = analyzer.analyze_factor_exposure(
            self.test_portfolio_weights, self.test_fund_factors
        )
        self.assertIn('value', factor_exposure)
        self.assertIn('growth', factor_exposure)
        
        # 测试行业集中度分析
        sector_concentration = analyzer.analyze_sector_concentration(
            self.test_portfolio_weights, self.test_fund_sectors
        )
        self.assertIn('herfindahl_index', sector_concentration)
        self.assertIn('max_sector_concentration', sector_concentration)
        
        # 测试相关性风险分析
        correlation_risk = analyzer.analyze_correlation_risk(self.test_fund_nav_dict)
        self.assertIn('avg_correlation', correlation_risk)
        self.assertIn('max_correlation', correlation_risk)
        
        # 测试综合风险暴露分析
        comprehensive_analysis = analyzer.comprehensive_risk_exposure_analysis(
            self.test_portfolio_weights,
            self.test_fund_factors,
            self.test_fund_sectors,
            self.test_fund_nav_dict
        )
        self.assertIn('factor_exposure', comprehensive_analysis)
        self.assertIn('sector_concentration', comprehensive_analysis)
        self.assertIn('correlation_risk', comprehensive_analysis)
    
    def test_drawdown_control(self):
        """测试回撤控制"""
        controller = DrawdownController()
        
        # 测试当前回撤计算
        current_dd = controller.calculate_current_drawdown(self.test_nav_series)
        self.assertLessEqual(current_dd, 0.0)
        
        # 测试回撤突破检测
        breach_status = controller.detect_drawdown_breaches(self.test_nav_series)
        self.assertIn('current_drawdown', breach_status)
        self.assertIn('is_warning_breached', breach_status)
        self.assertIn('is_limit_breached', breach_status)
        
        # 测试风险信号生成
        risk_signals = controller.generate_risk_signals(self.test_nav_series)
        self.assertIn('warning_signal', risk_signals)
        self.assertIn('stop_loss_signal', risk_signals)
        
        # 测试动态风险预算
        fund_risk_scores = {'000001': 0.8, '000002': 0.6, '000003': 0.7}
        adjusted_weights = controller.dynamic_risk_budgeting(
            self.test_portfolio_weights, fund_risk_scores
        )
        self.assertAlmostEqual(sum(adjusted_weights.values()), 1.0, places=6)


if __name__ == '__main__':
    unittest.main()