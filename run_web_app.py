#!/usr/bin/env python3
"""
运行Web应用的入口文件
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from web_app.app import app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)