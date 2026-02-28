#!/usr/bin/env python3
"""
连续数据扩展工作脚本 - 7×24小时运行
自动扩展基金数据缓存，定期提交到GitHub
"""

import os
import sys
import time
import subprocess
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('auto_evolution.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

from enhanced_data_fetcher import EnhancedDataFetcher
from agents.data_backtest.backtest_engine import BacktestEngine


class ContinuousWorker:
    """连续工作者 - 7×24小时运行"""
    
    def __init__(self):
        self.fetcher = EnhancedDataFetcher()
        self.backtest_engine = BacktestEngine()
        self.work_cycle_count = 0
        self.total_funds_processed = 0
        self.last_git_commit_time = None
        
    def get_current_cache_count(self) -> int:
        """获取当前缓存文件数量"""
        cache_dir = 'data_cache'
        if not os.path.exists(cache_dir):
            return 0
        return len([f for f in os.listdir(cache_dir) if f.endswith('.csv')])
    
    def expand_data_batch(self, batch_size: int = 100) -> int:
        """扩展一批数据"""
        logger.info(f"开始扩展数据批次，目标数量: {batch_size}")
        
        # 获取基金列表
        fund_list = self.fetcher.get_comprehensive_fund_list()
        logger.info(f"获取到基金列表: {len(fund_list)} 只")
        
        # 获取已缓存的基金代码
        cached_funds = set()
        cache_dir = 'data_cache'
        if os.path.exists(cache_dir):
            for f in os.listdir(cache_dir):
                if f.endswith('.csv'):
                    cached_funds.add(f.replace('.csv', ''))
        
        # 选择未缓存的基金
        new_funds = []
        for _, row in fund_list.iterrows():
            fund_code = row['fund_code']
            if fund_code not in cached_funds:
                new_funds.append(fund_code)
                if len(new_funds) >= batch_size:
                    break
        
        if not new_funds:
            logger.info("所有基金已缓存，无需扩展")
            return 0
        
        logger.info(f"需要获取新基金: {len(new_funds)} 只")
        
        # 批量获取数据
        success_count = 0
        for i, fund_code in enumerate(new_funds):
            try:
                # 获取数据
                nav_data = self.fetcher.fetch_fund_data_with_fallback(fund_code, days=730)
                
                if not nav_data.empty and len(nav_data) > 30:
                    success_count += 1
                    
                # 进度日志
                if (i + 1) % 10 == 0:
                    logger.info(f"进度: {i+1}/{len(new_funds)} ({success_count} 成功)")
                    
            except Exception as e:
                logger.error(f"获取基金{fund_code}数据失败: {e}")
                
        logger.info(f"批次完成: 成功获取 {success_count}/{len(new_funds)} 只基金")
        return success_count
    
    def run_backtest_on_cache(self) -> dict:
        """对缓存数据运行回测"""
        logger.info("开始运行回测分析...")
        
        cache_dir = 'data_cache'
        if not os.path.exists(cache_dir):
            return {}
            
        # 获取所有缓存文件
        cache_files = [f for f in os.listdir(cache_dir) if f.endswith('.csv')]
        if not cache_files:
            return {}
        
        results = {}
        processed = 0
        
        for cache_file in cache_files[:50]:  # 每次最多处理50只
            fund_code = cache_file.replace('.csv', '')
            try:
                import pandas as pd
                nav_data = pd.read_csv(os.path.join(cache_dir, cache_file), parse_dates=['date'])
                
                if len(nav_data) > 30:
                    backtest_result = self.backtest_engine.backtest_single_fund(fund_code, nav_data)
                    results[fund_code] = backtest_result
                    processed += 1
                    
            except Exception as e:
                logger.error(f"回测基金{fund_code}失败: {e}")
                
        logger.info(f"回测完成: {processed} 只基金")
        return results
    
    def commit_to_github(self, message: str = None) -> bool:
        """提交到GitHub"""
        try:
            if message is None:
                cache_count = self.get_current_cache_count()
                message = f"auto: Data expansion - {cache_count} funds cached"
            
            # Git操作
            subprocess.run(['git', 'add', '.'], check=True)
            subprocess.run(['git', 'commit', '-m', message], check=True)
            subprocess.run(['git', 'push', 'origin', 'enhanced-strategy-agent-20260228'], check=True)
            
            self.last_git_commit_time = datetime.now()
            logger.info(f"✅ 成功提交到GitHub: {message}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"提交到GitHub失败: {e}")
            return False
        except Exception as e:
            logger.error(f"Git操作异常: {e}")
            return False
    
    def run_work_cycle(self) -> dict:
        """运行一个工作周期"""
        self.work_cycle_count += 1
        logger.info(f"\n{'='*60}")
        logger.info(f"工作周期 #{self.work_cycle_count} 开始")
        logger.info(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"{'='*60}")
        
        cycle_result = {
            'cycle_id': self.work_cycle_count,
            'start_time': datetime.now().isoformat(),
            'funds_added': 0,
            'backtest_completed': False,
            'git_committed': False
        }
        
        # 1. 扩展数据
        logger.info("任务1: 扩展基金数据...")
        initial_count = self.get_current_cache_count()
        funds_added = self.expand_data_batch(batch_size=50)
        final_count = self.get_current_cache_count()
        
        cycle_result['funds_added'] = final_count - initial_count
        self.total_funds_processed += cycle_result['funds_added']
        
        logger.info(f"数据缓存: {initial_count} -> {final_count} (+{cycle_result['funds_added']})")
        
        # 2. 运行回测
        logger.info("任务2: 运行回测分析...")
        backtest_results = self.run_backtest_on_cache()
        cycle_result['backtest_completed'] = len(backtest_results) > 0
        
        # 3. 提交到GitHub
        logger.info("任务3: 检查是否需要提交到GitHub...")
        should_commit = (
            cycle_result['funds_added'] > 0 or
            self.last_git_commit_time is None or
            (datetime.now() - self.last_git_commit_time).total_seconds() > 3600  # 1小时
        )
        
        if should_commit:
            cycle_result['git_committed'] = self.commit_to_github()
        else:
            logger.info("暂不需要提交到GitHub")
        
        cycle_result['end_time'] = datetime.now().isoformat()
        
        logger.info(f"\n工作周期 #{self.work_cycle_count} 完成:")
        logger.info(f"  新增基金: {cycle_result['funds_added']}")
        logger.info(f"  总基金数: {final_count}")
        logger.info(f"  回测完成: {cycle_result['backtest_completed']}")
        logger.info(f"  Git提交: {cycle_result['git_committed']}")
        
        return cycle_result
    
    def run_continuous(self, max_cycles: int = None, rest_seconds: int = 300):
        """连续运行"""
        logger.info("🚀 启动连续工作模式...")
        logger.info(f"最大周期数: {max_cycles or '无限'}")
        logger.info(f"周期间休息: {rest_seconds}秒")
        
        cycle_count = 0
        while True:
            if max_cycles and cycle_count >= max_cycles:
                logger.info(f"达到最大周期数 {max_cycles}，停止工作")
                break
                
            try:
                # 运行工作周期
                self.run_work_cycle()
                cycle_count += 1
                
                # 休息
                if rest_seconds > 0:
                    logger.info(f"休息 {rest_seconds} 秒...")
                    time.sleep(rest_seconds)
                    
            except KeyboardInterrupt:
                logger.info("用户中断，停止工作")
                break
            except Exception as e:
                logger.error(f"工作周期异常: {e}")
                logger.info("休息60秒后继续...")
                time.sleep(60)


if __name__ == "__main__":
    worker = ContinuousWorker()
    
    # 解析命令行参数
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--max-cycles', type=int, default=None, help='最大工作周期数')
    parser.add_argument('--rest', type=int, default=300, help='周期间休息时间（秒）')
    parser.add_argument('--single', action='store_true', help='只运行一个周期')
    args = parser.parse_args()
    
    if args.single:
        # 只运行一个周期
        worker.run_work_cycle()
    else:
        # 连续运行
        worker.run_continuous(max_cycles=args.max_cycles, rest_seconds=args.rest)