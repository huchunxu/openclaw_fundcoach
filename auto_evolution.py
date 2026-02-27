#!/usr/bin/env python3
"""
自动进化流程 - 触发DevOps Agent进行策略优化
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.devops_agent import DevOpsAgent

def main():
    """主函数：运行自动进化流程"""
    print("🚀 启动自动进化流程...")
    
    # 初始化DevOps Agent
    devops_agent = DevOpsAgent(".")
    
    # 模拟策略改进数据（在实际应用中，这会来自Strategy Agent的优化结果）
    strategy_improvement = {
        'old_metrics': {
            'annual_return': 0.08,
            'sharpe_ratio': 0.7,
            'max_drawdown': -0.25,
            'volatility': 0.18
        },
        'new_metrics': {
            'annual_return': 0.11,
            'sharpe_ratio': 0.85,
            'max_drawdown': -0.20,
            'volatility': 0.16
        }
    }
    
    # 运行完整的DevOps流水线
    results = devops_agent.run_full_pipeline(strategy_improvement)
    
    # 输出结果摘要
    print("\n📊 自动进化流程结果:")
    print(f"单元测试: {results['unit_tests']['status']}")
    print(f"集成测试: {results['integration_tests']['status']}")
    
    if 'backtest_comparison' in results:
        comparison = results['backtest_comparison']
        if isinstance(comparison, dict) and comparison.get('status') != 'skipped':
            print(f"回测对比: {'✅ 改进' if comparison['is_improved'] else '❌ 退步'}")
            if comparison['improvements']:
                print("改进项:")
                for imp in comparison['improvements']:
                    print(f"  - {imp}")
            if comparison['regressions']:
                print("退步项:")
                for reg in comparison['regressions']:
                    print(f"  - {reg}")
    
    if 'create_pr' in results:
        print(f"Pull Request: {results['create_pr']['message']}")
    elif results['unit_tests']['status'] == 'success' and results['integration_tests']['status'] == 'success':
        print("✅ 所有测试通过，可以手动创建PR")
    
    print("\n✅ 自动进化流程完成！")
    
    # 检查是否所有关键步骤都成功
    success = (
        results['unit_tests']['status'] == 'success' and
        results['integration_tests']['status'] == 'success'
    )
    
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)