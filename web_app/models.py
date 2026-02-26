"""
Web应用数据模型和分析器
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from agents.data_backtest.fund_data import FundDataFetcher
from agents.data_backtest.backtest_engine import BacktestEngine
from agents.strategy_agent.factor_model import FactorModel
from agents.strategy_agent.fund_scoring import FundScoringSystem
from agents.strategy_agent.style_classification import StyleClassification
from agents.portfolio_agent.portfolio_generator import PortfolioGenerator
from agents.portfolio_agent.weight_optimizer import WeightOptimizer
from agents.risk_agent.stress_testing import StressTesting
from agents.risk_agent.risk_exposure import RiskExposureAnalyzer
from agents.risk_agent.drawdown_control import DrawdownController
from agents.ui_agent.user_interface import UserInterface
from agents.ui_agent.visualization import VisualizationEngine
from agents.ui_agent.risk_disclosure import RiskDisclosureGenerator


class PortfolioAnalyzer:
    """投资组合分析器"""
    
    def __init__(self):
        self.data_fetcher = FundDataFetcher()
        self.backtest_engine = BacktestEngine()
        self.factor_model = FactorModel()
        self.scoring_system = FundScoringSystem()
        self.style_classifier = StyleClassification()
        self.portfolio_generator = PortfolioGenerator()
        self.weight_optimizer = WeightOptimizer()
        self.stress_tester = StressTesting()
        self.risk_analyzer = RiskExposureAnalyzer()
        self.drawdown_controller = DrawdownController()
        self.ui_interface = UserInterface()
        self.viz_engine = VisualizationEngine()
        self.disclosure_gen = RiskDisclosureGenerator()
        
    def analyze_fund_list(self, fund_codes: List[str]) -> Dict:
        """
        分析基金列表
        
        Args:
            fund_codes: 基金代码列表
            
        Returns:
            分析结果字典
        """
        # 获取基金数据
        fund_nav_dict = {}
        fund_basic_info = {}
        fund_backtest_results = {}
        
        for fund_code in fund_codes:
            # 获取净值数据（使用缓存或示例数据）
            nav_data = self.data_fetcher.get_fund_nav_history(fund_code)
            if nav_data.empty:
                # 使用示例数据
                dates = pd.date_range(start='2023-01-01', end='2024-01-01', freq='D')
                np.random.seed(hash(fund_code) % 1000)
                returns = np.random.normal(0.001, 0.02, len(dates))
                nav = [1.0]
                for r in returns[1:]:
                    nav.append(nav[-1] * (1 + r))
                nav_data = pd.DataFrame({'date': dates, 'nav': nav})
                
            fund_nav_dict[fund_code] = nav_data
            
            # 获取基本信息
            basic_info = self.data_fetcher.get_fund_basic_info(fund_code)
            if not basic_info:
                basic_info = {
                    'fund_code': fund_code,
                    'fund_name': f'基金{fund_code}',
                    'fund_type': '混合型',
                    'fund_size': 50.0,
                    'establish_date': '2020-01-01',
                    'sector': 'general'
                }
            fund_basic_info[fund_code] = basic_info
            
            # 回测分析
            backtest_result = self.backtest_engine.backtest_single_fund(fund_code, nav_data)
            fund_backtest_results[fund_code] = backtest_result
            
        return {
            'fund_nav_dict': fund_nav_dict,
            'fund_basic_info': fund_basic_info,
            'fund_backtest_results': fund_backtest_results
        }
    
    def generate_portfolio_analysis(self, fund_codes: List[str], 
                                 mode: str = 'auto', 
                                 preferences: Optional[Dict] = None) -> Dict:
        """
        生成投资组合分析
        
        Args:
            fund_codes: 基金代码列表
            mode: 分析模式 ('auto' 或 'manual')
            preferences: 用户偏好设置
            
        Returns:
            完整分析结果
        """
        # 分析基金数据
        analysis_data = self.analyze_fund_list(fund_codes)
        fund_nav_dict = analysis_data['fund_nav_dict']
        fund_basic_info = analysis_data['fund_basic_info']
        fund_backtest_results = analysis_data['fund_backtest_results']
        
        if mode == 'manual':
            # 手动模式：直接使用提供的基金
            selected_funds = fund_codes
        else:
            # 自动模式：进行因子建模和打分
            fund_scores_data = []
            fund_factors_dict = {}
            
            for fund_code in fund_codes:
                factors = self.factor_model.calculate_all_factors(
                    fund_code,
                    fund_basic_info[fund_code],
                    fund_nav_dict[fund_code],
                    fund_backtest_results[fund_code]
                )
                fund_factors_dict[fund_code] = factors
                
                score_result = self.scoring_system.score_single_fund(
                    fund_code,
                    fund_basic_info[fund_code],
                    fund_nav_dict[fund_code],
                    fund_backtest_results[fund_code]
                )
                
                style_result = self.style_classifier.classify_fund_comprehensive(
                    fund_code,
                    fund_basic_info[fund_code],
                    factors
                )
                
                fund_scores_data.append({
                    'fund_code': fund_code,
                    'composite_score': score_result['composite_score'],
                    'investment_style': style_result['investment_style']
                })
            
            fund_scores_df = pd.DataFrame(fund_scores_data)
            fund_scores_df = fund_scores_df.sort_values('composite_score', ascending=False)
            
            # 选择Top-N基金（默认5只）
            selected_funds = fund_scores_df.head(5)['fund_code'].tolist()
        
        # 生成组合权重
        selected_fund_scores = []
        for fund_code in selected_funds:
            if fund_code in fund_scores_df['fund_code'].values:
                score_row = fund_scores_df[fund_scores_df['fund_code'] == fund_code].iloc[0]
                selected_fund_scores.append({
                    'fund_code': fund_code,
                    'composite_score': score_row['composite_score'],
                    'investment_style': score_row['investment_style']
                })
        
        if selected_fund_scores:
            selected_scores_df = pd.DataFrame(selected_fund_scores)
            portfolio_weights = self.weight_optimizer.optimize_portfolio_weights(
                selected_scores_df, fund_nav_dict, 'risk_parity'
            )
        else:
            # 等权重分配
            portfolio_weights = {fund_code: 1.0/len(selected_funds) for fund_code in selected_funds}
        
        # 构建组合净值
        all_dates = None
        for fund_code in selected_funds:
            if fund_code in fund_nav_dict:
                nav_data = fund_nav_dict[fund_code]
                if all_dates is None:
                    all_dates = set(nav_data['date'])
                else:
                    all_dates = all_dates.intersection(set(nav_data['date']))
        
        if all_dates and len(all_dates) > 1:
            all_dates = sorted(list(all_dates))
            portfolio_nav = []
            
            for date in all_dates:
                weighted_nav = 0.0
                total_weight = 0.0
                
                for fund_code in selected_funds:
                    if fund_code in portfolio_weights and fund_code in fund_nav_dict:
                        weight = portfolio_weights[fund_code]
                        nav_data = fund_nav_dict[fund_code]
                        nav_on_date = nav_data[nav_data['date'] == date]
                        
                        if not nav_on_date.empty:
                            weighted_nav += weight * nav_on_date['nav'].iloc[0]
                            total_weight += weight
                
                if total_weight > 0:
                    normalized_nav = weighted_nav / total_weight
                    portfolio_nav.append(normalized_nav)
            
            portfolio_nav_series = pd.Series(portfolio_nav, index=all_dates)
        else:
            portfolio_nav_series = pd.Series([1.0], index=[pd.Timestamp('2023-01-01')])
        
        # 风险分析
        stress_results = self.stress_tester.run_comprehensive_stress_test(portfolio_nav_series)
        fund_sectors = {code: info['sector'] for code, info in fund_basic_info.items()}
        exposure_results = self.risk_analyzer.comprehensive_risk_exposure_analysis(
            portfolio_weights,
            fund_factors_dict,
            fund_sectors,
            fund_nav_dict
        )
        
        # 计算组合整体指标
        portfolio_results = {
            'annual_return': sum(
                fund_backtest_results[code]['annual_return'] * weight 
                for code, weight in portfolio_weights.items() 
                if code in fund_backtest_results
            ),
            'volatility': exposure_results.get('correlation_risk', {}).get('avg_correlation', 0.2),
            'max_drawdown': min([v for k, v in stress_results.items() if k.endswith('_max_drawdown')]),
            'sharpe_ratio': sum(
                fund_backtest_results[code]['sharpe_ratio'] * weight 
                for code, weight in portfolio_weights.items() 
                if code in fund_backtest_results
            )
        }
        
        # 生成可视化数据
        analysis_results = {
            'portfolio_results': portfolio_results,
            'portfolio_weights': portfolio_weights,
            'factor_exposure': exposure_results.get('factor_exposure', {}),
            'stress_test_results': stress_results,
            'sector_concentration': exposure_results.get('sector_concentration', {}),
            'selected_funds': selected_funds,
            'fund_details': {code: {
                'name': fund_basic_info[code]['fund_name'],
                'type': fund_basic_info[code]['fund_type'],
                'size': fund_basic_info[code]['fund_size'],
                'backtest_results': fund_backtest_results[code]
            } for code in selected_funds}
        }
        
        charts_data = self.viz_engine.generate_comprehensive_report(analysis_results)
        risk_disclosure = self.disclosure_gen.generate_comprehensive_risk_disclosure(analysis_results)
        
        return {
            'analysis_results': analysis_results,
            'charts_data': charts_data,
            'risk_disclosure': risk_disclosure,
            'mode': mode
        }