"""
Web API接口
"""

from flask import Blueprint, request, jsonify
from web_app.models import PortfolioAnalyzer
import logging

api_bp = Blueprint('api', __name__)
logger = logging.getLogger(__name__)


@api_bp.route('/analyze', methods=['POST'])
def analyze_portfolio():
    """
    分析投资组合API
    
    Request JSON:
    {
        "fund_codes": ["000001", "000002", ...],
        "mode": "auto" or "manual",
        "preferences": {
            "risk_tolerance": "medium",
            "investment_horizon": 3,
            "max_drawdown_limit": -0.25
        }
    }
    
    Response JSON:
    {
        "success": true,
        "data": {
            "analysis_results": {...},
            "charts_data": {...},
            "risk_disclosure": "..."
        }
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'Invalid JSON data'}), 400
            
        fund_codes = data.get('fund_codes', [])
        mode = data.get('mode', 'auto')
        preferences = data.get('preferences', {})
        
        if not fund_codes:
            return jsonify({'success': False, 'error': 'Fund codes are required'}), 400
            
        # 获取应用分析器实例
        from flask import current_app
        analyzer = current_app.analyzer
        
        # 执行分析
        result = analyzer.generate_portfolio_analysis(fund_codes, mode, preferences)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Analysis failed: {str(e)}'
        }), 500


@api_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查API"""
    return jsonify({'status': 'healthy', 'version': '1.0.0'})


@api_bp.route('/funds/<fund_code>', methods=['GET'])
def get_fund_info(fund_code):
    """
    获取单只基金信息
    
    Response JSON:
    {
        "success": true,
        "data": {
            "fund_code": "000001",
            "fund_name": "...",
            "fund_type": "...",
            "backtest_results": {...}
        }
    }
    """
    try:
        from flask import current_app
        analyzer = current_app.analyzer
        
        # 分析单只基金
        analysis_data = analyzer.analyze_fund_list([fund_code])
        
        if fund_code in analysis_data['fund_basic_info']:
            fund_info = analysis_data['fund_basic_info'][fund_code]
            backtest_results = analysis_data['fund_backtest_results'][fund_code]
            
            return jsonify({
                'success': True,
                'data': {
                    'fund_code': fund_code,
                    'fund_name': fund_info['fund_name'],
                    'fund_type': fund_info['fund_type'],
                    'fund_size': fund_info['fund_size'],
                    'backtest_results': backtest_results
                }
            })
        else:
            return jsonify({'success': False, 'error': 'Fund not found'}), 404
            
    except Exception as e:
        logger.error(f"Fund info error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to get fund info: {str(e)}'
        }), 500