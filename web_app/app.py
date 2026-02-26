from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def create_app():
    """创建Flask应用"""
    app = Flask(__name__, 
                template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
                static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend', 'dist'))
    app.config['SECRET_KEY'] = 'openclaw-fundcoach-secret-key'
    
    # 启用CORS
    CORS(app)
    
    # API路由
    @app.route('/api/health')
    def health_check():
        return jsonify({'status': 'healthy'})
    
    @app.route('/api/analyze', methods=['POST'])
    def analyze_portfolio():
        from web_app.api import analyze_portfolio
        return analyze_portfolio()
    
    # 静态文件服务（生产模式）
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_frontend(path):
        if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        else:
            return send_from_directory(app.static_folder, 'index.html')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)