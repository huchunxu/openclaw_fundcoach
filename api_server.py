#!/usr/bin/env python3
"""
基金教练 API 服务 - Flask RESTful API
提供基金分析、组合优化、回测、风险评估等功能
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import sys
import json

sys.path.insert(0, os.path.dirname(__file__))

from strategy_analyzer import StrategyAnalyzer

app = Flask(__name__)
CORS(app)

# 初始化分析器
analyzer = None

def get_analyzer():
    global analyzer
    if analyzer is None:
        analyzer = StrategyAnalyzer()
    return analyzer


@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'ok',
        'service': 'fundcoach-api',
        'version': '1.0.0'
    })


@app.route('/api/funds/list', methods=['GET'])
def list_funds():
    """获取基金列表"""
    limit = request.args.get('limit', 100, type=int)
    analyzer = get_analyzer()
    
    if not analyzer.analysis_results:
        analyzer.analyze_all_funds(limit=limit)
    
    funds = analyzer.analysis_results[:limit]
    return jsonify({
        'total': len(funds),
        'funds': funds
    })


@app.route('/api/funds/<fund_code>', methods=['GET'])
def get_fund_detail(fund_code):
    """获取单只基金详情"""
    analyzer = get_analyzer()
    df = analyzer.load_fund_data(fund_code)
    
    if df is None:
        return jsonify({'error': '基金不存在'}), 404
    
    factors = analyzer.calculate_factors(fund_code, df)
    if factors is None:
        return jsonify({'error': '数据不足'}), 400
    
    # 生成净值曲线
    chart_data = [
        {'date': str(row['date'])[:10], 'nav': round(float(row['nav']), 4)}
        for _, row in df.iterrows()
    ][::10]  # 采样
    
    return jsonify({
        'fund_code': fund_code,
        'factors': factors,
        'chart_data': chart_data
    })


@app.route('/api/analysis/full', methods=['GET'])
def full_analysis():
    """完整策略分析"""
    top_n = request.args.get('top_n', 10, type=int)
    weight_method = request.args.get('method', 'equal')
    
    analyzer = get_analyzer()
    report = analyzer.full_analysis(top_n=top_n, weight_method=weight_method)
    
    return jsonify(report)


@app.route('/api/portfolio/generate', methods=['POST'])
def generate_portfolio():
    """生成优化组合"""
    data = request.get_json() or {}
    top_n = data.get('top_n', 10)
    method = data.get('method', 'equal')  # equal | score_weighted
    
    analyzer = get_analyzer()
    if not analyzer.analysis_results:
        analyzer.analyze_all_funds()
    
    portfolio = analyzer.generate_portfolio(top_n=top_n, method=method)
    
    return jsonify(portfolio)


@app.route('/api/portfolio/backtest', methods=['POST'])
def backtest_portfolio():
    """组合回测"""
    data = request.get_json()
    if not data or 'portfolio' not in data:
        return jsonify({'error': '缺少组合数据'}), 400
    
    analyzer = get_analyzer()
    result = analyzer.backtest_portfolio(data['portfolio'])
    
    return jsonify(result)


@app.route('/api/risk/assess', methods=['POST'])
def assess_risk():
    """风险评估"""
    data = request.get_json()
    if not data or 'portfolio' not in data:
        return jsonify({'error': '缺少组合数据'}), 400
    
    analyzer = get_analyzer()
    result = analyzer.risk_assessment(data['portfolio'])
    
    return jsonify(result)


@app.route('/api/ranking', methods=['GET'])
def get_ranking():
    """获取基金排名"""
    limit = request.args.get('limit', 50, type=int)
    sort_by = request.args.get('sort', 'composite_score')  # sharpe, return, drawdown, etc.
    
    analyzer = get_analyzer()
    if not analyzer.analysis_results:
        analyzer.analyze_all_funds()
    
    scored = analyzer.calculate_composite_score(analyzer.analysis_results)
    
    # 排序
    if sort_by == 'sharpe':
        scored = sorted(scored, key=lambda x: x['sharpe'], reverse=True)
    elif sort_by == 'return':
        scored = sorted(scored, key=lambda x: x['annual_return'], reverse=True)
    elif sort_by == 'drawdown':
        scored = sorted(scored, key=lambda x: x['max_drawdown'])
    else:
        scored = sorted(scored, key=lambda x: x['composite_score'], reverse=True)
    
    return jsonify({
        'sort_by': sort_by,
        'total': len(scored),
        'ranking': scored[:limit]
    })


@app.route('/api/compare', methods=['POST'])
def compare_funds():
    """基金对比"""
    data = request.get_json()
    fund_codes = data.get('codes', [])
    
    if len(fund_codes) < 2:
        return jsonify({'error': '至少需要 2 只基金'}), 400
    
    analyzer = get_analyzer()
    comparison = []
    
    for code in fund_codes:
        df = analyzer.load_fund_data(code)
        if df is not None:
            factors = analyzer.calculate_factors(code, df)
            if factors:
                comparison.append(factors)
    
    return jsonify({
        'funds': comparison,
        'count': len(comparison)
    })


if __name__ == '__main__':
    print("=" * 60)
    print("🚀 基金教练 API 服务启动")
    print("=" * 60)
    print("端口：5000")
    print("地址：http://localhost:5000")
    print()
    print("可用接口:")
    print("  GET  /api/health          - 健康检查")
    print("  GET  /api/funds/list      - 基金列表")
    print("  GET  /api/funds/<code>    - 基金详情")
    print("  GET  /api/analysis/full   - 完整分析")
    print("  POST /api/portfolio/generate - 生成组合")
    print("  POST /api/portfolio/backtest - 组合回测")
    print("  POST /api/risk/assess     - 风险评估")
    print("  GET  /api/ranking         - 基金排名")
    print("  POST /api/compare         - 基金对比")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=False)
