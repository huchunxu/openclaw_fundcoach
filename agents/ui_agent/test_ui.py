#!/usr/bin/env python3
"""
UI Agent 单元测试
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from .user_interface import UserInterface
from .visualization import VisualizationEngine
from .risk_disclosure import RiskDisclosureGenerator


class TestUIAgent(unittest.TestCase):
    """UI Agent 测试类"""
    
    def setUp(self):
        """测试前准备"""
        # 创建测试数据
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
        
        # 创建测试分析结果
        self.test_analysis_results = {
            'portfolio_results': {
                'annual_return': 0.15,
                'volatility': 0.18,
                'max_drawdown': -0.22,
                'sharpe_ratio': 1.2
            },
            'portfolio_weights': self.test_portfolio_weights,
            'factor_exposure': {
                'value': 0.6,
                'growth': 0.7,
                'momentum': 0.5,
                'quality': 0.8
            },
            'stress_test_results': {
                '2008_crisis_max_drawdown': -0.45,
                '2015_turbulence_max_drawdown': -0.32,
                '2020_pandemic_max_drawdown': -0.38
            },
            'sector_concentration': {
                'max_sector_concentration': 0.35,
                'herfindahl_index': 0.25
            }
        }
    
    def test_user_interface(self):
        """测试用户交互界面"""
        ui = UserInterface()
        
        # 测试模式切换
        self.assertTrue(ui.switch_mode('manual'))
        self.assertEqual(ui.mode, 'manual')
        self.assertTrue(ui.switch_mode('auto'))
        self.assertEqual(ui.mode, 'auto')
        self.assertFalse(ui.switch_mode('invalid'))
        
        # 测试基金代码处理
        fund_codes = ['000001', '000002', 'invalid', '123']
        validated_codes = ui.process_fund_input(fund_codes)
        self.assertEqual(len(validated_codes), 2)
        self.assertIn('000001', validated_codes)
        self.assertIn('000002', validated_codes)
        
        # 测试自动模式配置
        auto_config = ui.get_auto_mode_config()
        self.assertEqual(auto_config['mode'], 'auto')
        self.assertIn('risk_tolerance', auto_config)
        
        # 测试手动模式配置
        manual_config = ui.get_manual_mode_config(['000001', '000002'])
        self.assertEqual(manual_config['mode'], 'manual')
        self.assertEqual(len(manual_config['fund_codes']), 2)
        
        # 测试用户输入验证
        valid_input = {'mode': 'manual', 'fund_codes': ['000001']}
        is_valid, error_msg = ui.validate_user_input(valid_input)
        self.assertTrue(is_valid)
        
        invalid_input = {'mode': 'manual', 'fund_codes': []}
        is_valid, error_msg = ui.validate_user_input(invalid_input)
        self.assertFalse(is_valid)
    
    def test_visualization_engine(self):
        """测试可视化引擎"""
        viz = VisualizationEngine()
        
        # 测试风险收益图表
        risk_return_chart = viz.generate_risk_return_chart(
            self.test_analysis_results['portfolio_results']
        )
        self.assertIn('chart_type', risk_return_chart)
        self.assertEqual(risk_return_chart['chart_type'], 'risk_return_scatter')
        
        # 测试权重饼图
        weight_pie_chart = viz.generate_weight_pie_chart(self.test_portfolio_weights)
        self.assertIn('chart_type', weight_pie_chart)
        self.assertEqual(weight_pie_chart['chart_type'], 'pie')
        
        # 测试因子暴露热力图
        factor_heatmap = viz.generate_factor_exposure_heatmap(
            self.test_analysis_results['factor_exposure']
        )
        self.assertIn('chart_type', factor_heatmap)
        self.assertEqual(factor_heatmap['chart_type'], 'heatmap')
        
        # 测试压力测试对比
        stress_comparison = viz.generate_stress_test_comparison(
            self.test_analysis_results['stress_test_results']
        )
        self.assertIn('chart_type', stress_comparison)
        self.assertEqual(stress_comparison['chart_type'], 'bar')
        
        # 测试综合报告
        comprehensive_report = viz.generate_comprehensive_report(self.test_analysis_results)
        self.assertIn('risk_return_chart', comprehensive_report)
        self.assertIn('weight_pie_chart', comprehensive_report)
        self.assertIn('factor_exposure_heatmap', comprehensive_report)
        self.assertIn('stress_test_comparison', comprehensive_report)
    
    def test_risk_disclosure_generator(self):
        """测试风险提示生成器"""
        disclosure_gen = RiskDisclosureGenerator()
        
        # 测试风险等级评估
        risk_level = disclosure_gen.assess_risk_level(
            self.test_analysis_results['portfolio_results']
        )
        self.assertIn(risk_level, ['low', 'medium', 'high'])
        
        # 测试回撤警告
        drawdown_warning = disclosure_gen.generate_drawdown_warning(-0.22)
        self.assertIsInstance(drawdown_warning, str)
        self.assertGreater(len(drawdown_warning), 0)
        
        # 测试综合风险提示
        comprehensive_disclosure = disclosure_gen.generate_comprehensive_risk_disclosure(
            self.test_analysis_results
        )
        self.assertIsInstance(comprehensive_disclosure, str)
        self.assertGreater(len(comprehensive_disclosure), 100)
        
        # 测试合规性检查
        compliance_checks = disclosure_gen.validate_compliance(self.test_analysis_results)
        self.assertIn('has_risk_disclosure', compliance_checks)
        self.assertIn('concentration_within_limits', compliance_checks)
        
        # 测试投资者适当性提醒
        investor_profile = {'risk_tolerance': 'medium'}
        suitability_notice = disclosure_gen.generate_investor_suitability_notice(
            investor_profile, self.test_analysis_results
        )
        self.assertIsInstance(suitability_notice, str)
        self.assertGreater(len(suitability_notice), 0)


if __name__ == '__main__':
    unittest.main()