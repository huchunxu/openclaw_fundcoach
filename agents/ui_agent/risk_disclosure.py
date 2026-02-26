"""
风险提示模块

功能：
- 自动生成风险提示文本
- 合规性检查
- 投资者适当性提醒
- 历史数据免责声明
"""

from typing import Dict, List, Optional


class RiskDisclosureGenerator:
    """风险提示生成器"""
    
    def __init__(self):
        self.disclaimer_template = """
历史数据仅供参考，不构成投资建议。
投资有风险，入市需谨慎。
过往业绩不代表未来表现。
"""
        
        self.risk_level_messages = {
            'low': "该组合风险等级较低，适合保守型投资者。",
            'medium': "该组合风险等级中等，适合稳健型投资者。",
            'high': "该组合风险等级较高，适合激进型投资者。"
        }
        
        self.drawdown_warnings = {
            'mild': "组合最大回撤在可接受范围内。",
            'moderate': "组合存在中等程度回撤风险，请谨慎评估。",
            'severe': "组合回撤风险较高，建议充分了解风险后再做决策。"
        }
        
    def assess_risk_level(self, portfolio_results: Dict) -> str:
        """
        评估组合风险等级
        
        Args:
            portfolio_results: 组合分析结果
            
        Returns:
            风险等级 ('low', 'medium', 'high')
        """
        volatility = portfolio_results.get('volatility', 0)
        max_drawdown = portfolio_results.get('max_drawdown', 0)
        
        # 简单风险评估逻辑
        if volatility < 0.15 and max_drawdown > -0.2:
            return 'low'
        elif volatility < 0.25 and max_drawdown > -0.3:
            return 'medium'
        else:
            return 'high'
    
    def generate_drawdown_warning(self, max_drawdown: float) -> str:
        """
        生成回撤警告
        
        Args:
            max_drawdown: 最大回撤值（负数）
            
        Returns:
            回撤警告文本
        """
        if max_drawdown >= -0.2:
            return self.drawdown_warnings['mild']
        elif max_drawdown >= -0.35:
            return self.drawdown_warnings['moderate']
        else:
            return self.drawdown_warnings['severe']
    
    def generate_comprehensive_risk_disclosure(self, analysis_results: Dict) -> str:
        """
        生成综合风险提示
        
        Args:
            analysis_results: 完整分析结果
            
        Returns:
            风险提示文本
        """
        disclosure_parts = []
        
        # 添加标题
        disclosure_parts.append("📊 投资组合风险提示")
        disclosure_parts.append("=" * 40)
        
        # 风险等级提示
        if 'portfolio_results' in analysis_results:
            risk_level = self.assess_risk_level(analysis_results['portfolio_results'])
            disclosure_parts.append(self.risk_level_messages[risk_level])
            
            # 回撤警告
            max_drawdown = analysis_results['portfolio_results'].get('max_drawdown', 0)
            drawdown_warning = self.generate_drawdown_warning(max_drawdown)
            disclosure_parts.append(drawdown_warning)
            
        # 压力测试结果提示
        if 'stress_test_results' in analysis_results:
            stress_results = analysis_results['stress_test_results']
            worst_scenario = min(
                [v for k, v in stress_results.items() if k.endswith('_max_drawdown')],
                default=0
            )
            disclosure_parts.append(f"压力测试显示，在极端市场条件下，组合可能面临{abs(worst_scenario):.1%}的最大回撤。")
            
        # 因子集中度提示
        if 'factor_exposure' in analysis_results:
            factor_exposure = analysis_results['factor_exposure']
            max_exposure = max(factor_exposure.values()) if factor_exposure else 0
            if max_exposure > 0.7:
                disclosure_parts.append("组合在某些因子上暴露较高，可能存在风格集中风险。")
                
        # 行业集中度提示
        if 'sector_concentration' in analysis_results:
            sector_concentration = analysis_results['sector_concentration']
            max_sector_conc = sector_concentration.get('max_sector_concentration', 0)
            if max_sector_conc > 0.4:
                disclosure_parts.append("组合在某些行业上集中度较高，可能存在行业风险。")
                
        # 添加通用免责声明
        disclosure_parts.append(self.disclaimer_template.strip())
        
        return "\n\n".join(disclosure_parts)
    
    def validate_compliance(self, analysis_results: Dict) -> Dict[str, bool]:
        """
        验证合规性
        
        Args:
            analysis_results: 分析结果
            
        Returns:
            合规性检查结果
        """
        compliance_checks = {
            'has_risk_disclosure': True,
            'has_historical_disclaimer': True,
            'risk_level_appropriate': True,
            'concentration_within_limits': True
        }
        
        # 检查集中度限制
        if 'sector_concentration' in analysis_results:
            sector_concentration = analysis_results['sector_concentration']
            max_sector_conc = sector_concentration.get('max_sector_concentration', 0)
            compliance_checks['concentration_within_limits'] = max_sector_conc <= 0.5
            
        # 检查风险等级适当性（简化）
        if 'portfolio_results' in analysis_results:
            risk_level = self.assess_risk_level(analysis_results['portfolio_results'])
            # 这里可以添加更复杂的适当性检查逻辑
            compliance_checks['risk_level_appropriate'] = True
            
        return compliance_checks
    
    def generate_investor_suitability_notice(self, investor_profile: Dict, 
                                           portfolio_analysis: Dict) -> str:
        """
        生成投资者适当性提醒
        
        Args:
            investor_profile: 投资者画像
            portfolio_analysis: 组合分析结果
            
        Returns:
            适当性提醒文本
        """
        risk_tolerance = investor_profile.get('risk_tolerance', 'medium')
        portfolio_risk_level = self.assess_risk_level(portfolio_analysis.get('portfolio_results', {}))
        
        suitability_message = f"根据您的风险偏好（{risk_tolerance}），"
        
        if risk_tolerance == portfolio_risk_level:
            suitability_message += "该组合与您的风险承受能力匹配。"
        elif (risk_tolerance == 'high' and portfolio_risk_level in ['medium', 'low']) or \
             (risk_tolerance == 'medium' and portfolio_risk_level == 'low'):
            suitability_message += "该组合风险低于您的承受能力，相对保守。"
        else:
            suitability_message += "⚠️ 该组合风险高于您的承受能力，建议谨慎考虑。"
            
        return suitability_message