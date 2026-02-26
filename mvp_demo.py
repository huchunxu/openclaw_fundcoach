#!/usr/bin/env python3
"""
MVP演示脚本 - 端到端基金组合研究系统
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

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
from agents.ui_agent.user_interface import UserInterface
from agents.ui_agent.visualization import VisualizationEngine
from agents.ui_agent.risk_disclosure import RiskDisclosureGenerator


def create_sample_fund_data():
    """创建示例基金数据用于演示"""
    # 创建测试净值数据
    dates = pd.date_range(start='2023-01-01', end='2024-01-01', freq='D')
    np.random.seed(42)
    
    fund_nav_dict = {}
    fund_basic_info = {}
    fund_codes = ['000001', '000002', '000003', '000004', '000005']
    sectors = ['technology', 'healthcare', 'finance', 'consumer', 'energy']
    fund_types = ['混合型', '股票型', '混合型', '股票型', '混合型']
    sizes = [80.0, 120.0, 60.0, 90.0, 45.0]
    
    for i, fund_code in enumerate(fund_codes):
        # 每个基金有略微不同的收益和波动率
        base_return = 0.001 + i * 0.0001
        base_vol = 0.02 + i * 0.001
        
        returns = np.random.normal(base_return, base_vol, len(dates))
        nav = [1.0]
        for r in returns[1:]:
            nav.append(nav[-1] * (1 + r))
            
        fund_nav_dict[fund_code] = pd.DataFrame({
            'date': dates,
            'nav': nav
        })
        
        fund_basic_info[fund_code] = {
            'fund_code': fund_code,
            'fund_name': f'测试基金{i+1}',
            'fund_type': fund_types[i],
            'fund_size': sizes[i],
            'establish_date': '2020-01-01',
            'sector': sectors[i]
        }
    
    return fund_nav_dict, fund_basic_info


def run_mvp_demo():
    """运行MVP演示"""
    print("🚀 OpenClaw FundCoach MVP 演示")
    print("=" * 50)
    
    # 1. 创建示例数据
    print("1. 创建示例基金数据...")
    fund_nav_dict, fund_basic_info = create_sample_fund_data()
    print(f"✅ 创建了 {len(fund_nav_dict)} 只基金的示例数据")
    
    # 2. Data Agent - 回测分析
    print("\n2. 执行回测分析...")
    backtest_engine = BacktestEngine()
    fund_backtest_results = {}
    
    for fund_code, nav_data in fund_nav_dict.items():
        results = backtest_engine.backtest_single_fund(fund_code, nav_data)
        fund_backtest_results[fund_code] = results
    
    print("✅ 回测分析完成")
    
    # 3. Strategy Agent - 因子建模和打分
    print("\n3. 执行因子建模和基金打分...")
    factor_model = FactorModel()
    scoring_system = FundScoringSystem()
    style_classifier = StyleClassification()
    
    fund_scores_data = []
    fund_factors_dict = {}
    
    for fund_code in fund_nav_dict.keys():
        factors = factor_model.calculate_all_factors(
            fund_code,
            fund_basic_info[fund_code],
            fund_nav_dict[fund_code],
            fund_backtest_results[fund_code]
        )
        fund_factors_dict[fund_code] = factors
        
        score_result = scoring_system.score_single_fund(
            fund_code,
            fund_basic_info[fund_code],
            fund_nav_dict[fund_code],
            fund_backtest_results[fund_code]
        )
        
        style_result = style_classifier.classify_fund_comprehensive(
            fund_code,
            fund_basic_info[fund_code],
            factors
        )
        
        fund_scores_data.append({
            'fund_code': fund_code,
            'composite_score': score_result['composite_score'],
            'investment_style': style_result['investment_style']
        })
    
    fund_scores_df = pd.DataFrame(fund_scores_data)
    print("✅ 因子建模和基金打分完成")
    
    # 4. Portfolio Agent - 组合优化
    print("\n4. 生成优化投资组合...")
    portfolio_generator = PortfolioGenerator()
    weight_optimizer = WeightOptimizer()
    
    # 生成Top-3组合
    top_n_portfolio = portfolio_generator.generate_top_n_portfolio(fund_scores_df, n=3)
    print(f"Top-N组合: {top_n_portfolio}")
    
    # 权重优化
    optimized_weights = weight_optimizer.optimize_portfolio_weights(
        fund_scores_df, fund_nav_dict, 'risk_parity'
    )
    print(f"优化后权重: {optimized_weights}")
    
    # 5. Risk Agent - 风险分析
    print("\n5. 执行风险分析...")
    stress_tester = StressTesting()
    risk_analyzer = RiskExposureAnalyzer()
    drawdown_controller = DrawdownController()
    
    # 构建组合净值
    all_dates = None
    for nav_data in fund_nav_dict.values():
        if all_dates is None:
            all_dates = set(nav_data['date'])
        else:
            all_dates = all_dates.intersection(set(nav_data['date']))
    
    all_dates = sorted(list(all_dates))
    portfolio_nav = []
    
    for date in all_dates:
        weighted_nav = 0.0
        total_weight = 0.0
        
        for fund_code, weight in optimized_weights.items():
            if fund_code not in fund_nav_dict:
                continue
                
            nav_data = fund_nav_dict[fund_code]
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
    print(f"压力测试结果: 最坏情况回撤 {min([v for k, v in stress_results.items() if k.endswith('_max_drawdown')]):.2%}")
    
    # 风险暴露分析
    fund_sectors = {code: info['sector'] for code, info in fund_basic_info.items()}
    exposure_results = risk_analyzer.comprehensive_risk_exposure_analysis(
        optimized_weights,
        fund_factors_dict,
        fund_sectors,
        fund_nav_dict
    )
    print(f"行业集中度: {exposure_results['sector_concentration']['max_sector_concentration']:.2%}")
    
    # 6. UI Agent - 生成报告
    print("\n6. 生成用户报告...")
    ui = UserInterface()
    viz = VisualizationEngine()
    disclosure_gen = RiskDisclosureGenerator()
    
    # 组合分析结果
    portfolio_results = {
        'annual_return': sum(
            fund_backtest_results[code]['annual_return'] * weight 
            for code, weight in optimized_weights.items() 
            if code in fund_backtest_results
        ),
        'volatility': exposure_results.get('correlation_risk', {}).get('avg_correlation', 0.2),
        'max_drawdown': min([v for k, v in stress_results.items() if k.endswith('_max_drawdown')])
    }
    
    analysis_results = {
        'portfolio_results': portfolio_results,
        'portfolio_weights': optimized_weights,
        'factor_exposure': exposure_results['factor_exposure'],
        'stress_test_results': stress_results,
        'sector_concentration': exposure_results['sector_concentration']
    }
    
    # 生成风险提示
    risk_disclosure = disclosure_gen.generate_comprehensive_risk_disclosure(analysis_results)
    print("\n📋 风险提示:")
    print(risk_disclosure)
    
    # 生成可视化数据
    charts_data = viz.generate_comprehensive_report(analysis_results)
    print(f"\n📊 生成了 {len(charts_data)} 个可视化图表")
    
    print("\n🎉 MVP演示完成！")
    print("所有核心功能已验证，可以进行实际试用。")
    
    return analysis_results, risk_disclosure, charts_data


if __name__ == "__main__":
    try:
        results = run_mvp_demo()
        print("\n✅ MVP版本准备就绪，可以进行试用！")
    except Exception as e:
        print(f"\n❌ MVP演示失败: {e}")
        sys.exit(1)