import React, { useState } from 'react';
import axios from 'axios';

const ManualModePage = () => {
  const [fundCodes, setFundCodes] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsAnalyzing(true);
    setError('');
    setAnalysisResult(null);

    try {
      // 验证基金代码
      const fundCodesList = fundCodes
        .split(',')
        .map(code => code.trim())
        .filter(code => code.length === 6 && /^\d+$/.test(code));

      if (fundCodesList.length === 0) {
        setError('请输入有效的6位数字基金代码');
        setIsAnalyzing(false);
        return;
      }

      const response = await axios.post('/api/analyze', {
        fund_codes: fundCodesList,
        mode: 'manual'
      });

      if (response.data.success) {
        setAnalysisResult(response.data.data);
      } else {
        setError(response.data.error || '分析失败');
      }
    } catch (err) {
      setError('请求失败: ' + (err.response?.data?.error || err.message));
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-800 mb-6">
        <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 inline mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
        </svg>
        手动模式
      </h1>
      
      <p className="text-gray-600 mb-8">
        指定基金代码，进行深度分析和组合优化。
      </p>

      <div className="bg-white rounded-lg shadow-md p-6 mb-8">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">基金输入</h2>
        
        <form onSubmit={handleSubmit}>
          <div className="mb-6">
            <label htmlFor="fundCodes" className="block text-sm font-medium text-gray-700 mb-2">
              基金代码（逗号分隔）
            </label>
            <input
              type="text"
              id="fundCodes"
              value={fundCodes}
              onChange={(e) => setFundCodes(e.target.value)}
              placeholder="例如: 000001,000002,000003"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
              required
            />
            <p className="mt-1 text-sm text-gray-500">
              请输入6位数字基金代码，至少1个
            </p>
          </div>
          
          <button
            type="submit"
            disabled={isAnalyzing}
            className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
          >
            {isAnalyzing ? (
              <>
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                分析中...
              </>
            ) : (
              <>
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
                开始分析
              </>
            )}
          </button>
        </form>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-8">
          <div className="flex">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-red-400 mr-2" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            <span className="text-red-700">{error}</span>
          </div>
        </div>
      )}

      {analysisResult && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">分析结果</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div>
              <h3 className="text-lg font-medium text-gray-700 mb-3">组合概览</h3>
              <ul className="space-y-2">
                <li className="flex justify-between">
                  <span>预期年化收益:</span>
                  <span className="font-medium">
                    {(analysisResult.analysis_results.portfolio_results.annual_return * 100).toFixed(2)}%
                  </span>
                </li>
                <li className="flex justify-between">
                  <span>波动率:</span>
                  <span className="font-medium">
                    {(analysisResult.analysis_results.portfolio_results.volatility * 100).toFixed(2)}%
                  </span>
                </li>
                <li className="flex justify-between">
                  <span>最大回撤:</span>
                  <span className="font-medium">
                    {(analysisResult.analysis_results.portfolio_results.max_drawdown * 100).toFixed(2)}%
                  </span>
                </li>
                <li className="flex justify-between">
                  <span>夏普比率:</span>
                  <span className="font-medium">
                    {analysisResult.analysis_results.portfolio_results.sharpe_ratio.toFixed(2)}
                  </span>
                </li>
              </ul>
            </div>
            
            <div>
              <h3 className="text-lg font-medium text-gray-700 mb-3">选中基金</h3>
              <ul className="space-y-2">
                {Object.entries(analysisResult.analysis_results.portfolio_weights).map(([code, weight]) => (
                  <li key={code} className="flex justify-between">
                    <span>{code}:</span>
                    <span className="font-medium">{(weight * 100).toFixed(1)}%</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
          
          <div className="mb-6">
            <h3 className="text-lg font-medium text-gray-700 mb-3">风险提示</h3>
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <div className="whitespace-pre-line text-sm text-yellow-800">
                {analysisResult.risk_disclosure}
              </div>
            </div>
          </div>
          
          <div>
            <h3 className="text-lg font-medium text-gray-700 mb-3">可视化图表</h3>
            <p className="text-gray-600">图表功能将在后续版本中完善</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default ManualModePage;