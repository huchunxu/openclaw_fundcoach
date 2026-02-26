"""
可视化模块

功能：
- 风险收益曲线绘制
- 组合权重饼图
- 因子暴露热力图
- 回撤分析图表
- 压力测试结果可视化
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import json


class VisualizationEngine:
    """可视化引擎"""
    
    def __init__(self):
        pass
        
    def generate_risk_return_chart(self, portfolio_results: Dict) -> Dict:
        """
        生成风险收益曲线数据
        
        Args:
            portfolio_results: 组合回测结果
            
        Returns:
            图表数据字典
        """
        chart_data = {
            'chart_type': 'risk_return_scatter',
            'data': {
                'x': portfolio_results.get('volatility', 0),
                'y': portfolio_results.get('annual_return', 0),
                'label': 'Portfolio',
                'color': '#2196F3'
            },
            'layout': {
                'title': 'Risk-Return Profile',
                'xaxis_title': 'Annual Volatility',
                'yaxis_title': 'Annual Return',
                'xaxis_tickformat': '.1%',
                'yaxis_tickformat': '.1%'
            }
        }
        return chart_data
    
    def generate_weight_pie_chart(self, portfolio_weights: Dict[str, float]) -> Dict:
        """
        生成组合权重饼图数据
        
        Args:
            portfolio_weights: 组合权重字典
            
        Returns:
            饼图数据字典
        """
        labels = list(portfolio_weights.keys())
        values = list(portfolio_weights.values())
        
        # 过滤掉权重过小的基金（小于1%）
        filtered_labels = []
        filtered_values = []
        others_weight = 0.0
        
        for label, value in zip(labels, values):
            if value >= 0.01:
                filtered_labels.append(label)
                filtered_values.append(value)
            else:
                others_weight += value
                
        if others_weight > 0:
            filtered_labels.append('Others')
            filtered_values.append(others_weight)
            
        chart_data = {
            'chart_type': 'pie',
            'data': {
                'labels': filtered_labels,
                'values': filtered_values
            },
            'layout': {
                'title': 'Portfolio Weight Distribution'
            }
        }
        return chart_data
    
    def generate_factor_exposure_heatmap(self, factor_exposure: Dict[str, float]) -> Dict:
        """
        生成因子暴露热力图数据
        
        Args:
            factor_exposure: 因子暴露字典
            
        Returns:
            热力图数据字典
        """
        factors = list(factor_exposure.keys())
        exposures = list(factor_exposure.values())
        
        # 归一化到-1到1范围用于颜色映射
        normalized_exposures = []
        for exp in exposures:
            # 假设因子暴露在0-1范围内，转换为-1到1
            normalized = (exp - 0.5) * 2
            normalized_exposures.append(max(-1, min(1, normalized)))
            
        chart_data = {
            'chart_type': 'heatmap',
            'data': {
                'x': ['Exposure'],
                'y': factors,
                'z': [normalized_exposures]
            },
            'layout': {
                'title': 'Factor Exposure Analysis',
                'colorscale': 'RdBu'
            }
        }
        return chart_data
    
    def generate_drawdown_chart(self, nav_series: pd.Series) -> Dict:
        """
        生成回撤分析图表数据
        
        Args:
            nav_series: 净值序列
            
        Returns:
            回撤图表数据字典
        """
        if nav_series.empty:
            return {}
            
        # 计算回撤
        rolling_max = nav_series.expanding().max()
        drawdown = (nav_series - rolling_max) / rolling_max
        
        dates = nav_series.index.strftime('%Y-%m-%d').tolist()
        nav_values = nav_series.values.tolist()
        drawdown_values = drawdown.values.tolist()
        
        chart_data = {
            'chart_type': 'dual_axis',
            'data': {
                'dates': dates,
                'nav': nav_values,
                'drawdown': drawdown_values
            },
            'layout': {
                'title': 'Portfolio Performance and Drawdown',
                'yaxis1_title': 'Net Asset Value',
                'yaxis2_title': 'Drawdown',
                'yaxis2_tickformat': '.1%'
            }
        }
        return chart_data
    
    def generate_stress_test_comparison(self, stress_results: Dict) -> Dict:
        """
        生成压力测试对比图表数据
        
        Args:
            stress_results: 压力测试结果
            
        Returns:
            对比图表数据字典
        """
        scenarios = []
        max_drawdowns = []
        
        for key, value in stress_results.items():
            if key.endswith('_max_drawdown'):
                scenario_name = key.replace('_max_drawdown', '')
                scenarios.append(scenario_name)
                max_drawdowns.append(value)
                
        chart_data = {
            'chart_type': 'bar',
            'data': {
                'x': scenarios,
                'y': max_drawdowns
            },
            'layout': {
                'title': 'Stress Test Results - Maximum Drawdown',
                'yaxis_tickformat': '.1%'
            }
        }
        return chart_data
    
    def generate_comprehensive_report(self, analysis_results: Dict) -> Dict:
        """
        生成综合可视化报告
        
        Args:
            analysis_results: 完整分析结果
            
        Returns:
            综合报告数据字典
        """
        report = {}
        
        # 风险收益图表
        if 'portfolio_results' in analysis_results:
            report['risk_return_chart'] = self.generate_risk_return_chart(
                analysis_results['portfolio_results']
            )
            
        # 权重分布
        if 'portfolio_weights' in analysis_results:
            report['weight_pie_chart'] = self.generate_weight_pie_chart(
                analysis_results['portfolio_weights']
            )
            
        # 因子暴露
        if 'factor_exposure' in analysis_results:
            report['factor_exposure_heatmap'] = self.generate_factor_exposure_heatmap(
                analysis_results['factor_exposure']
            )
            
        # 压力测试
        if 'stress_test_results' in analysis_results:
            report['stress_test_comparison'] = self.generate_stress_test_comparison(
                analysis_results['stress_test_results']
            )
            
        # 回撤分析（如果有净值数据）
        if 'portfolio_nav_series' in analysis_results:
            report['drawdown_chart'] = self.generate_drawdown_chart(
                analysis_results['portfolio_nav_series']
            )
            
        return report
    
    def export_charts_to_json(self, charts_data: Dict, filename: str = 'charts.json') -> str:
        """
        导出图表数据到JSON文件
        
        Args:
            charts_data: 图表数据字典
            filename: 输出文件名
            
        Returns:
            文件路径
        """
        try:
            with open(filename, 'w') as f:
                json.dump(charts_data, f, indent=2)
            return filename
        except Exception as e:
            print(f"导出图表数据失败: {e}")
            return ""