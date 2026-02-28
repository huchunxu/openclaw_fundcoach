#!/usr/bin/env python3
"""
简化版自动进化引擎 - 无需GitPython依赖
"""

import os
import sys
import pandas as pd
from datetime import datetime
import logging

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

from enhanced_data_fetcher import EnhancedDataFetcher
from agents.data_backtest.backtest_engine import BacktestEngine
from agents.strategy_agent.factor_model_enhanced import EnhancedFactorModel
from agents.strategy_agent.fund_scoring_enhanced import EnhancedFundScoringSystem

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_simple_auto_evolution():
    """运行简化版自动进化"""
    logger.info("🚀 开始简化版自动进化流程...")
    
    # 1. 获取基金列表
    logger.info("1. 获取基金列表...")
    fetcher = EnhancedDataFetcher()
    fund_list = fetcher.get_comprehensive_fund_list()
    logger.info(f"获取到 {len(fund_list)} 只基金")
    
    # 2. 选择前50只基金进行数据扩展
    target_funds = fund_list.head(50)['fund_code'].tolist()
    logger.info(f"2. 选择前 {len(target_funds)} 只基金进行数据扩展...")
    
    # 3. 批量获取数据
    fund_data_dict = fetcher.batch_fetch_enhanced(target_funds, use_cache=True)
    logger.info(f"3. 成功获取 {len(fund_data_dict)} 只基金的数据")
    
    # 4. 运行回测和分析
    logger.info("4. 运行回测和因子分析...")
    backtest_engine = BacktestEngine()
    factor_model = EnhancedFactorModel()
    scoring_system = EnhancedFundScoringSystem()
    
    analyzed_funds = 0
    for fund_code, nav_data in fund_data_dict.items():
        if len(nav_data) < 30:
            continue
            
        # 回测
        backtest_results = backtest_engine.backtest_single_fund(fund_code, nav_data)
        
        # 基金基本信息（模拟）
        fund_basic_info = {
            'fund_code': fund_code,
            'fund_name': f'基金{fund_code}',
            'fund_type': '混合型',
            'fund_size': 50.0,
            'establish_date': '2020-01-01'
        }
        
        # 因子分析
        factors = factor_model.calculate_all_factors(
            fund_code, fund_basic_info, nav_data, backtest_results
        )
        
        # 打分
        score_result = scoring_system.score_single_fund_enhanced(
            fund_code, fund_basic_info, nav_data, backtest_results
        )
        
        analyzed_funds += 1
        if analyzed_funds % 10 == 0:
            logger.info(f"已分析 {analyzed_funds} 只基金")
    
    logger.info(f"4. 完成分析 {analyzed_funds} 只基金")
    
    # 5. 检查数据缓存
    cache_files = os.listdir('data_cache') if os.path.exists('data_cache') else []
    logger.info(f"5. 数据缓存文件数: {len(cache_files)}")
    
    logger.info("✅ 简化版自动进化完成！")
    return len(fund_data_dict), len(cache_files)

if __name__ == "__main__":
    try:
        funds_processed, cache_count = run_simple_auto_evolution()
        print(f"\n📊 自动进化结果:")
        print(f"   处理基金数量: {funds_processed}")
        print(f"   缓存文件数量: {cache_count}")
        print(f"   完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    except Exception as e:
        logger.error(f"自动进化失败: {e}")
        sys.exit(1)