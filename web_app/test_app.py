#!/usr/bin/env python3
"""
测试Flask应用是否正确配置
"""

import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from web_app.app import create_app

def test_app():
    """测试Flask应用"""
    app = create_app()
    
    # 测试模板目录
    print(f"Template folder: {app.template_folder}")
    print(f"Static folder: {app.static_folder}")
    
    # 测试路由
    with app.test_client() as client:
        response = client.get('/')
        print(f"Root route status: {response.status_code}")
        
        response = client.get('/auto')
        print(f"Auto route status: {response.status_code}")
        
        response = client.get('/manual')
        print(f"Manual route status: {response.status_code}")

if __name__ == '__main__':
    test_app()