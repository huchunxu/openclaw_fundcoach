#!/usr/bin/env python3
"""
简单Flask测试 - 验证基本功能
"""

from flask import Flask, render_template_string

app = Flask(__name__)

@app.route('/')
def hello():
    return render_template_string('''
    <html>
    <head><title>OpenClaw FundCoach Test</title></head>
    <body>
        <h1>✅ Web UI Working!</h1>
        <p>Flask is running correctly.</p>
        <a href="/test">Test Route</a>
    </body>
    </html>
    ''')

@app.route('/test')
def test():
    return "Test route working!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)