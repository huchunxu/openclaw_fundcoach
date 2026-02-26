#!/usr/bin/env python3
"""
集成测试 - 验证所有Agent模块协同工作
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agents.data_backtest.fund_data import FundDataFetcher
from agents.data_backtest.backtest_engine import BacktestEngine
from agents.strategy_agent.factor_model import FactorModel
from agents.strategy_agent.fund_scoring import FundScoringSystem
from agents.strategy_agent.style_classification import StyleClassification
from agents.portfolio_agent.portfolio_generator import PortfolioGenerator
from agents.portfolio_agent.weight_optimizer import WeightOptimizer
from agents.risk_agent.stress_testing import StressTesting
from agents.risk_agent.risk_exposure import RiskExposureAnalyzer
from agents.risk_agent.drawdown_control import DrawdownController


class IntegrationTest(unittest.TestCase):
    """集成测试类"""
    
    def setUp(self):
        """测试前准备 - 创建完整的测试数据"""
        # 创建测试净值数据
        dates = pd.date_range(start='2023-01-01', end='2024-01-01', freq='D')
        np.random.seed(42)
        
        # 为不同基金创建略有差异的净值数据
        self.fund_nav_dict = {}
        fund_codes = ['000001', '000002', '000003', '000004', '000005']
        
        for i, fund_code in enumerate(fund_codes):
            # 每个基金有略微不同的收益和波动率
            base_return = 0.001 + i * 0.0001
            base_vol = 0.02 + i * 0.001
            
            returns = np.random.normal(base_return, base_vol, len(dates))
            nav = [1.0]
            for r in returns[1:]:
                nav.append(nav[-1] * (1 + r))
                
            self.fund_nav_dict[fund_code] = pd.DataFrame({
                'date': dates,
                'nav': nav
            })
        
        # 创建基金基本信息
        self.fund_basic_info = {}
        sectors = ['technology', 'healthcare', 'finance', 'consumer', 'energy']
        fund_types = ['混合型', '股票型', '混合型', '股票型', '混合型']
        sizes = [80.0, 120.0, 60.0, 90.0, 45.0]
        
        for i, fund_code in enumerate(fund_codes):
            self.fund_basic_info[fund_code] = {
                'fund_code': fund_code,
                'fund_name': f'测试基金{i+1}',
                'fund_type': fund_types[i],
                'fund_size': sizes[i],
                'establish_date': '2020-01-01',
                'sector': sectors[i]
            }
    
    def test_end_to_end_workflow(self):
        """端到端工作流测试"""
        print("开始端到端集成测试...")
        
        # 1. Data Agent - 获取基金数据和回测结果
        print("1. 测试Data Agent...")
        backtest_engine = BacktestEngine()
        fund_backtest_results = {}
        
        for fund_code, nav_data in self.fund_nav_dict.items():
            results = backtest_engine.backtest_single_fund(fund_code, nav_data)
            fund_backtest_results[fund_code] = results
        
        # 验证回测结果
        self.assertEqual(len(fund_backtest_results), 5)
        for fund_code, results in fund_backtest_results.items():
            self.assertIn('annual_return', results)
            self.assertIn('sharpe_ratio', results)
            self.assertIn('max_drawdown', results)
            self.assertIn('volatility', results)
        
        print("✅ Data Agent测试通过")
        
        # 2. Strategy Agent - 因子建模和基金打分
        print("2. 测试Strategy Agent...")
        factor_model = FactorModel()
        scoring_system = FundScoringSystem()
        style_classifier = StyleClassification()
        
        # 计算因子和打分
        fund_scores_data = []
        fund_factors_dict = {}
        fund_styles_dict = {}
        
        for fund_code in self.fund_nav_dict.keys():
            # 计算因子
            factors = factor_model.calculate_all_factors(
                fund_code,
                self.fund_basic_info[fund_code],
                self.fund_nav_dict[fund_code],
                fund_backtest_results[fund_code]
            )
            fund_factors_dict[fund_code] = factors
            
            # 计算综合评分
            score_result = scoring_system.score_single_fund(
                fund_code,
                self.fund_basic_info[fund_code],
                self.fund_nav_dict[fund_code],
                fund_backtest_results[fund_code]
            )
            
            # 风格分类
            style_result = style_classifier.classify_fund_comprehensive(
                fund_code,
                self.fund_basic_info[fund_code],
                factors
            )
            fund_styles_dict[fund_code] = style_result
            
            fund_scores_data.append({
                'fund_code': fund_code,
                'composite_score': score_result['composite_score'],
                'investment_style': style_result['investment_style']
            })
        
        fund_scores_df = pd.DataFrame(fund_scores_data)
        
        # 验证打分结果
        self.assertEqual(len(fund_scores_df), 5)
        self.assertTrue(all(fund_scores_df['composite_score'] >= 0))
        self.assertTrue(all(fund_scores_df['composite_score'] <= 1))
        
        print("✅ Strategy Agent测试通过")
        
        # 3. Portfolio Agent - 组合生成和优化
        print("3. 测试Portfolio Agent...")
        portfolio_generator = PortfolioGenerator()
        weight_optimizer = WeightOptimizer()
        
        # 生成Top-N组合
        top_n_portfolio = portfolio_generator.generate_top_n_portfolio(fund_scores_df, n=3)
        
        # 权重优化
        optimized_weights = weight_optimizer.optimize_portfolio_weights(
            fund_scores_df, self.fund_nav_dict, 'risk_parity'
        )
        
        # 验证组合权重
        self.assertEqual(len(top_n_portfolio), 3)
        self.assertAlmostEqual(sum(top_n_portfolio.values()), 1.0, places=6)
        self.assertGreater(len(optimized_weights), 0)
        self.assertAlmostEqual(sum(optimized_weights.values()), 1.0, places=6)
        
        print("✅ Portfolio Agent测试通过")
        
        # 4. Risk Agent - 风险分析和控制
        print("4. 测试Risk Agent...")
        stress_tester = StressTesting()
        risk_analyzer = RiskExposureAnalyzer()
        drawdown_controller = DrawdownController()
        
        # 构建组合净值用于风险测试
        portfolio_weights = optimized_weights
        all_dates = None
        for nav_data in self.fund_nav_dict.values():
            if all_dates is None:
                all_dates = set(nav_data['date'])
            else:
                all_dates = all_dates.intersection(set(nav_data['date']))
        
        all_dates = sorted(list(all_dates))
        portfolio_nav = []
        
        for date in all_dates:
            weighted_nav = 0.0
            total_weight = 0.0
            
            for fund_code, weight in portfolio_weights.items():
                if fund_code not in self.fund_nav_dict:
                    continue
                    
                nav_data = self.fund_nav_dict[fund_code]
                nav_on_date = nav_data[nav_data['date'] == date]
                
                if not nav_on_date.empty:
                    weighted_nav += weight * nav_on_date['nav'].iloc[0]
                    total_weight += weight
                    
            if total_weight > 0:
                normalized_nav = weighted_nav / total_weight
                portfolio_nav.append(normalized_nav)
        
        portfolio_nav_series = pd.Series(portfolio_nav, index=all_dates)
        
        # 压力测试
        stress_results = stress_tester.run_comprehensive_stress_test(portfolio_nav_series)
        self.assertIn('2008_crisis_max_drawdown', stress_results)
        self.assertIn('monte_carlo', stress_results)
        
        # 风险暴露分析
        fund_sectors = {code: info['sector'] for code, info in self.fund_basic_info.items()}
        exposure_results = risk_analyzer.comprehensive_risk_exposure_analysis(
            portfolio_weights,
            fund_factors_dict,
            fund_sectors,
            self.fund_nav_dict
        )
        self.assertIn('factor_exposure', exposure_results)
        self.assertIn('sector_concentration', exposure_results)
        self.assertIn('correlation_risk', exposure_results)
        
        # 回撤控制
        drawdown_status = drawdown_controller.detect_drawdown_breaches(portfolio_nav_series)
        self.assertIn('current_drawdown', drawdown_status)
        self.assertIn('is_warning_breached', drawdown_status)
        self.assertIn('is_limit_breached', drawdown_status)
        
        print("✅ Risk Agent测试通过")
        
        # 5. 完整工作流验证
        print("5. 验证完整工作流...")
        final_portfolio_report = {
            'portfolio_weights': portfolio_weights,
            'expected_annual_return': sum(
                fund_backtest_results[code]['annual_return'] * weight 
                for code, weight in portfolio_weights.items() 
                if code in fund_backtest_results
            ),
            'stress_test_results': stress_results,
            'risk_exposure_analysis': exposure_results,
            'drawdown_status': drawdown_status
        }
        
        # 验证报告完整性
        self.assertIn('portfolio_weights', final_portfolio_report)
        self.assertIn('expected_annual_return', final_portfolio_report)
        self.assertIn('stress_test_results', final_portfolio_report)
        self.assertIn('risk_exposure_analysis', final_portfolio_report)
        self.assertIn('drawdown_status', final_portfolio_report)
        
        print("✅ 完整工作流验证通过")
        print("🎉 端到端集成测试全部通过！")
    
    def test_error_handling(self):
        """错误处理测试"""
        print("测试错误处理...")
        
        # 测试空数据输入
        empty_df = pd.DataFrame()
        backtest_engine = BacktestEngine()
        empty_results = backtest_engine.backtest_single_fund('000000', empty_df)
        self.assertEqual(empty_results, {})
        
        print("✅ 错误处理测试通过")


if __name__ == '__main__':
    # 运行集成测试
    unittest.main(verbosity=2)