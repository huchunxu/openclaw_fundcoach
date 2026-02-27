#!/usr/bin/env python3
"""
Flask Web 应用 - 集成所有Agent的API接口
"""

from flask import Flask, jsonify, request, render_template
import os
import sys
import json
import numpy as np

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 使用直接导入（修复Mac兼容性问题）
from strategy_agent import StrategyAgent
from portfolio_agent import PortfolioAgent  
from risk_agent import RiskAgent
from data_agent import DataAgent

app = Flask(__name__, 
            template_folder='../frontend/dist',
            static_folder='../frontend/dist/assets')

# 初始化Agent实例
strategy_agent = StrategyAgent()
portfolio_agent = PortfolioAgent()
risk_agent = RiskAgent()
data_agent = DataAgent()

@app.route('/')
def index():
    """主页面"""
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_funds():
    """分析基金组合的完整流程"""
    try:
        data = request.json
        fund_pool = data.get('fund_pool', {})
        
        if not fund_pool:
            return jsonify({'error': 'No fund data provided'}), 400
        
        # 1. Strategy Agent 分析
        strategy_results = strategy_agent.analyze_fund_pool(fund_pool)
        
        # 2. Portfolio Agent 优化
        portfolio = portfolio_agent.create_diversified_portfolio(
            fund_pool, strategy_results
        )
        
        # 3. Risk Agent 评估
        risk_report = risk_agent.generate_risk_report(
            portfolio, fund_pool, strategy_results
        )
        
        # 构建响应
        response = {
            'strategy_results': strategy_results,
            'portfolio': portfolio,
            'risk_report': risk_report,
            'status': 'success'
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/factors', methods=['POST'])
def calculate_factors():
    """计算单个基金的因子"""
    try:
        data = request.json
        fund_data = data.get('fund_data', {})
        
        if not fund_data:
            return jsonify({'error': 'No fund data provided'}), 400
        
        factors = strategy_agent.calculate_factors(fund_data)
        score = strategy_agent.score_fund(factors)
        style = strategy_agent.classify_style(fund_data)
        
        return jsonify({
            'factors': factors,
            'score': score,
            'style': style,
            'status': 'success'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/optimize', methods=['POST'])
def optimize_portfolio():
    """优化投资组合"""
    try:
        data = request.json
        fund_pool = data.get('fund_pool', {})
        risk_tolerance = data.get('risk_tolerance', 0.5)
        
        if not fund_pool:
            return jsonify({'error': 'No fund data provided'}), 400
        
        # 先进行策略分析
        strategy_results = strategy_agent.analyze_fund_pool(fund_pool)
        
        # 创建优化组合
        portfolio = portfolio_agent.create_diversified_portfolio(
            fund_pool, strategy_results, risk_tolerance
        )
        
        return jsonify({
            'portfolio': portfolio,
            'status': 'success'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/risk', methods=['POST'])
def risk_analysis():
    """风险分析"""
    try:
        data = request.json
        portfolio_weights = data.get('portfolio_weights', {})
        fund_pool = data.get('fund_pool', {})
        
        if not portfolio_weights or not fund_pool:
            return jsonify({'error': 'Missing portfolio or fund data'}), 400
        
        # 获取策略结果（用于风格信息）
        strategy_results = strategy_agent.analyze_fund_pool(fund_pool)
        
        # 生成风险报告
        risk_report = risk_agent.generate_risk_report(
            portfolio_weights, fund_pool, strategy_results
        )
        
        return jsonify({
            'risk_report': risk_report,
            'status': 'success'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'agents': {
            'strategy': 'active',
            'portfolio': 'active', 
            'risk': 'active',
            'data': 'active'
        }
    })

@app.route('/api/funds/search', methods=['GET'])
def search_funds():
    """搜索基金"""
    try:
        keyword = request.args.get('keyword', '')
        limit = int(request.args.get('limit', 50))
        
        funds = data_agent.search_funds(keyword, limit)
        
        return jsonify({
            'funds': funds,
            'count': len(funds),
            'status': 'success'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/funds/list', methods=['GET'])
def get_fund_list():
    """获取基金列表（分页）"""
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        
        result = data_agent.get_fund_list(page, page_size)
        
        return jsonify({
            'funds': result['funds'],
            'total': result['total'],
            'page': result['page'],
            'page_size': result['page_size'],
            'total_pages': result['total_pages'],
            'status': 'success'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/funds/<fund_code>', methods=['GET'])
def get_fund_detail(fund_code):
    """获取基金详细信息"""
    try:
        # 获取基本信息
        basic_info = data_agent.fetch_fund_basic_info(fund_code)
        if not basic_info:
            return jsonify({'error': 'Fund not found'}), 404
        
        # 获取净值历史（最近100天）
        nav_history = data_agent.fetch_fund_nav_history(fund_code, days=100)
        
        return jsonify({
            'basic_info': basic_info,
            'nav_history': nav_history[:100] if nav_history else [],
            'status': 'success'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)