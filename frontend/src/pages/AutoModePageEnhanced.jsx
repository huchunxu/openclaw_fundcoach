import React, { useState, useEffect } from 'react';
import axios from 'axios';

const AutoModePageEnhanced = () => {
  const [formData, setFormData] = useState({
    riskTolerance: 'medium',
    investmentHorizon: 3,
    selectedFunds: []
  });
  
  const [availableFunds, setAvailableFunds] = useState([]);
  const [fundSearchTerm, setFundSearchTerm] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [error, setError] = useState('');
  const [loadingFunds, setLoadingFunds] = useState(true);

  // 加载可用基金列表
  useEffect(() => {
    const fetchAvailableFunds = async () => {
      try {
        const response = await axios.get('/api/funds/available');
        if (response.data.status === 'success') {
          setAvailableFunds(response.data.funds);
        }
      } catch (err) {
        console.error('Failed to load available funds:', err);
        // 如果API失败，使用示例数据
        setAvailableFunds([
          { fund_code: '000001', fund_name: '示例基金1' },
          { fund_code: '000002', fund_name: '示例基金2' }
        ]);
      } finally {
        setLoadingFunds(false);
      }
    };
    
    fetchAvailableFunds();
  }, []);

  // 过滤基金列表
  const filteredFunds = availableFunds.filter(fund => 
    fund.fund_code.includes(fundSearchTerm) || 
    (fund.fund_name && fund.fund_name.includes(fundSearchTerm))
  );

  // 选择/取消选择基金
  const toggleFundSelection = (fundCode) => {
    setFormData(prev => ({
      ...prev,
      selectedFunds: prev.selectedFunds.includes(fundCode)
        ? prev.selectedFunds.filter(code => code !== fundCode)
        : [...prev.selectedFunds, fundCode]
    }));
  };

  // 全选
  const selectAllFunds = () => {
    setFormData(prev => ({
      ...prev,
      selectedFunds: filteredFunds.map(fund => fund.fund_code)
    }));
  };

  // 清空选择
  const clearSelection = () => {
    setFormData(prev => ({
      ...prev,
      selectedFunds: []
    }));
  };

  // 提交分析
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (formData.selectedFunds.length === 0) {
      setError('请至少选择一只基金');
      return;
    }
    
    setIsAnalyzing(true);
    setError('');
    setAnalysisResult(null);

    try {
      const response = await axios.post('/api/analyze', {
        fund_codes: formData.selectedFunds,
        mode: 'auto',
        preferences: {
          risk_tolerance: formData.riskTolerance,
          investment_horizon: parseInt(formData.investmentHorizon)
        }
      });

      if (response.data.success || response.data.status === 'success') {
        setAnalysisResult(response.data.data || response.data);
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
    <div className="max-w-6xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gray-800 mb-2">
        🤖 自动模式
      </h1>
      <p className="text-gray-600 mb-8">
        基于因子模型自动构建最优投资组合
      </p>

      {/* 可用基金统计 */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
        <div className="flex items-center justify-between">
          <div>
            <span className="text-blue-800 font-semibold">📊 数据统计</span>
            <p className="text-blue-600 text-sm mt-1">
              当前可用基金: <strong>{availableFunds.length}</strong> 只
            </p>
          </div>
          <div className="text-blue-800 font-semibold">
            已选择: <strong>{formData.selectedFunds.length}</strong> 只
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* 左侧：基金选择 */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">
            📋 基金选择
          </h2>
          
          {/* 搜索框 */}
          <div className="mb-4">
            <input
              type="text"
              placeholder="搜索基金代码或名称..."
              value={fundSearchTerm}
              onChange={(e) => setFundSearchTerm(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* 操作按钮 */}
          <div className="flex space-x-2 mb-4">
            <button
              type="button"
              onClick={selectAllFunds}
              className="px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded hover:bg-blue-200"
            >
              全选
            </button>
            <button
              type="button"
              onClick={clearSelection}
              className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
            >
              清空
            </button>
          </div>

          {/* 基金列表 */}
          <div className="max-h-96 overflow-y-auto border rounded-lg">
            {loadingFunds ? (
              <div className="p-4 text-center text-gray-500">
                加载中...
              </div>
            ) : filteredFunds.length === 0 ? (
              <div className="p-4 text-center text-gray-500">
                未找到匹配的基金
              </div>
            ) : (
              filteredFunds.slice(0, 100).map(fund => (
                <div
                  key={fund.fund_code}
                  onClick={() => toggleFundSelection(fund.fund_code)}
                  className={`p-3 border-b cursor-pointer hover:bg-gray-50 ${
                    formData.selectedFunds.includes(fund.fund_code)
                      ? 'bg-blue-50 border-l-4 border-l-blue-500'
                      : ''
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <span className="font-mono font-semibold">{fund.fund_code}</span>
                      <span className="text-gray-600 ml-2">{fund.fund_name}</span>
                    </div>
                    {formData.selectedFunds.includes(fund.fund_code) && (
                      <span className="text-blue-600">✓</span>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* 右侧：参数设置 */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">
            ⚙️ 参数设置
          </h2>
          
          <form onSubmit={handleSubmit}>
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  风险偏好
                </label>
                <select
                  value={formData.riskTolerance}
                  onChange={(e) => setFormData(prev => ({ ...prev, riskTolerance: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="low">🛡️ 保守型 - 追求稳定收益</option>
                  <option value="medium">⚖️ 稳健型 - 平衡风险收益</option>
                  <option value="high">🚀 激进型 - 追求高收益</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  投资期限 (年)
                </label>
                <input
                  type="number"
                  min="1"
                  max="30"
                  value={formData.investmentHorizon}
                  onChange={(e) => setFormData(prev => ({ ...prev, investmentHorizon: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <button
                type="submit"
                disabled={isAnalyzing || formData.selectedFunds.length === 0}
                className={`w-full py-3 px-4 rounded-lg font-semibold text-white ${
                  isAnalyzing || formData.selectedFunds.length === 0
                    ? 'bg-gray-400 cursor-not-allowed'
                    : 'bg-blue-600 hover:bg-blue-700'
                }`}
              >
                {isAnalyzing ? '🔄 分析中...' : '🚀 开始分析'}
              </button>
            </div>
          </form>

          {/* 错误提示 */}
          {error && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
              ⚠️ {error}
            </div>
          )}
        </div>
      </div>

      {/* 分析结果 */}
      {analysisResult && (
        <div className="mt-8 bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">
            📊 分析结果
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="bg-green-50 p-4 rounded-lg">
              <div className="text-sm text-green-600">预期年化收益</div>
              <div className="text-2xl font-bold text-green-800">
                {(analysisResult.analysis_results?.portfolio_results?.annual_return * 100 || 0).toFixed(2)}%
              </div>
            </div>
            
            <div className="bg-blue-50 p-4 rounded-lg">
              <div className="text-sm text-blue-600">夏普率</div>
              <div className="text-2xl font-bold text-blue-800">
                {analysisResult.analysis_results?.portfolio_results?.sharpe_ratio?.toFixed(2) || 'N/A'}
              </div>
            </div>
            
            <div className="bg-red-50 p-4 rounded-lg">
              <div className="text-sm text-red-600">最大回撤</div>
              <div className="text-2xl font-bold text-red-800">
                {(analysisResult.analysis_results?.portfolio_results?.max_drawdown * 100 || 0).toFixed(2)}%
              </div>
            </div>
          </div>

          <div className="text-sm text-gray-600 bg-gray-50 p-4 rounded-lg">
            ⚠️ <strong>风险提示：</strong>历史数据仅供参考，不构成投资建议。投资有风险，入市需谨慎。
          </div>
        </div>
      )}
    </div>
  );
};

export default AutoModePageEnhanced;