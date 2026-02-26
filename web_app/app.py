"""
Flask Web应用主程序 - 修复版本
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from web_app.api import api_bp
from web_app.models import PortfolioAnalyzer


def create_app():
    """创建Flask应用"""
    app = Flask(__name__, 
                template_folder=os.path.join(os.path.dirname(__file__), 'templates'))
    app.config['SECRET_KEY'] = 'openclaw-fundcoach-secret-key'
    
    # 启用CORS
    CORS(app)
    
    # 注册蓝图
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # 初始化全局分析器
    app.analyzer = PortfolioAnalyzer()
    
    return app


def create_routes(app):
    """创建路由"""
    @app.route('/')
    def index():
        """主页"""
        return render_template('index.html')

    @app.route('/dashboard')
    def dashboard():
        """仪表盘页面"""
        return render_template('dashboard.html')

    @app.route('/manual')
    def manual_mode():
        """手动模式页面"""
        return render_template('manual.html')

    @app.route('/auto')
    def auto_mode():
        """自动模式页面"""
        return render_template('auto.html')

    return app


if __name__ == '__main__':
    # 创建应用
    app = create_app()
    app = create_routes(app)
    
    # 运行应用
    app.run(host='0.0.0.0', port=5000, debug=True)