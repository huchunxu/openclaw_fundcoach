#!/usr/bin/env python3
"""
增强的策略分析 API - 整合因子分析、组合优化、风险评估
"""

import os
import sys
import json
import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Dict, Optional

sys.path.insert(0, os.path.dirname(__file__))


class StrategyAnalyzer:
    """策略分析器 - 因子分析、基金评分、组合优化"""
    
    def __init__(self, cache_dir: str = 'data_cache'):
        self.cache_dir = cache_dir
        self.funds_data = {}
        self.analysis_results = {}
        
    def load_fund_data(self, fund_code: str) -> Optional[pd.DataFrame]:
        """加载单只基金数据"""
        filepath = os.path.join(self.cache_dir, f'{fund_code}.csv')
        if not os.path.exists(filepath):
            return None
        try:
            df = pd.read_csv(filepath, parse_dates=['date'])
            return df.sort_values('date')
        except Exception as e:
            print(f"加载基金{fund_code}数据失败：{e}")
            return None
    
    def calculate_factors(self, fund_code: str, df: pd.DataFrame) -> Dict:
        """计算单只基金的因子指标"""
        if len(df) < 30:
            return None
            
        nav = df['nav'].values
        dates = df['date'].values
        
        # 收益率计算
        returns = np.diff(nav) / nav[:-1]
        total_return = (nav[-1] / nav[0] - 1) * 100
        
        # 年化收益率
        days = (pd.Timestamp(dates[-1]) - pd.Timestamp(dates[0])).days
        annual_return = ((1 + total_return/100) ** (365/max(days, 1)) - 1) * 100
        
        # 波动率
        volatility = np.std(returns) * np.sqrt(252) * 100 if len(returns) > 0 else 0
        
        # 夏普比率
        if np.std(returns) > 0:
            sharpe = (np.mean(returns) / np.std(returns)) * np.sqrt(252)
        else:
            sharpe = 0
        
        # 最大回撤
        peak = np.maximum.accumulate(nav)
        drawdown = (nav - peak) / peak * 100
        max_drawdown = np.min(drawdown)
        
        # 卡玛比率 (收益/最大回撤)
        calmar = annual_return / abs(max_drawdown) if max_drawdown != 0 else 0
        
        # 胜率
        positive_days = np.sum(returns > 0)
        win_rate = positive_days / len(returns) * 100 if len(returns) > 0 else 0
        
        return {
            'fund_code': fund_code,
            'total_return': round(total_return, 2),
            'annual_return': round(annual_return, 2),
            'volatility': round(volatility, 2),
            'sharpe': round(sharpe, 2),
            'max_drawdown': round(max_drawdown, 2),
            'calmar': round(calmar, 2),
            'win_rate': round(win_rate, 2),
            'data_points': len(df),
            'start_date': str(dates[0])[:10],
            'end_date': str(dates[-1])[:10]
        }
    
    def analyze_all_funds(self, limit: int = 300) -> List[Dict]:
        """分析所有缓存基金"""
        print(f"📊 开始分析基金数据...")
        
        cache_files = [f for f in os.listdir(self.cache_dir) if f.endswith('.csv')]
        results = []
        
        for i, f in enumerate(cache_files[:limit]):
            fund_code = f.replace('.csv', '')
            df = self.load_fund_data(fund_code)
            if df is not None:
                factors = self.calculate_factors(fund_code, df)
                if factors:
                    results.append(factors)
            
            if (i + 1) % 50 == 0:
                print(f"  进度：{i+1}/{min(len(cache_files), limit)}")
        
        print(f"✅ 完成分析 {len(results)} 只基金")
        self.analysis_results = results
        return results
    
    def calculate_composite_score(self, funds: List[Dict]) -> List[Dict]:
        """计算综合评分"""
        if not funds:
            return []
        
        df = pd.DataFrame(funds)
        
        # 归一化各指标 (0-1)
        def normalize(series, higher_better=True):
            min_val = series.min()
            max_val = series.max()
            if max_val - min_val < 0.001:
                return pd.Series([0.5] * len(series))
            if higher_better:
                return (series - min_val) / (max_val - min_val)
            else:
                return 1 - (series - min_val) / (max_val - min_val)
        
        df['score_return'] = normalize(df['annual_return'])
        df['score_sharpe'] = normalize(df['sharpe'])
        df['score_drawdown'] = normalize(df['max_drawdown'], higher_better=False)
        df['score_volatility'] = normalize(df['volatility'], higher_better=False)
        df['score_calmar'] = normalize(df['calmar'])
        
        # 综合评分 (权重可调)
        weights = {
            'score_return': 0.25,
            'score_sharpe': 0.25,
            'score_drawdown': 0.20,
            'score_volatility': 0.15,
            'score_calmar': 0.15
        }
        
        df['composite_score'] = sum(df[k] * v for k, v in weights.items())
        df['composite_score'] = round(df['composite_score'], 3)
        
        # 排序
        df = df.sort_values('composite_score', ascending=False)
        
        return df.to_dict('records')
    
    def generate_portfolio(self, top_n: int = 10, method: str = 'equal') -> Dict:
        """生成优化组合"""
        if not self.analysis_results:
            self.analyze_all_funds()
        
        scored_funds = self.calculate_composite_score(self.analysis_results)
        top_funds = scored_funds[:top_n]
        
        if method == 'equal':
            # 等权重
            weight = 1.0 / top_n
            portfolio = [{'fund_code': f['fund_code'], 'weight': round(weight, 4)} for f in top_funds]
        elif method == 'score_weighted':
            # 按评分加权
            total_score = sum(f['composite_score'] for f in top_funds)
            portfolio = [{
                'fund_code': f['fund_code'],
                'weight': round(f['composite_score'] / total_score, 4)
            } for f in top_funds]
        else:
            portfolio = [{'fund_code': f['fund_code'], 'weight': round(1.0/top_n, 4)} for f in top_funds]
        
        return {
            'method': method,
            'funds': portfolio,
            'total_funds': len(portfolio),
            'generated_at': datetime.now().isoformat()
        }
    
    def backtest_portfolio(self, portfolio: List[Dict]) -> Dict:
        """回测组合表现"""
        print("📈 运行组合回测...")
        
        # 加载所有基金数据
        fund_navs = {}
        fund_returns = {}
        for item in portfolio:
            fund_code = item['fund_code']
            df = self.load_fund_data(fund_code)
            if df is not None and len(df) > 1:
                # 提取日期和净值
                dates = df['date'].apply(lambda x: str(x)[:10]).values
                navs = df['nav'].values
                fund_navs[fund_code] = dict(zip(dates, navs))
        
        if not fund_navs:
            return {'error': '无法加载基金数据', 'total_return': 0, 'sharpe': 0, 'max_drawdown': 0}
        
        # 找到共同日期
        all_dates = set()
        for fund_code, nav_dict in fund_navs.items():
            all_dates.update(nav_dict.keys())
        common_dates = sorted(list(all_dates))
        
        if len(common_dates) < 10:
            return {'error': '共同交易日太少', 'total_return': 0, 'sharpe': 0, 'max_drawdown': 0}
        
        # 构建收益矩阵
        returns_data = []
        for i in range(1, len(common_dates)):
            daily_returns = []
            for item in portfolio:
                fund_code = item['fund_code']
                weight = item['weight']
                prev_nav = fund_navs[fund_code].get(common_dates[i-1], None)
                curr_nav = fund_navs[fund_code].get(common_dates[i], None)
                if prev_nav and curr_nav and prev_nav > 0:
                    daily_ret = (curr_nav - prev_nav) / prev_nav * weight
                    daily_returns.append(daily_ret)
            if daily_returns:
                returns_data.append({'date': common_dates[i], 'return': sum(daily_returns)})
        
        if not returns_data:
            return {'error': '无法计算收益', 'total_return': 0, 'sharpe': 0, 'max_drawdown': 0}
        
        returns_df = pd.DataFrame(returns_data)
        
        # 累计净值
        cumulative = (1 + returns_df['return']).cumprod()
        
        # 计算指标
        total_return = (cumulative.iloc[-1] - 1) * 100
        days = len(cumulative)
        annual_return = ((1 + total_return/100) ** (252/max(days, 1)) - 1) * 100
        volatility = returns_df['return'].std() * np.sqrt(252) * 100
        sharpe = annual_return / volatility if volatility > 0 else 0
        
        # 最大回撤
        peak = cumulative.cummax()
        drawdown = (cumulative - peak) / peak * 100
        max_drawdown = drawdown.min()
        
        # 生成净值曲线数据 (采样 100 个点)
        step = max(1, len(cumulative) // 100)
        chart_data = [
            {'date': returns_df['date'].iloc[i], 'nav': round(float(cumulative.iloc[i]), 4)}
            for i in range(0, len(cumulative), step)
        ]
        
        return {
            'total_return': round(float(total_return), 2),
            'annual_return': round(float(annual_return), 2),
            'volatility': round(float(volatility), 2),
            'sharpe': round(float(sharpe), 2),
            'max_drawdown': round(float(max_drawdown), 2),
            'data_points': len(cumulative),
            'chart_data': chart_data
        }
    
    def risk_assessment(self, portfolio: List[Dict]) -> Dict:
        """风险评估"""
        print("⚠️ 进行风险评估...")
        
        # 压力测试场景
        scenarios = [
            {'name': '温和下跌', 'market_return': -0.10},
            {'name': '严重下跌', 'market_return': -0.20},
            {'name': '极端暴跌', 'market_return': -0.30},
            {'name': '温和上涨', 'market_return': 0.10},
            {'name': '大幅上涨', 'market_return': 0.20},
        ]
        
        # 估算组合 Beta (简化：假设 0.85)
        portfolio_beta = 0.85
        
        stress_results = []
        for scenario in scenarios:
            impact = scenario['market_return'] * portfolio_beta
            stress_results.append({
                'scenario': scenario['name'],
                'market_change': f"{scenario['market_return']*100:.0f}%",
                'estimated_impact': f"{impact*100:.2f}%"
            })
        
        # 风险指标
        risk_metrics = {
            'concentration_risk': '中等' if len(portfolio) >= 10 else '较高',
            'fund_count': len(portfolio),
            'estimated_beta': portfolio_beta,
            'style_exposure': '偏股型混合',
            'liquidity_risk': '低'
        }
        
        return {
            'stress_test': stress_results,
            'risk_metrics': risk_metrics,
            'assessment_date': datetime.now().isoformat()
        }
    
    def full_analysis(self, top_n: int = 10, weight_method: str = 'equal') -> Dict:
        """完整分析流程"""
        print("=" * 60)
        print("🚀 启动完整策略分析流程")
        print("=" * 60)
        
        # 1. 分析所有基金
        self.analyze_all_funds()
        
        # 2. 计算评分
        scored_funds = self.calculate_composite_score(self.analysis_results)
        top_funds = scored_funds[:top_n]
        
        # 3. 生成组合
        portfolio = self.generate_portfolio(top_n, weight_method)
        
        # 4. 回测组合
        backtest_result = self.backtest_portfolio(portfolio['funds'])
        
        # 5. 风险评估
        risk_result = self.risk_assessment(portfolio['funds'])
        
        # 6. 汇总报告
        report = {
            'analysis_date': datetime.now().isoformat(),
            'total_funds_analyzed': len(self.analysis_results),
            'portfolio': portfolio,
            'top_funds_detail': top_funds,
            'backtest_result': backtest_result,
            'risk_assessment': risk_result,
            'disclaimer': '历史数据仅供参考，不构成投资建议'
        }
        
        print("=" * 60)
        print("✅ 完整分析完成")
        print("=" * 60)
        
        return report


if __name__ == "__main__":
    analyzer = StrategyAnalyzer()
    report = analyzer.full_analysis(top_n=10, weight_method='equal')
    
    # 输出报告摘要
    print("\n📊 组合报告摘要:")
    print("-" * 40)
    print(f"分析基金数：{report['total_funds_analyzed']}")
    print(f"组合基金数：{report['portfolio']['total_funds']}")
    print(f"配置方法：{report['portfolio']['method']}")
    print()
    print("回测结果:")
    bt = report['backtest_result']
    print(f"  累计收益：{bt.get('total_return', 'N/A')}%")
    print(f"  年化收益：{bt.get('annual_return', 'N/A')}%")
    print(f"  夏普比率：{bt.get('sharpe', 'N/A')}")
    print(f"  最大回撤：{bt.get('max_drawdown', 'N/A')}%")
    print()
    print("⚠️ " + report['disclaimer'])
