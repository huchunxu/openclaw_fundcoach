#!/usr/bin/env python3
"""
自动数据扩展脚本 - 批量抓取大量基金数据以扩展数据集
"""

import pandas as pd
import numpy as np
import os
import sys
import time
from datetime import datetime, timedelta
from typing import List, Dict

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

from agents.data_backtest.fund_data_real import RealFundDataFetcher


def auto_expand_fund_dataset(target_fund_count: int = 5000, batch_size: int = 100):
    """
    自动扩展基金数据集
    
    Args:
        target_fund_count: 目标基金数量
        batch_size: 每批处理的基金数量
    """
    print(f"🚀 开始自动数据扩展...")
    print(f"目标基金数量: {target_fund_count}")
    print(f"批次大小: {batch_size}")
    
    # 初始化数据抓取器
    fetcher = RealFundDataFetcher(cache_dir="data_cache")
    
    # 获取基金列表
    print("1. 获取基金列表...")
    fund_list = fetcher.get_fund_list_real()
    print(f"   获取到 {len(fund_list)} 只基金")
    
    if len(fund_list) == 0:
        print("❌ 无法获取基金列表，使用示例数据")
        return
    
    # 过滤有效的基金代码
    valid_funds = fund_list[fund_list['fund_code'].str.match(r'^\d{6}$')]
    print(f"   有效基金数量: {len(valid_funds)}")
    
    # 限制目标数量
    target_funds = valid_funds.head(target_fund_count)
    fund_codes = target_funds['fund_code'].tolist()
    
    print(f"2. 开始批量抓取 {len(fund_codes)} 只基金数据...")
    
    # 分批处理
    total_processed = 0
    successful_fetches = 0
    
    for i in range(0, len(fund_codes), batch_size):
        batch = fund_codes[i:i+batch_size]
        print(f"   处理批次 {i//batch_size + 1}/{(len(fund_codes)-1)//batch_size + 1} ({len(batch)} 只基金)")
        
        try:
            # 批量获取数据
            batch_data = fetcher.batch_fetch_funds_real(batch, use_cache=True)
            
            successful_fetches += len(batch_data)
            total_processed += len(batch)
            
            print(f"   ✅ 成功获取 {len(batch_data)} 只基金数据")
            
            # 避免请求过于频繁
            if len(batch) > 1:
                time.sleep(2)
                
        except Exception as e:
            print(f"   ⚠️  批次处理失败: {e}")
            total_processed += len(batch)
            continue
    
    print(f"\n📊 数据扩展完成!")
    print(f"   总处理基金: {total_processed}")
    print(f"   成功获取: {successful_fetches}")
    print(f"   缓存目录: data_cache/")
    
    # 统计缓存文件数量
    cache_files = os.listdir("data_cache") if os.path.exists("data_cache") else []
    print(f"   缓存文件数: {len(cache_files)}")
    
    return successful_fetches


def validate_data_quality():
    """验证数据质量"""
    print("\n🔍 验证数据质量...")
    
    if not os.path.exists("data_cache"):
        print("   ❌ 缓存目录不存在")
        return False
    
    cache_files = [f for f in os.listdir("data_cache") if f.endswith('.csv')]
    if len(cache_files) == 0:
        print("   ❌ 无缓存数据文件")
        return False
    
    # 随机检查几个文件
    import random
    sample_files = random.sample(cache_files, min(5, len(cache_files)))
    
    valid_files = 0
    for file in sample_files:
        try:
            df = pd.read_csv(os.path.join("data_cache", file), parse_dates=['date'])
            if len(df) > 100 and 'nav' in df.columns:
                valid_files += 1
        except:
            continue
    
    quality_score = valid_files / len(sample_files)
    print(f"   数据质量评分: {quality_score:.2%}")
    
    return quality_score > 0.8


def main():
    """主函数"""
    print("=" * 60)
    print("OpenClaw FundCoach - 自动数据扩展")
    print("=" * 60)
    
    try:
        # 扩展数据集
        success_count = auto_expand_fund_dataset(target_fund_count=2000, batch_size=50)
        
        if success_count > 0:
            # 验证数据质量
            if validate_data_quality():
                print("\n✅ 数据扩展成功！可以进行下一步优化。")
            else:
                print("\n⚠️  数据质量较低，建议重新运行。")
        else:
            print("\n❌ 数据扩展失败！")
            
    except KeyboardInterrupt:
        print("\n⏹️  用户中断操作")
    except Exception as e:
        print(f"\n❌ 数据扩展出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()