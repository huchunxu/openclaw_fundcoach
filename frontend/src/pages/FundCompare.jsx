import React, { useState } from 'react';

const API_BASE = 'http://localhost:5000/api';

export default function FundCompare() {
  const [fundCodes, setFundCodes] = useState('');
  const [comparison, setComparison] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleCompare = async () => {
    const codes = fundCodes.split(/[,，\s]+/).filter(c => c.trim());
    if (codes.length < 2) {
      alert('请输入至少2只基金代码');
      return;
    }
    
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/compare`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ codes })
      });
      const data = await res.json();
      setComparison(data);
    } catch (e) {
      console.error('对比失败:', e);
    }
    setLoading(false);
  };

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">🔍 基金对比</h1>
      
      <div className="bg-white p-6 rounded-lg shadow mb-6">
        <label className="block text-gray-700 mb-2">输入基金代码（用逗号或空格分隔）</label>
        <div className="flex gap-4">
          <input
            type="text"
            value={fundCodes}
            onChange={(e) => setFundCodes(e.target.value)}
            placeholder="例如: 000196, 000141, 000162"
            className="flex-1 px-4 py-2 border rounded-lg"
          />
          <button
            onClick={handleCompare}
            disabled={loading}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? '对比中...' : '开始对比'}
          </button>
        </div>
      </div>

      {comparison && comparison.funds && (
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">对比结果 ({comparison.count} 只基金)</h2>
          
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-gray-50">
                  <th className="px-4 py-2 text-left">基金代码</th>
                  <th className="px-4 py-2 text-right">累计收益</th>
                  <th className="px-4 py-2 text-right">年化收益</th>
                  <th className="px-4 py-2 text-right">夏普比率</th>
                  <th className="px-4 py-2 text-right">最大回撤</th>
                  <th className="px-4 py-2 text-right">波动率</th>
                </tr>
              </thead>
              <tbody>
                {comparison.funds.map((fund, i) => (
                  <tr key={i} className="border-t hover:bg-gray-50">
                    <td className="px-4 py-3 font-mono">{fund.fund_code}</td>
                    <td className="px-4 py-3 text-right text-green-600">{fund.total_return}%</td>
                    <td className="px-4 py-3 text-right">{fund.annual_return}%</td>
                    <td className="px-4 py-3 text-right">{fund.sharpe}</td>
                    <td className="px-4 py-3 text-right text-red-600">{fund.max_drawdown}%</td>
                    <td className="px-4 py-3 text-right">{fund.volatility}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg text-yellow-800 text-sm">
        ⚠️ 历史数据仅供参考，不构成投资建议
      </div>
    </div>
  );
}