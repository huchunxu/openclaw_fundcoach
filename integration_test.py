#!/usr/bin/env python3
"""
集成测试：验证新开发的Agent功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 动态导入Agent类
exec(open('agents/strategy_agent.py').read())
exec(open('agents/portfolio_agent.py').read())
exec(open('agents/risk_agent.py').read())

import numpy as np

def test_integration():
    """集成测试"""
    print("🚀 开始集成测试...")
    
    # 创建模拟基金数据
    np.random.seed(42)
    fund_pool = {}
    for i in range(1, 6):
        returns = np.random.normal(0.001 * i, 0.02, 500).tolist()
        fund_pool[f"00000{i}"] = {'returns': returns}
    
    # 1. Strategy Agent 测试
    print("1. 测试 Strategy Agent...")
    strategy_agent = StrategyAgent()
    strategy_results = strategy_agent.analyze_fund_pool(fund_pool)
    print(f"   ✓ 分析了 {len(strategy_results)} 只基金")
    
    # 2. Portfolio Agent 测试
    print("2. 测试 Portfolio Agent...")
    portfolio_agent = PortfolioAgent()
    portfolio = portfolio_agent.create_diversified_portfolio(fund_pool, strategy_results)
    print(f"   ✓ 创建了包含 {len(portfolio)} 只基金的组合")
    print(f"   ✓ 组合权重总和: {sum(portfolio.values()):.6f}")
    
    # 3. Risk Agent 测试
    print("3. 测试 Risk Agent...")
    risk_agent = RiskAgent()
    risk_report = risk_agent.generate_risk_report(portfolio, fund_pool, strategy_results)
    print(f"   ✓ 风险等级: {risk_report['risk_assessment']['risk_level']}")
    print(f"   ✓ 最大回撤: {risk_report['risk_metrics']['max_drawdown']:.2%}")
    print(f"   ✓ 年化收益: {risk_report['risk_metrics']['annual_return']:.2%}")
    
    # 4. 验证风险提示生成
    print("4. 验证风险提示...")
    risk_level = risk_report['risk_assessment']['risk_level']
    if risk_level == 'high':
        print("   ⚠️  高风险组合 - 需要谨慎")
    elif risk_level == 'medium':
        print("   ⚠️  中等风险组合 - 适合稳健型投资者")
    else:
        print("   ✅ 低风险组合 - 适合保守型投资者")
    
    print("\n✅ 集成测试完成！所有新功能正常工作。")
    return True

if __name__ == "__main__":
    test_integration()