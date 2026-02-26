#!/usr/bin/env python3
"""
Strategy Agent 单元测试
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from .factor_model import FactorModel
from .fund_scoring import FundScoringSystem
from .style_classification import StyleClassification


class TestStrategyAgent(unittest.TestCase):
    """Strategy Agent 测试类"""
    
    def setUp(self):
        """测试前准备"""
        # 创建测试数据
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
        
        self.test_fund_data = {
            'fund_code': '000001',
            'fund_name': '测试基金',
            'fund_type': '混合型',
            'fund_size': 50.0,
            'establish_date': '2020-01-01'
        }
        
        self.test_backtest_results = {
            'sharpe_ratio': 1.5,
            'max_drawdown': -0.2,
            'annual_return': 0.15,
            'volatility': 0.18
        }
    
    def test_factor_model(self):
        """测试因子模型"""
        factor_model = FactorModel()
        
        factors = factor_model.calculate_all_factors(
            '000001', self.test_fund_data, self.test_nav_data, self.test_backtest_results
        )
        
        self.assertIn('value', factors)
        self.assertIn('growth', factors)
        self.assertIn('momentum', factors)
        self.assertIn('quality', factors)
        
        # 检查因子值在合理范围内
        for factor_value in factors.values():
            self.assertGreaterEqual(factor_value, 0.0)
            self.assertLessEqual(factor_value, 1.0)
    
    def test_fund_scoring(self):
        """测试基金打分系统"""
        scoring_system = FundScoringSystem()
        
        score_result = scoring_system.score_single_fund(
            '000001', self.test_fund_data, self.test_nav_data, self.test_backtest_results
        )
        
        self.assertIn('composite_score', score_result)
        self.assertIn('factors', score_result)
        self.assertGreaterEqual(score_result['composite_score'], 0.0)
        self.assertLessEqual(score_result['composite_score'], 1.0)
    
    def test_style_classification(self):
        """测试风格分类"""
        factor_model = FactorModel()
        factors = factor_model.calculate_all_factors(
            '000001', self.test_fund_data, self.test_nav_data, self.test_backtest_results
        )
        
        classifier = StyleClassification()
        classification = classifier.classify_fund_comprehensive(
            '000001', self.test_fund_data, factors
        )
        
        self.assertIn('fund_type', classification)
        self.assertIn('market_cap_style', classification)
        self.assertIn('investment_style', classification)


if __name__ == '__main__':
    unittest.main()