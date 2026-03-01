import React, { useState, useEffect } from 'react';
import { Line, Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const API_BASE = 'http://localhost:5000/api';

export default function AnalysisDashboard() {
  const [loading, setLoading] = useState(false);
  const [analysisData, setAnalysisData] = useState(null);
  const [rankingData, setRankingData] = useState([]);
  const [sortBy, setSortBy] = useState('composite_score');

  // 完整分析
  const runFullAnalysis = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/analysis/full`);
      const data = await res.json();
      setAnalysisData(data);
    } catch (e) {
      console.error('分析失败:', e);
    }
    setLoading(false);
  };

  // 获取排名
  const fetchRanking = async (sort) => {
    try {
      const res = await fetch(`${API_BASE}/ranking?limit=20&sort=${sort}`);
      const data = await res.json();
      setRankingData(data.ranking || []);
    } catch (e) {
      console.error('获取排名失败:', e);
    }
  };

  useEffect(() => {
    fetchRanking(sortBy);
  }, [sortBy]);

  // 净值曲线数据
  const chartData = analysisData?.backtest_result?.chart_data || [];
  const lineChartData = {
    labels: chartData.map(d => d.date?.slice(5) || ''),
    datasets: [{
      label: '组合净值',
      data: chartData.map(d => d.nav || 1),
      borderColor: 'rgb(59, 130, 246)',
      backgroundColor: 'rgba(59, 130, 246, 0.1)',
      fill: true,
      tension: 0.4
    }]
  };

  // 基金评分柱状图
  const barChartData = {
    labels: rankingData.slice(0, 10).map(f => f.fund_code),
    datasets: [{
      label: '综合评分',
      data: rankingData.slice(0, 10).map(f => f.composite_score),
      backgroundColor: 'rgba(16, 185, 129, 0.6)',
      borderColor: 'rgb(16, 185, 129)',
      borderWidth: 1
    }]
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <h1 className="text-3xl font-bold mb-6 text-gray-800">📊 策略分析仪表盘</h1>
      
      {/* 控制面板 */}
      <div className="flex gap-4 mb-6">
        <button
          onClick={runFullAnalysis}
          disabled={loading}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? '分析中...' : '🚀 运行完整分析'}
        </button>
        
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
          className="px-4 py-2 border rounded-lg"
        >
          <option value="composite_score">综合评分</option>
          <option value="sharpe">夏普比率</option>
          <option value="return">收益率</option>
          <option value="drawdown">回撤控制</option>
        </select>
      </div>

      {/* 分析结果 */}
      {analysisData && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white p-4 rounded-lg shadow">
            <div className="text-gray-500 text-sm">累计收益</div>
            <div className="text-2xl font-bold text-green-600">
              {analysisData.backtest_result?.total_return || 0}%
            </div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow">
            <div className="text-gray-500 text-sm">年化收益</div>
            <div className="text-2xl font-bold text-blue-600">
              {analysisData.backtest_result?.annual_return || 0}%
            </div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow">
            <div className="text-gray-500 text-sm">夏普比率</div>
            <div className="text-2xl font-bold text-purple-600">
              {analysisData.backtest_result?.sharpe || 0}
            </div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow">
            <div className="text-gray-500 text-sm">最大回撤</div>
            <div className="text-2xl font-bold text-red-600">
              {analysisData.backtest_result?.max_drawdown || 0}%
            </div>
          </div>
        </div>
      )}

      {/* 图表区域 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 净值曲线 */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">📈 组合净值曲线</h2>
          {chartData.length > 0 ? (
            <Line data={lineChartData} options={{
              responsive: true,
              plugins: { legend: { display: false } },
              scales: { y: { beginAtZero: false } }
            }} />
          ) : (
            <div className="text-gray-400 text-center py-10">点击"运行完整分析"生成数据</div>
          )}
        </div>

        {/* 基金评分 */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">🏆 Top 10 基金评分</h2>
          {rankingData.length > 0 ? (
            <Bar data={barChartData} options={{
              responsive: true,
              plugins: { legend: { display: false } }
            }} />
          ) : (
            <div className="text-gray-400 text-center py-10">加载中...</div>
          )}
        </div>
      </div>

      {/* 组合详情 */}
      {analysisData?.portfolio && (
        <div className="mt-6 bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">💼 推荐组合</h2>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            {analysisData.portfolio.funds?.map((f, i) => (
              <div key={i} className="bg-gray-50 p-3 rounded">
                <div className="font-mono text-sm">{f.fund_code}</div>
                <div className="text-blue-600">{(f.weight * 100).toFixed(1)}%</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 风险提示 */}
      <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg text-yellow-800 text-sm">
        ⚠️ 历史数据仅供参考，不构成投资建议
      </div>
    </div>
  );
}