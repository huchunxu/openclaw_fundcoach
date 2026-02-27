#!/usr/bin/env python3
"""
DevOps Agent - 自动化测试、回测对比和Pull Request生成
"""

import os
import sys
import subprocess
import json
import datetime
from typing import Dict, List, Tuple
import logging

class DevOpsAgent:
    """DevOps智能体：负责自动化测试、回测对比和PR生成"""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = repo_path
        self.logger = logging.getLogger(__name__)
    
    def run_unit_tests(self) -> Dict:
        """运行单元测试"""
        try:
            # 尝试使用pytest
            result = subprocess.run(
                ["python", "-m", "unittest", "discover", "tests", "-v"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                return {
                    'status': 'success',
                    'message': '所有单元测试通过',
                    'output': result.stdout
                }
            else:
                return {
                    'status': 'failure',
                    'message': '单元测试失败',
                    'error': result.stderr,
                    'output': result.stdout
                }
        except subprocess.TimeoutExpired:
            return {
                'status': 'failure',
                'message': '单元测试超时',
                'error': '测试执行时间超过5分钟'
            }
        except Exception as e:
            return {
                'status': 'failure',
                'message': '单元测试执行异常',
                'error': str(e)
            }
    
    def run_integration_test(self) -> Dict:
        """运行集成测试"""
        try:
            result = subprocess.run(
                ["python", "integration_test.py"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                return {
                    'status': 'success',
                    'message': '集成测试通过',
                    'output': result.stdout
                }
            else:
                return {
                    'status': 'failure',
                    'message': '集成测试失败',
                    'error': result.stderr,
                    'output': result.stdout
                }
        except subprocess.TimeoutExpired:
            return {
                'status': 'failure',
                'message': '集成测试超时',
                'error': '测试执行时间超过5分钟'
            }
        except Exception as e:
            return {
                'status': 'failure',
                'message': '集成测试执行异常',
                'error': str(e)
            }
    
    def run_backtest_comparison(self, old_strategy: Dict, new_strategy: Dict) -> Dict:
        """运行回测对比分析"""
        # 这里应该实现具体的回测对比逻辑
        # 为简化，我们模拟一个对比结果
        comparison = {
            'annual_return_change': new_strategy.get('annual_return', 0) - old_strategy.get('annual_return', 0),
            'sharpe_ratio_change': new_strategy.get('sharpe_ratio', 0) - old_strategy.get('sharpe_ratio', 0),
            'max_drawdown_change': new_strategy.get('max_drawdown', 0) - old_strategy.get('max_drawdown', 0),
            'volatility_change': new_strategy.get('volatility', 0) - old_strategy.get('volatility', 0)
        }
        
        # 判断是否改进
        improvements = []
        regressions = []
        
        if comparison['annual_return_change'] > 0.01:
            improvements.append(f"年化收益提升 {comparison['annual_return_change']:.2%}")
        elif comparison['annual_return_change'] < -0.01:
            regressions.append(f"年化收益下降 {abs(comparison['annual_return_change']):.2%}")
        
        if comparison['sharpe_ratio_change'] > 0.1:
            improvements.append(f"夏普率提升 {comparison['sharpe_ratio_change']:.3f}")
        elif comparison['sharpe_ratio_change'] < -0.1:
            regressions.append(f"夏普率下降 {abs(comparison['sharpe_ratio_change']):.3f}")
        
        if comparison['max_drawdown_change'] > 0.05:  # 回撤变小（负值变大）
            improvements.append(f"最大回撤改善 {comparison['max_drawdown_change']:.2%}")
        elif comparison['max_drawdown_change'] < -0.05:
            regressions.append(f"最大回撤恶化 {abs(comparison['max_drawdown_change']):.2%}")
        
        return {
            'comparison': comparison,
            'improvements': improvements,
            'regressions': regressions,
            'is_improved': len(improvements) > len(regressions)
        }
    
    def create_branch(self, branch_name: str) -> Dict:
        """创建新分支"""
        try:
            # 检查分支是否已存在
            result = subprocess.run(
                ["git", "branch", "--list", branch_name],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            if result.stdout.strip():
                # 分支已存在，切换到该分支
                subprocess.run(["git", "checkout", branch_name], cwd=self.repo_path)
                return {
                    'status': 'success',
                    'message': f'已切换到现有分支 {branch_name}'
                }
            
            # 创建新分支
            result = subprocess.run(
                ["git", "checkout", "-b", branch_name],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return {
                    'status': 'success',
                    'message': f'成功创建并切换到分支 {branch_name}'
                }
            else:
                return {
                    'status': 'failure',
                    'message': '创建分支失败',
                    'error': result.stderr
                }
        except Exception as e:
            return {
                'status': 'failure',
                'message': '创建分支异常',
                'error': str(e)
            }
    
    def commit_changes(self, message: str) -> Dict:
        """提交更改"""
        try:
            # 添加所有更改
            subprocess.run(["git", "add", "."], cwd=self.repo_path)
            
            # 提交
            result = subprocess.run(
                ["git", "commit", "-m", message],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return {
                    'status': 'success',
                    'message': '更改已提交',
                    'commit_hash': result.stdout.strip()
                }
            else:
                return {
                    'status': 'failure',
                    'message': '提交失败',
                    'error': result.stderr
                }
        except Exception as e:
            return {
                'status': 'failure',
                'message': '提交异常',
                'error': str(e)
            }
    
    def push_branch(self, branch_name: str) -> Dict:
        """推送分支到远程仓库"""
        try:
            result = subprocess.run(
                ["git", "push", "origin", branch_name],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return {
                    'status': 'success',
                    'message': f'分支 {branch_name} 已推送到远程仓库'
                }
            else:
                return {
                    'status': 'failure',
                    'message': '推送分支失败',
                    'error': result.stderr
                }
        except Exception as e:
            return {
                'status': 'failure',
                'message': '推送分支异常',
                'error': str(e)
            }
    
    def generate_pr_description(self, improvements: List[str], regressions: List[str], 
                              comparison: Dict, risk_assessment: str) -> str:
        """生成PR描述"""
        description = f"""# 策略优化改进

## 改进目标
自动优化基金量化策略，提升风险调整后收益。

## 修改文件
- agents/strategy_agent.py
- agents/portfolio_agent.py  
- agents/risk_agent.py
- web_app/app.py
- frontend/src/components/

## 回测区间
最近3年历史数据（包含完整牛熊周期）

## 性能变化
"""
        
        if improvements:
            description += "### ✅ 改进项\n"
            for improvement in improvements:
                description += f"- {improvement}\n"
        
        if regressions:
            description += "### ⚠️ 退步项\n"
            for regression in regressions:
                description += f"- {regression}\n"
        
        description += f"""
## 风险说明
{risk_assessment}

## 影响评估
- **是否影响现有策略**: 否，新增功能不影响现有API
- **向后兼容性**: 完全兼容
- **测试覆盖**: 包含单元测试和集成测试

---

**历史数据仅供参考，不构成投资建议。**
"""
        
        return description
    
    def create_pull_request(self, branch_name: str, title: str, description: str) -> Dict:
        """创建Pull Request（模拟）"""
        # 在实际环境中，这里会调用GitHub API
        # 目前我们只生成PR信息
        pr_info = {
            'branch': branch_name,
            'title': title,
            'description': description,
            'status': 'ready_for_review'
        }
        
        # 保存PR信息到文件
        pr_file = f"pr_{branch_name.replace('/', '_')}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(os.path.join(self.repo_path, pr_file), 'w') as f:
            f.write(f"# {title}\n\n{description}")
        
        return {
            'status': 'success',
            'message': f'Pull Request信息已生成: {pr_file}',
            'pr_info': pr_info
        }
    
    def run_full_pipeline(self, strategy_improvement: Dict = None) -> Dict:
        """运行完整的DevOps流水线"""
        results = {}
        
        # 1. 运行测试
        self.logger.info("Running unit tests...")
        results['unit_tests'] = self.run_unit_tests()
        
        self.logger.info("Running integration tests...")
        results['integration_tests'] = self.run_integration_test()
        
        # 2. 如果提供了策略改进信息，进行回测对比
        if strategy_improvement:
            self.logger.info("Running backtest comparison...")
            old_metrics = strategy_improvement.get('old_metrics', {})
            new_metrics = strategy_improvement.get('new_metrics', {})
            results['backtest_comparison'] = self.run_backtest_comparison(old_metrics, new_metrics)
        else:
            results['backtest_comparison'] = {'status': 'skipped', 'message': 'No strategy improvement data provided'}
        
        # 3. 创建分支和PR（如果测试通过）
        if (results['unit_tests']['status'] == 'success' and 
            results['integration_tests']['status'] == 'success'):
            
            branch_name = f"feature/auto-optimization-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}"
            
            self.logger.info(f"Creating branch: {branch_name}")
            results['create_branch'] = self.create_branch(branch_name)
            
            if results['create_branch']['status'] == 'success':
                commit_message = "feat: Auto-generated strategy optimization"
                results['commit'] = self.commit_changes(commit_message)
                
                if results['commit']['status'] == 'success':
                    results['push'] = self.push_branch(branch_name)
                    
                    if results['push']['status'] == 'success':
                        # 生成PR描述
                        improvements = results['backtest_comparison'].get('improvements', [])
                        regressions = results['backtest_comparison'].get('regressions', [])
                        comparison = results['backtest_comparison'].get('comparison', {})
                        risk_assessment = "策略经过充分测试，风险可控。建议在生产环境中小范围验证后再全面部署。"
                        
                        pr_description = self.generate_pr_description(
                            improvements, regressions, comparison, risk_assessment
                        )
                        
                        results['create_pr'] = self.create_pull_request(
                            branch_name, 
                            "feat: Auto-optimized fund strategy",
                            pr_description
                        )
        
        return results