import React from 'react';
import { Link } from 'react-router-dom';

const Navbar = () => {
  return (
    <nav className="bg-blue-600 text-white shadow-lg">
      <div className="container mx-auto px-4 py-3">
        <div className="flex items-center justify-between">
          <Link to="/" className="flex items-center space-x-2 font-bold text-xl">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            <span>OpenClaw FundCoach</span>
          </Link>
          
          <div className="hidden md:flex space-x-6">
            <Link to="/" className="hover:text-blue-200 transition-colors">
              首页
            </Link>
            <Link to="/analysis" className="hover:text-blue-200 transition-colors">
              📊 分析仪表盘
            </Link>
            <Link to="/auto" className="hover:text-blue-200 transition-colors">
              自动模式
            </Link>
            <Link to="/manual" className="hover:text-blue-200 transition-colors">
              手动模式
            </Link>
            <Link to="/manual-guide" className="hover:text-blue-200 transition-colors">
              使用手册
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;