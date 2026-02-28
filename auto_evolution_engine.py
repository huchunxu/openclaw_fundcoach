#!/usr/bin/env python3
"""
自动进化引擎 - 实现OpenClaw FundCoach的自进化能力
"""

import pandas as pd
import numpy as np
import os
import sys
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import git
import subprocess

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

from enhanced_data_fetcher import EnhancedDataFetcher
from enhanced_backtest_engine import EnhancedBacktestEngine
from agents.strategy_agent.factor_model_enhanced import EnhancedFactorModel
from agents.strategy_agent.fund_scoring_enhanced import EnhancedFundScoringSystem
from agents.portfolio_agent.portfolio_generator_enhanced import EnhancedPortfolioGenerator
from agents.portfolio_agent.weight_optimizer_enhanced import EnhancedWeightOptimizer
from agents.risk_agent.stress_testing_enhanced import EnhancedStressTesting
from agents.risk_agent.risk_exposure_enhanced import EnhancedRiskExposureAnalyzer


class AutoEvolutionEngine:
    """自动进化引擎"""
    
    def __init__(self, config_file: str = "evolution_config.json"):
        self.config = self._load_config(config_file)
        self.data_fetcher = EnhancedDataFetcher()
        self.backtest_engine = EnhancedBacktestEngine()
        self.evolution_history = []
        self.repo = git.Repo(os.path.dirname(__file__))
        
    def _load_config(self, config_file: str) -> Dict:
        """加载配置文件"""
        default_config = {
            "data_expansion": {
                "target_fund_count": 5000,
                "batch_size": 100,
                "retry_attempts": 3,
                "cache_dir": "data_cache"
            },
            "backtest_settings": {
                "min_history_days": 730,  # 2年
                "max_drawdown_threshold": -0.35,
                "min_sharpe_ratio": 0.8,
                "benchmark_codes": ["000300", "000905"]  # 沪深300, 中证500
            },
            "evolution_triggers": {
                "sharpe_decline_threshold": 0.1,
                "drawdown_exceed_threshold": True,
                "fund_pool_change_threshold": 0.2,
                "new_factor_available": True
            },
            "github_settings": {
                "auto_commit": True,
                "auto_push": True,
                "branch_prefix": "auto-evolution-",
                "pr_template": "AUTO: Evolution improvement - {improvement_summary}"
            }
        }
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                    # 合并配置
                    for key, value in user_config.items():
                        if key in default_config:
                            default_config[key].update(value)
                        else:
                            default_config[key] = value
            except Exception as e:
                print(f"加载配置文件失败: {e}")
                
        return default_config
    
    def expand_fund_data(self) -> Dict:
        """扩展基金数据池"""
        print("🚀 开始扩展基金数据池...")
        
        target_count = self.config["data_expansion"]["target_fund_count"]
        batch_size = self.config["data_expansion"]["batch_size"]
        cache_dir = self.config["data_expansion"]["cache_dir"]
        
        # 获取现有缓存数据
        existing_funds = set()
        if os.path.exists(cache_dir):
            for file in os.listdir(cache_dir):
                if file.endswith('.csv'):
                    fund_code = file.replace('.csv', '')
                    existing_funds.add(fund_code)
        
        print(f"现有基金数量: {len(existing_funds)}")
        
        # 获取基金列表
        fund_list = self.data_fetcher.get_fund_list_real()
        print(f"获取到基金列表: {len(fund_list)} 只")
        
        # 过滤已有基金
        new_funds = []
        for _, row in fund_list.iterrows():
            fund_code = row['fund_code']
            if fund_code not in existing_funds:
                new_funds.append(fund_code)
                if len(new_funds) >= (target_count - len(existing_funds)):
                    break
        
        print(f"需要获取新基金: {len(new_funds)} 只")
        
        # 批量获取数据
        success_count = 0
        total_processed = 0
        
        for i in range(0, len(new_funds), batch_size):
            batch = new_funds[i:i+batch_size]
            print(f"处理批次 {i//batch_size + 1}/{(len(new_funds)-1)//batch_size + 1} ({len(batch)} 只基金)")
            
            batch_result = self.data_fetcher.batch_fetch_funds_real(
                batch, 
                use_cache=True,
                max_workers=10,
                timeout=30
            )
            
            success_count += len(batch_result)
            total_processed += len(batch)
            
            # 避免过于频繁请求
            time.sleep(2)
        
        # 验证数据质量
        final_fund_count = len(existing_funds) + success_count
        data_quality = self._assess_data_quality(cache_dir)
        
        result = {
            "initial_fund_count": len(existing_funds),
            "expanded_fund_count": final_fund_count,
            "success_rate": success_count / max(len(new_funds), 1),
            "data_quality_score": data_quality,
            "cache_dir": cache_dir
        }
        
        print(f"✅ 数据扩展完成! 最终基金数量: {final_fund_count}")
        return result
    
    def _assess_data_quality(self, cache_dir: str) -> float:
        """评估数据质量"""
        if not os.path.exists(cache_dir):
            return 0.0
            
        csv_files = [f for f in os.listdir(cache_dir) if f.endswith('.csv')]
        if not csv_files:
            return 0.0
            
        quality_scores = []
        sample_size = min(10, len(csv_files))
        
        for file in csv_files[:sample_size]:
            try:
                df = pd.read_csv(os.path.join(cache_dir, file))
                if len(df) >= 365:  # 至少1年数据
                    quality_scores.append(1.0)
                elif len(df) >= 180:  # 至少半年数据
                    quality_scores.append(0.7)
                elif len(df) >= 90:  # 至少3个月数据
                    quality_scores.append(0.4)
                else:
                    quality_scores.append(0.1)
            except:
                quality_scores.append(0.0)
                
        return np.mean(quality_scores) if quality_scores else 0.0
    
    def run_comprehensive_backtest(self, fund_codes: List[str]) -> Dict:
        """运行全面回测"""
        print("📊 开始全面回测分析...")
        
        # 获取基金数据
        fund_nav_dict = {}
        fund_basic_info = {}
        
        for fund_code in fund_codes:
            nav_data = self.data_fetcher.load_cached_data(fund_code)
            if nav_data is not None and len(nav_data) >= 365:
                fund_nav_dict[fund_code] = nav_data
                
                basic_info = self.data_fetcher.get_fund_basic_info_real(fund_code)
                fund_basic_info[fund_code] = basic_info
        
        if not fund_nav_dict:
            print("❌ 无有效基金数据进行回测")
            return {}
        
        # 运行回测
        backtest_results = {}
        for fund_code, nav_data in fund_nav_dict.items():
            results = self.backtest_engine.backtest_single_fund(fund_code, nav_data)
            backtest_results[fund_code] = results
        
        # 计算整体统计
        sharpe_ratios = [r['sharpe_ratio'] for r in backtest_results.values()]
        max_drawdowns = [r['max_drawdown'] for r in backtest_results.values()]
        annual_returns = [r['annual_return'] for r in backtest_results.values()]
        
        overall_stats = {
            "total_funds": len(backtest_results),
            "avg_sharpe_ratio": np.mean(sharpe_ratios),
            "median_sharpe_ratio": np.median(sharpe_ratios),
            "best_sharpe_ratio": max(sharpe_ratios),
            "worst_sharpe_ratio": min(sharpe_ratios),
            "avg_max_drawdown": np.mean(max_drawdowns),
            "median_max_drawdown": np.median(max_drawdowns),
            "best_max_drawdown": max(max_drawdowns),  # 最小回撤（最不负面）
            "worst_max_drawdown": min(max_drawdowns),  # 最大回撤
            "avg_annual_return": np.mean(annual_returns),
            "median_annual_return": np.median(annual_returns)
        }
        
        result = {
            "backtest_results": backtest_results,
            "overall_stats": overall_stats,
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"✅ 回测完成! 分析了 {len(backtest_results)} 只基金")
        return result
    
    def evaluate_current_performance(self) -> Dict:
        """评估当前系统性能"""
        print("🔍 评估当前系统性能...")
        
        # 获取当前基金池
        cache_dir = self.config["data_expansion"]["cache_dir"]
        fund_codes = []
        if os.path.exists(cache_dir):
            for file in os.listdir(cache_dir):
                if file.endswith('.csv'):
                    fund_code = file.replace('.csv', '')
                    fund_codes.append(fund_code)
        
        if not fund_codes:
            return {"status": "no_data", "message": "无基金数据"}
        
        # 运行回测
        backtest_result = self.run_comprehensive_backtest(fund_codes[:1000])  # 限制数量
        
        if not backtest_result:
            return {"status": "backtest_failed", "message": "回测失败"}
        
        # 评估性能指标
        stats = backtest_result["overall_stats"]
        performance_score = 0.0
        
        # 夏普率评分
        if stats["avg_sharpe_ratio"] >= 1.0:
            sharpe_score = 1.0
        elif stats["avg_sharpe_ratio"] >= 0.8:
            sharpe_score = 0.8
        elif stats["avg_sharpe_ratio"] >= 0.6:
            sharpe_score = 0.6
        else:
            sharpe_score = 0.4
        
        # 回撤评分
        avg_dd = stats["avg_max_drawdown"]
        if avg_dd >= -0.2:
            drawdown_score = 1.0
        elif avg_dd >= -0.25:
            drawdown_score = 0.8
        elif avg_dd >= -0.3:
            drawdown_score = 0.6
        else:
            drawdown_score = 0.4
        
        # 收益评分
        avg_return = stats["avg_annual_return"]
        if avg_return >= 0.15:
            return_score = 1.0
        elif avg_return >= 0.1:
            return_score = 0.8
        elif avg_return >= 0.05:
            return_score = 0.6
        else:
            return_score = 0.4
        
        performance_score = (sharpe_score + drawdown_score + return_score) / 3.0
        
        evaluation = {
            "status": "success",
            "performance_score": performance_score,
            "metrics": {
                "avg_sharpe_ratio": stats["avg_sharpe_ratio"],
                "avg_max_drawdown": stats["avg_max_drawdown"],
                "avg_annual_return": stats["avg_annual_return"]
            },
            "recommendations": self._generate_recommendations(stats)
        }
        
        print(f"✅ 性能评估完成! 综合得分: {performance_score:.2f}")
        return evaluation
    
    def _generate_recommendations(self, stats: Dict) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        if stats["avg_sharpe_ratio"] < 0.8:
            recommendations.append("夏普率偏低，建议优化因子模型或调整权重")
            
        if stats["avg_max_drawdown"] < -0.25:
            recommendations.append("回撤控制不足，建议加强风险约束")
            
        if stats["avg_annual_return"] < 0.08:
            recommendations.append("收益表现一般，建议引入新的alpha因子")
            
        if stats["total_funds"] < 1000:
            recommendations.append("基金池规模较小，建议扩展数据源")
            
        return recommendations
    
    def trigger_evolution(self, force: bool = False) -> bool:
        """触发进化流程"""
        print("🔄 检查是否需要触发进化...")
        
        if force:
            print("⚡ 强制触发进化")
            return True
            
        # 评估当前性能
        evaluation = self.evaluate_current_performance()
        if evaluation["status"] != "success":
            print(f"⚠️ 评估失败: {evaluation.get('message', '未知错误')}")
            return False
            
        performance_score = evaluation["performance_score"]
        metrics = evaluation["metrics"]
        
        # 检查进化触发条件
        triggers = self.config["evolution_triggers"]
        
        if triggers["sharpe_decline_threshold"] > 0:
            if metrics["avg_sharpe_ratio"] < (1.0 - triggers["sharpe_decline_threshold"]):
                print("🎯 触发条件: 夏普率下降")
                return True
                
        if triggers["drawdown_exceed_threshold"]:
            if metrics["avg_max_drawdown"] < -0.3:
                print("🎯 触发条件: 回撤超出阈值")
                return True
                
        if triggers["fund_pool_change_threshold"] > 0:
            # 检查基金池变化
            cache_dir = self.config["data_expansion"]["cache_dir"]
            current_fund_count = len([f for f in os.listdir(cache_dir) if f.endswith('.csv')])
            if hasattr(self, '_last_fund_count'):
                change_ratio = abs(current_fund_count - self._last_fund_count) / self._last_fund_count
                if change_ratio > triggers["fund_pool_change_threshold"]:
                    print("🎯 触发条件: 基金池显著变化")
                    return True
            self._last_fund_count = current_fund_count
            
        if triggers["new_factor_available"]:
            # 检查是否有新因子可用
            if hasattr(self, '_last_factor_count'):
                current_factor_count = len(EnhancedFactorModel().__dict__.get('factors', {}))
                if current_factor_count > self._last_factor_count:
                    print("🎯 触发条件: 新因子可用")
                    return True
            else:
                self._last_factor_count = 6  # 当前因子数量
                
        print("⏸️ 无需进化，当前性能良好")
        return False
    
    def execute_evolution_step(self) -> Dict:
        """执行单次进化步骤"""
        print("🧬 执行进化步骤...")
        
        # 步骤1: 扩展数据
        data_result = self.expand_fund_data()
        
        # 步骤2: 重新评估性能
        evaluation = self.evaluate_current_performance()
        
        # 步骤3: 如果性能提升，保存结果
        evolution_result = {
            "data_expansion": data_result,
            "performance_evaluation": evaluation,
            "timestamp": datetime.now().isoformat(),
            "evolution_id": f"evol_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        }
        
        # 保存进化历史
        self.evolution_history.append(evolution_result)
        
        # 自动提交到GitHub
        if self.config["github_settings"]["auto_commit"]:
            self._auto_commit_evolution(evolution_result)
            
        return evolution_result
    
    def _auto_commit_evolution(self, evolution_result: Dict):
        """自动提交进化结果到GitHub"""
        try:
            # 创建新分支
            branch_name = f"{self.config['github_settings']['branch_prefix']}{evolution_result['evolution_id']}"
            new_branch = self.repo.create_head(branch_name)
            new_branch.checkout()
            
            # 添加和提交更改
            self.repo.git.add(A=True)
            commit_message = self.config["github_settings"]["pr_template"].format(
                improvement_summary=f"Data expanded to {evolution_result['data_expansion']['expanded_fund_count']} funds, performance score: {evolution_result['performance_evaluation'].get('performance_score', 0):.2f}"
            )
            self.repo.index.commit(commit_message)
            
            # 推送到远程
            if self.config["github_settings"]["auto_push"]:
                origin = self.repo.remote(name='origin')
                origin.push(refspec=f"{branch_name}:{branch_name}")
                print(f"✅ 自动提交到分支: {branch_name}")
                
        except Exception as e:
            print(f"❌ 自动提交失败: {e}")
    
    def run_continuous_evolution(self, max_iterations: int = 10):
        """运行连续进化"""
        print("🚀 启动连续进化引擎...")
        print("=" * 50)
        
        for iteration in range(max_iterations):
            print(f"\n🔄 进化迭代 {iteration + 1}/{max_iterations}")
            
            # 检查是否需要进化
            if self.trigger_evolution():
                # 执行进化
                result = self.execute_evolution_step()
                print(f"✅ 进化完成: {result['evolution_id']}")
            else:
                print("⏸️ 跳过本次迭代")
                
            # 等待一段时间再进行下一次检查
            if iteration < max_iterations - 1:
                wait_time = 3600  # 1小时
                print(f"⏳ 等待 {wait_time} 秒后进行下一次检查...")
                time.sleep(wait_time)
        
        print("\n🏁 连续进化完成!")


if __name__ == "__main__":
    # 创建进化引擎
    engine = AutoEvolutionEngine()
    
    # 运行单次进化（用于测试）
    if len(sys.argv) > 1 and sys.argv[1] == "--continuous":
        # 运行连续进化
        engine.run_continuous_evolution()
    else:
        # 运行单次进化
        result = engine.execute_evolution_step()
        print(f"\n📊 进化结果:")
        print(f"  数据扩展: {result['data_expansion']['expanded_fund_count']} 只基金")
        if 'performance_evaluation' in result:
            eval_result = result['performance_evaluation']
            if eval_result['status'] == 'success':
                print(f"  性能得分: {eval_result['performance_score']:.2f}")
                print(f"  夏普率: {eval_result['metrics']['avg_sharpe_ratio']:.2f}")
                print(f"  平均回撤: {eval_result['metrics']['avg_max_drawdown']:.2%}")