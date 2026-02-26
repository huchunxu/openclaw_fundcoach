"""
修正后的Flask Web应用主程序
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def create_app():
    """创建Flask应用"""
    app = Flask(__name__, 
                template_folder=os.path.join(os.path.dirname(__file__), 'templates'))
    app.config['SECRET_KEY'] = 'openclaw-fundcoach-secret-key'
    
    # 启用CORS
    CORS(app)
    
    @app.route('/')
    def index():
        """主页"""
        return render_template('index.html')

    @app.route('/dashboard')
    def dashboard():
        """仪表盘页面"""
        return render_template('index.html')

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
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)