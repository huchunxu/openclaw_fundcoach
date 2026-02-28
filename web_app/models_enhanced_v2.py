"""
Web应用数据模型和分析器 - 增强版本
支持扩展的数据缓存和增强的Agent模块
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# 导入增强版模块
from enhanced_data_fetcher import EnhancedDataFetcher
from enhanced_backtest_engine import EnhancedBacktestEngine
from agents.strategy_agent.factor_model_enhanced import EnhancedFactorModel
from agents.strategy_agent.fund_scoring_enhanced import EnhancedFundScoringSystem
from agents.portfolio_agent.portfolio_generator_enhanced import EnhancedPortfolioGenerator
from agents.portfolio_agent.weight_optimizer_enhanced import EnhancedWeightOptimizer
from agents.risk_agent.stress_testing_enhanced import EnhancedStressTesting
from agents.risk_agent.risk_exposure_enhanced import EnhancedRiskExposureAnalyzer


class EnhancedPortfolioAnalyzer:
    """增强版投资组合分析器"""
    
    def __init__(self):
        self.data_fetcher = EnhancedDataFetcher()
        self.backtest_engine = EnhancedBacktestEngine()
        self.factor_model = EnhancedFactorModel()
        self.scoring_system = EnhancedFundScoringSystem()
        self.portfolio_generator = EnhancedPortfolioGenerator()
        self.weight_optimizer = EnhancedWeightOptimizer()
        self.stress_tester = EnhancedStressTesting()
        self.risk_analyzer = EnhancedRiskExposureAnalyzer()
        
    def get_all_available_funds(self) -> List[Dict]:
        """
        获取所有可用的基金列表（从数据缓存中）
        """
        cache_dir = "data_cache"
        if not os.path.exists(cache_dir):
            return []
            
        fund_list = []
        for filename in os.listdir(cache_dir):
            if filename.endswith('.csv'):
                fund_code = filename.replace('.csv', '')
                # 读取基金基本信息
                try:
                    df = pd.read_csv(os.path.join(cache_dir, filename))
                    if not df.empty:
                        fund_info = {
                            'fund_code': fund_code,
                            'fund_name': f'基金{fund_code}',
                            'fund_type': '混合型',
                            'data_points': len(df),
                            'date_range': f"{df['date'].min()} to {df['date'].max()}"
                        }
                        fund_list.append(fund_info)
                except Exception as e:
                    continue
                    
        return fund_list
    
    def analyze_fund_list(self, fund_codes: List[str]) -> Dict:
        """
        分析基金列表（使用增强数据源）
        """
        fund_nav_dict = {}
        fund_basic_info = {}
        fund_backtest_results = {}
        
        for fund_code in fund_codes:
            # 从增强数据抓取器获取数据
            nav_data = self.data_fetcher.load_cached_data(fund_code)
            if nav_data is None or nav_data.empty:
                # 如果缓存中没有，尝试获取新数据
                nav_data = self.data_fetcher.fetch_fund_data_with_fallback(fund_code)
                
            if nav_data is None or nav_data.empty:
                # 最后使用示例数据
                dates = pd.date_range(start='2023-01-01', end='2024-01-01', freq='D')
                np.random.seed(hash(fund_code) % 1000)
                returns = np.random.normal(0.001, 0.02, len(dates))
                nav = [1.0]
                for r in returns[1:]:
                    nav.append(nav[-1] * (1 + r))
                nav_data = pd.DataFrame({'date': dates, 'nav': nav})
                
            fund_nav_dict[fund_code] = nav_data
            
            # 获取基本信息
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
        生成投资组合分析（使用增强模块）
        """
        # 分析基金数据
        analysis_data = self.analyze_fund_list(fund_codes)
        fund_nav_dict = analysis_data['fund_nav_dict']
        fund_basic_info = analysis_data['fund_basic_info']
        fund_backtest_results = analysis_data['fund_backtest_results']
        
        if mode == 'manual':
            selected_funds = fund_codes
        else:
            # 使用增强的策略代理
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
                
                score_result = self.scoring_system.score_single_fund_enhanced(
                    fund_code,
                    fund_basic_info[fund_code],
                    fund_nav_dict[fund_code],
                    fund_backtest_results[fund_code]
                )
                
                fund_scores_data.append({
                    'fund_code': fund_code,
                    'composite_score': score_result['composite_score'],
                    'investment_style': 'balanced'  # 简化处理
                })
            
            fund_scores_df = pd.DataFrame(fund_scores_data)
            fund_scores_df = fund_scores_df.sort_values('composite_score', ascending=False)
            selected_funds = fund_scores_df.head(5)['fund_code'].tolist()
        
        # 使用增强的组合代理
        portfolio_weights = self.weight_optimizer.optimize_portfolio_weights_enhanced(
            fund_scores_df, fund_nav_dict, 'enhanced_risk_parity'
        )
        
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
        
        # 使用增强的风险代理
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
        
        return {
            'analysis_results': analysis_results,
            'mode': mode
        }