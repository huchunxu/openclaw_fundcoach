#!/usr/bin/env python3
"""
测试所有增强模块集成
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

from agents.strategy_agent.factor_model_enhanced import EnhancedFactorModel
from agents.strategy_agent.fund_scoring_enhanced import EnhancedFundScoringSystem
from agents.portfolio_agent.portfolio_generator_enhanced import EnhancedPortfolioGenerator
from agents.portfolio_agent.weight_optimizer_enhanced import EnhancedWeightOptimizer
from agents.risk_agent.stress_testing_enhanced import EnhancedStressTesting
from agents.risk_agent.risk_exposure_enhanced import EnhancedRiskExposureAnalyzer


def create_test_data():
    """创建测试数据"""
    # 创建测试净值数据（1年）
    dates = pd.date_range(start='2023-01-01', end='2024-01-01', freq='D')
    np.random.seed(42)
    
    # 模拟一个表现良好的基金
    base_return = 0.0015  # 日均收益0.15%
    base_vol = 0.018      # 日波动率1.8%
    
    returns = np.random.normal(base_return, base_vol, len(dates))
    nav = [1.0]
    for r in returns[1:]:
        nav.append(nav[-1] * (1 + r))
    
    nav_data = pd.DataFrame({
        'date': dates,
        'nav': nav
    })
    
    fund_data = {
        'fund_code': '000001',
        'fund_name': '测试基金',
        'fund_type': '混合型',
        'fund_size': 80.0,  # 80亿
        'establish_date': '2020-01-01',
        'sector': 'technology'
    }
    
    # 模拟回测结果
    backtest_results = {
        'annual_return': 0.18,      # 年化收益18%
        'volatility': 0.15,         # 年化波动率15%
        'sharpe_ratio': 1.8,        # 夏普率1.8
        'max_drawdown': -0.15,      # 最大回撤-15%
        'avg_drawdown': -0.08,      # 平均回撤-8%
        'sortino_ratio': 2.2,       # 索提诺比率2.2
        'calmar_ratio': 1.2,        # 卡玛比率1.2
        'avg_recovery_days': 90     # 平均恢复时间90天
    }
    
    return nav_data, fund_data, backtest_results


def test_enhanced_strategy():
    """测试增强策略代理"""
    print("1. 测试Enhanced Strategy Agent...")
    
    nav_data, fund_data, backtest_results = create_test_data()
    
    # 测试因子模型
    factor_model = EnhancedFactorModel()
    factors = factor_model.calculate_all_factors(
        '000001', fund_data, nav_data, backtest_results
    )
    
    print(f"   ✅ 计算得到 {len(factors)} 个增强因子")
    
    # 测试打分系统
    scoring_system = EnhancedFundScoringSystem()
    score_result = scoring_system.score_single_fund_enhanced(
        '000001', fund_data, nav_data, backtest_results
    )
    
    print(f"   ✅ 基金综合评分: {score_result['composite_score']:.4f}")
    
    return factors, score_result


def test_enhanced_portfolio():
    """测试增强组合代理"""
    print("2. 测试Enhanced Portfolio Agent...")
    
    # 创建多只基金数据
    fund_codes = ['000001', '000002', '000003']
    fund_scores_data = []
    fund_nav_dict = {}
    fund_basic_info = {}
    fund_backtest_results = {}
    
    for i, fund_code in enumerate(fund_codes):
        nav_data, fund_data, backtest_results = create_test_data()
        # 微调不同基金的参数
        fund_data['fund_code'] = fund_code
        fund_data['fund_size'] = 50.0 + i * 20.0
        backtest_results['annual_return'] = 0.15 + i * 0.02
        
        fund_scores_data.append({
            'fund_code': fund_code,
            'composite_score': 0.6 + i * 0.1,
            'investment_style': 'balanced'
        })
        
        fund_nav_dict[fund_code] = nav_data
        fund_basic_info[fund_code] = fund_data
        fund_backtest_results[fund_code] = backtest_results
    
    fund_scores_df = pd.DataFrame(fund_scores_data)
    
    # 测试组合生成
    portfolio_generator = EnhancedPortfolioGenerator()
    top_n_portfolio = portfolio_generator.generate_top_n_portfolio(fund_scores_df, n=2)
    print(f"   ✅ Top-N组合: {len(top_n_portfolio)} 只基金")
    
    # 测试权重优化
    weight_optimizer = EnhancedWeightOptimizer()
    optimized_weights = weight_optimizer.optimize_portfolio_weights_enhanced(
        fund_scores_df, fund_nav_dict, 'enhanced_risk_parity'
    )
    print(f"   ✅ 优化后权重: {len(optimized_weights)} 只基金")
    
    return top_n_portfolio, optimized_weights


def test_enhanced_risk():
    """测试增强风险代理"""
    print("3. 测试Enhanced Risk Agent...")
    
    # 创建组合净值
    dates = pd.date_range(start='2023-01-01', end='2024-01-01', freq='D')
    np.random.seed(42)
    returns = np.random.normal(0.001, 0.02, len(dates))
    nav = [1.0]
    for r in returns[1:]:
        nav.append(nav[-1] * (1 + r))
    
    portfolio_nav = pd.Series(nav, index=dates)
    
    # 测试压力测试
    stress_tester = EnhancedStressTesting()
    stress_results = stress_tester.run_comprehensive_stress_test(portfolio_nav)
    print(f"   ✅ 压力测试场景数: {len([k for k in stress_results.keys() if k.endswith('_max_drawdown')])}")
    
    # 测试风险暴露分析
    portfolio_weights = {'000001': 0.4, '000002': 0.3, '000003': 0.3}
    fund_factors = {
        '000001': {'value': 0.8, 'growth': 0.6},
        '000002': {'value': 0.5, 'growth': 0.8},
        '000003': {'value': 0.7, 'growth': 0.7}
    }
    fund_sectors = {'000001': 'tech', '000002': 'healthcare', '000003': 'finance'}
    fund_nav_dict = {}
    for code in portfolio_weights.keys():
        nav_data, _, _ = create_test_data()
        fund_nav_dict[code] = nav_data
    
    risk_analyzer = EnhancedRiskExposureAnalyzer()
    exposure_results = risk_analyzer.comprehensive_risk_exposure_analysis(
        portfolio_weights, fund_factors, fund_sectors, fund_nav_dict
    )
    print(f"   ✅ 风险暴露分析完成，行业集中度: {exposure_results['sector_concentration']['max_sector_concentration']:.2%}")
    
    return stress_results, exposure_results


def main():
    """主测试函数"""
    print("🧪 测试所有增强模块集成")
    print("=" * 50)
    
    try:
        # 测试策略代理
        factors, score_result = test_enhanced_strategy()
        
        # 测试组合代理
        top_n_portfolio, optimized_weights = test_enhanced_portfolio()
        
        # 测试风险代理
        stress_results, exposure_results = test_enhanced_risk()
        
        print("\n✅ 所有增强模块测试通过！")
        print("增强功能已准备就绪，可以合并到master分支。")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)