#!/usr/bin/env python3
"""
Web应用启动脚本 - 修复Mac兼容性问题
"""

import os
import sys
import warnings

# 忽略SSL警告（Mac LibreSSL问题）
warnings.filterwarnings("ignore", category=UserWarning, module="urllib3")

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from web_app.app import create_app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)