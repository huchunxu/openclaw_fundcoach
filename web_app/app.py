from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def create_app():
    """创建Flask应用"""
    # 获取项目根目录
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    static_folder = os.path.join(project_root, 'frontend', 'dist')
    
    app = Flask(__name__, 
                static_folder=static_folder,
                static_url_path='')
    app.config['SECRET_KEY'] = 'openclaw-fundcoach-secret-key'
    
    # 启用CORS
    CORS(app)
    
    # API路由
    @app.route('/api/health')
    def health_check():
        return jsonify({'status': 'healthy'})
    
    from web_app.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # 静态文件服务（生产模式）
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_frontend(path):
        if path and os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        else:
            return send_from_directory(app.static_folder, 'index.html')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)