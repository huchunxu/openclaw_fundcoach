#!/usr/bin/env python3
"""
Risk Agent - 风险评估和控制
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
import logging

class RiskAgent:
    """风险智能体：负责极端行情模拟、风险暴露分析和回撤控制"""
    
    def __init__(self):
        self.stress_scenarios = {
            'market_crash': -0.3,      # 市场崩盘：-30%
            'volatility_spike': 2.0,   # 波动率飙升：2倍
            'liquidity_crisis': -0.15, # 流动性危机：-15%
            'sector_rotation': 0.2     # 行业轮动：20%偏移
        }
        self.logger = logging.getLogger(__name__)
    
    def calculate_portfolio_metrics(self, portfolio_weights: Dict[str, float], 
                                 fund_returns: Dict[str, List[float]]) -> Dict:
        """计算组合风险指标"""
        # 获取组合收益序列
        portfolio_returns = self._calculate_portfolio_returns(portfolio_weights, fund_returns)
        
        # 年化收益率
        annual_return = np.mean(portfolio_returns) * 252
        
        # 波动率
        volatility = np.std(portfolio_returns) * np.sqrt(252)
        
        # 夏普率（假设无风险利率为0）
        sharpe_ratio = annual_return / volatility if volatility > 0 else 0
        
        # 最大回撤
        cumulative = np.cumprod(1 + np.array(portfolio_returns))
        running_max = np.maximum.accumulate(cumulative)
        drawdowns = (cumulative - running_max) / running_max
        max_drawdown = drawdowns.min()
        
        return {
            'annual_return': annual_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'portfolio_returns': portfolio_returns.tolist()
        }
    
    def _calculate_portfolio_returns(self, weights: Dict[str, float], 
                                  fund_returns: Dict[str, List[float]]) -> np.ndarray:
        """计算组合收益序列"""
        # 找到最短的收益序列长度
        min_length = min(len(returns) for returns in fund_returns.values() if returns)
        
        # 截断到相同长度
        aligned_returns = {}
        for fund_code, returns in fund_returns.items():
            if fund_code in weights and weights[fund_code] > 0:
                aligned_returns[fund_code] = returns[:min_length]
        
        # 计算加权组合收益
        portfolio_returns = np.zeros(min_length)
        for fund_code, weight in weights.items():
            if fund_code in aligned_returns:
                portfolio_returns += weight * np.array(aligned_returns[fund_code])
        
        return portfolio_returns
    
    def run_stress_test(self, portfolio_weights: Dict[str, float], 
                       fund_returns: Dict[str, List[float]]) -> Dict:
        """运行压力测试"""
        results = {}
        
        for scenario, impact in self.stress_scenarios.items():
            if scenario == 'market_crash':
                # 市场崩盘：所有资产同步下跌
                stressed_returns = {}
                for fund_code, returns in fund_returns.items():
                    stressed_returns[fund_code] = [r + impact for r in returns]
                
                metrics = self.calculate_portfolio_metrics(portfolio_weights, stressed_returns)
                results[scenario] = {
                    'max_drawdown': metrics['max_drawdown'],
                    'description': f'市场整体下跌{abs(impact)*100:.0f}%'
                }
            
            elif scenario == 'volatility_spike':
                # 波动率飙升：放大波动但保持均值
                stressed_returns = {}
                for fund_code, returns in fund_returns.items():
                    mean_return = np.mean(returns)
                    std_return = np.std(returns)
                    stressed_returns[fund_code] = [
                        mean_return + impact * (r - mean_return) for r in returns
                    ]
                
                metrics = self.calculate_portfolio_metrics(portfolio_weights, stressed_returns)
                results[scenario] = {
                    'volatility': metrics['volatility'],
                    'description': f'波动率放大{impact:.1f}倍'
                }
            
            elif scenario == 'liquidity_crisis':
                # 流动性危机：普遍下跌但程度较轻
                stressed_returns = {}
                for fund_code, returns in fund_returns.items():
                    stressed_returns[fund_code] = [r + impact for r in returns]
                
                metrics = self.calculate_portfolio_metrics(portfolio_weights, stressed_returns)
                results[scenario] = {
                    'max_drawdown': metrics['max_drawdown'],
                    'description': f'流动性危机导致下跌{abs(impact)*100:.0f}%'
                }
            
            elif scenario == 'sector_rotation':
                # 行业轮动：随机调整不同基金的表现
                stressed_returns = {}
                for fund_code, returns in fund_returns.items():
                    # 随机偏移，有些基金受益，有些受损
                    offset = np.random.normal(0, impact, len(returns))
                    stressed_returns[fund_code] = [r + o for r, o in zip(returns, offset)]
                
                metrics = self.calculate_portfolio_metrics(portfolio_weights, stressed_returns)
                results[scenario] = {
                    'volatility': metrics['volatility'],
                    'description': '行业轮动导致表现分化'
                }
        
        return results
    
    def analyze_risk_exposure(self, portfolio_weights: Dict[str, float], 
                            fund_styles: Dict[str, str]) -> Dict:
        """分析风险暴露"""
        # 风格集中度
        style_exposure = {}
        for fund_code, weight in portfolio_weights.items():
            if fund_code in fund_styles:
                style = fund_styles[fund_code]
                style_exposure[style] = style_exposure.get(style, 0) + weight
        
        # 行业集中度（简化：假设每个基金代表一个行业）
        industry_concentration = max(portfolio_weights.values()) if portfolio_weights else 0
        
        # 因子暴露分析
        factor_exposure = self._analyze_factor_exposure(portfolio_weights)
        
        return {
            'style_exposure': style_exposure,
            'industry_concentration': industry_concentration,
            'factor_exposure': factor_exposure
        }
    
    def _analyze_factor_exposure(self, portfolio_weights: Dict[str, float]) -> Dict:
        """分析因子暴露（简化版本）"""
        # 在实际应用中，这里会分析对各种风险因子的暴露
        # 目前简化为返回权重分布信息
        total_weight = sum(portfolio_weights.values())
        if total_weight == 0:
            return {'diversification': 0}
        
        # 分散度指标：权重越均匀，分散度越高
        weights_array = np.array(list(portfolio_weights.values()))
        diversification = 1 - np.sum(weights_array ** 2)  # Herfindahl指数的反向
        
        return {'diversification': diversification}
    
    def check_risk_limits(self, risk_metrics: Dict, stress_results: Dict) -> Dict:
        """检查风险限制"""
        alerts = []
        
        # 最大回撤限制
        if risk_metrics['max_drawdown'] < -0.25:
            alerts.append(f"最大回撤过高: {risk_metrics['max_drawdown']:.2%}")
        
        # 波动率限制
        if risk_metrics['volatility'] > 0.3:
            alerts.append(f"波动率过高: {risk_metrics['volatility']:.2%}")
        
        # 压力测试结果检查
        for scenario, result in stress_results.items():
            if 'max_drawdown' in result and result['max_drawdown'] < -0.35:
                alerts.append(f"压力测试失败 - {scenario}: {result['max_drawdown']:.2%}")
        
        return {
            'alerts': alerts,
            'risk_level': self._determine_risk_level(risk_metrics, len(alerts))
        }
    
    def _determine_risk_level(self, metrics: Dict, alert_count: int) -> str:
        """确定风险等级"""
        if alert_count >= 2:
            return "high"
        elif metrics['max_drawdown'] < -0.2 or metrics['volatility'] > 0.25:
            return "medium"
        else:
            return "low"
    
    def generate_risk_report(self, portfolio_weights: Dict[str, float], 
                           fund_pool: Dict, strategy_results: Dict) -> Dict:
        """生成完整风险报告"""
        # 获取基金收益数据
        fund_returns = {}
        fund_styles = {}
        for fund_code in portfolio_weights.keys():
            if fund_code in fund_pool:
                fund_returns[fund_code] = fund_pool[fund_code]['returns']
            if fund_code in strategy_results:
                fund_styles[fund_code] = strategy_results[fund_code]['style']
        
        # 计算基础风险指标
        risk_metrics = self.calculate_portfolio_metrics(portfolio_weights, fund_returns)
        
        # 运行压力测试
        stress_results = self.run_stress_test(portfolio_weights, fund_returns)
        
        # 分析风险暴露
        exposure_analysis = self.analyze_risk_exposure(portfolio_weights, fund_styles)
        
        # 检查风险限制
        risk_check = self.check_risk_limits(risk_metrics, stress_results)
        
        return {
            'risk_metrics': risk_metrics,
            'stress_test': stress_results,
            'exposure_analysis': exposure_analysis,
            'risk_assessment': risk_check
        }