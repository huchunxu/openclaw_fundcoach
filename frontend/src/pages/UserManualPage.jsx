import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

const UserManualPage = () => {
  const [manualContent, setManualContent] = useState('');

  useEffect(() => {
    // 从API获取使用手册内容
    fetch('/api/manual')
      .then(response => response.json())
      .then(data => {
        if (data.status === 'success') {
          setManualContent(data.content);
        }
      })
      .catch(error => {
        console.error('Failed to load manual:', error);
        setManualContent('# 使用手册加载失败\n\n请稍后重试。');
      });
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">OpenClaw FundCoach 使用手册</h1>
          <p className="text-gray-600 mb-6">
            本手册将指导您如何使用这个量化基金研究和模拟系统。
          </p>
          
          <div className="prose prose-lg max-w-none">
            {manualContent.split('\n').map((line, index) => {
              if (line.startsWith('# ')) {
                return <h2 key={index} className="text-2xl font-bold text-gray-900 mt-8 mb-4">{line.substring(2)}</h2>;
              } else if (line.startsWith('## ')) {
                return <h3 key={index} className="text-xl font-semibold text-gray-800 mt-6 mb-3">{line.substring(3)}</h3>;
              } else if (line.startsWith('- ')) {
                return <li key={index} className="text-gray-700 mb-2">{line.substring(2)}</li>;
              } else if (line.trim() === '') {
                return <br key={index} />;
              } else {
                return <p key={index} className="text-gray-700 mb-4">{line}</p>;
              }
            })}
          </div>
        </div>
        
        <div className="flex justify-between">
          <Link 
            to="/"
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            返回首页
          </Link>
        </div>
      </div>
    </div>
  );
};

export default UserManualPage;