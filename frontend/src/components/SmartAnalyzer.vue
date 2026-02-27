<template>
  <div class="smart-analyzer">
    <div class="text-center mb-8">
      <h1 class="text-3xl font-bold text-gray-900 mb-4">智能基金分析助手</h1>
      <p class="text-lg text-gray-600 max-w-2xl mx-auto">
        一键完成基金分析、组合优化和风险评估，让投资决策更简单
      </p>
    </div>
    
    <!-- 智能推荐区域 -->
    <div class="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6 mb-8">
      <h2 class="text-xl font-semibold mb-4 text-gray-800">🎯 智能推荐</h2>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div 
          v-for="(portfolio, index) in recommendedPortfolios" 
          :key="index"
          class="bg-white rounded-lg p-4 shadow hover:shadow-md transition-shadow cursor-pointer"
          @click="selectRecommendedPortfolio(portfolio)"
        >
          <div class="flex items-center justify-between mb-2">
            <span class="font-medium text-gray-800">{{ portfolio.name }}</span>
            <span class="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full">
              {{ portfolio.riskLevel }}
            </span>
          </div>
          <p class="text-sm text-gray-600 mb-3">{{ portfolio.description }}</p>
          <div class="text-sm">
            <span class="text-gray-700">预期年化收益:</span>
            <span class="font-semibold text-green-600 ml-1">{{ portfolio.expectedReturn }}%</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 自定义分析区域 -->
    <div class="bg-white rounded-xl shadow p-6">
      <h2 class="text-xl font-semibold mb-4 text-gray-800">🔍 自定义分析</h2>
      
      <!-- 基金选择 -->
      <div class="mb-6">
        <label class="block text-sm font-medium text-gray-700 mb-2">选择基金</label>
        <div class="flex flex-wrap gap-2 mb-4">
          <div 
            v-for="fund in selectedFunds" 
            :key="fund.code"
            class="flex items-center bg-blue-100 text-blue-800 px-3 py-1 rounded-full"
          >
            <span>{{ fund.code }} - {{ fund.name }}</span>
            <button 
              @click="removeFund(fund)" 
              class="ml-2 text-blue-600 hover:text-blue-800"
            >
              ×
            </button>
          </div>
          <div v-if="selectedFunds.length === 0" class="text-gray-500 text-sm">
            点击下方基金列表添加基金
          </div>
        </div>
        
        <div class="flex space-x-4">
          <input 
            v-model="searchKeyword"
            @keyup.enter="searchFunds"
            type="text" 
            class="flex-1 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            placeholder="搜索基金名称或代码..."
          />
          <button 
            @click="searchFunds"
            class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md"
          >
            搜索
          </button>
        </div>
        
        <!-- 搜索结果 -->
        <div v-if="searchResults.length > 0" class="mt-4 max-h-60 overflow-y-auto">
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
            <div 
              v-for="fund in searchResults" 
              :key="fund.code"
              @click="addFund(fund)"
              class="flex items-center p-2 hover:bg-gray-100 rounded cursor-pointer"
            >
              <div class="mr-3">
                <svg v-for="i in 5" :key="i" class="h-4 w-4 inline" :class="i <= fund.rating ? 'text-yellow-400' : 'text-gray-300'" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                </svg>
              </div>
              <div>
                <div class="font-medium text-gray-900">{{ fund.code }}</div>
                <div class="text-sm text-gray-600">{{ fund.name }}</div>
                <div class="text-xs text-gray-500">{{ fund.type }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 风险偏好设置 -->
      <div class="mb-6">
        <label class="block text-sm font-medium text-gray-700 mb-2">风险偏好</label>
        <div class="flex space-x-4">
          <button 
            v-for="risk in riskOptions" 
            :key="risk.value"
            @click="selectedRisk = risk.value"
            :class="[
              selectedRisk === risk.value 
                ? 'bg-blue-600 text-white' 
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300',
              'px-4 py-2 rounded-md font-medium transition-colors'
            ]"
          >
            {{ risk.label }}
          </button>
        </div>
      </div>
      
      <!-- 分析按钮 -->
      <div class="text-center">
        <button 
          @click="startAnalysis"
          :disabled="selectedFunds.length === 0 || analyzing"
          class="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-bold py-3 px-8 rounded-lg text-lg transition-all transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {{ analyzing ? '分析中...' : '🚀 开始智能分析' }}
        </button>
      </div>
    </div>
    
    <!-- 分析结果区域 -->
    <div v-if="analysisResult" class="mt-8">
      <div class="bg-white rounded-xl shadow p-6">
        <h2 class="text-2xl font-bold mb-6 text-gray-800">📊 分析结果</h2>
        
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <!-- 组合概览 -->
          <div>
            <h3 class="text-lg font-semibold mb-4 text-gray-800">组合概览</h3>
            <div class="space-y-3">
              <div class="flex justify-between">
                <span class="text-gray-600">预期年化收益</span>
                <span class="font-semibold text-green-600">{{ (analysisResult.portfolioMetrics.annual_return * 100).toFixed(2) }}%</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">夏普率</span>
                <span class="font-semibold">{{ analysisResult.portfolioMetrics.sharpe_ratio.toFixed(3) }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">最大回撤</span>
                <span class="font-semibold text-red-600">{{ (analysisResult.portfolioMetrics.max_drawdown * 100).toFixed(2) }}%</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">波动率</span>
                <span class="font-semibold">{{ (analysisResult.portfolioMetrics.volatility * 100).toFixed(2) }}%</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">风险等级</span>
                <span :class="{
                  'text-green-600': analysisResult.riskAssessment.risk_level === 'low',
                  'text-yellow-600': analysisResult.riskAssessment.risk_level === 'medium',
                  'text-red-600': analysisResult.riskAssessment.risk_level === 'high'
                }" class="font-semibold capitalize">
                  {{ analysisResult.riskAssessment.risk_level }}
                </span>
              </div>
            </div>
          </div>
          
          <!-- 组合权重 -->
          <div>
            <h3 class="text-lg font-semibold mb-4 text-gray-800">组合权重</h3>
            <div class="space-y-3">
              <div v-for="(weight, fundCode) in analysisResult.portfolio" :key="fundCode">
                <div class="flex justify-between mb-1">
                  <span class="font-medium">{{ fundCode }}</span>
                  <span>{{ (weight * 100).toFixed(1) }}%</span>
                </div>
                <div class="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    class="bg-blue-600 h-2 rounded-full" 
                    :style="{ width: (weight * 100) + '%' }"
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 风险提示 -->
        <div class="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <h4 class="font-semibold text-yellow-800 mb-2">⚠️ 风险提示</h4>
          <div class="text-sm text-yellow-700 space-y-1">
            <div v-if="analysisResult.riskAssessment.alerts.length > 0">
              <div v-for="(alert, index) in analysisResult.riskAssessment.alerts" :key="index">
                • {{ alert }}
              </div>
            </div>
            <div v-else>
              • 组合风险在可接受范围内
            </div>
            <div class="italic mt-2">
              历史数据仅供参考，不构成投资建议。投资有风险，入市需谨慎。
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'SmartAnalyzer',
  data() {
    return {
      // 推荐组合
      recommendedPortfolios: [
        {
          name: '稳健增长组合',
          description: '适合稳健型投资者，平衡收益与风险',
          riskLevel: '中等',
          expectedReturn: '8-12',
          funds: ['000001', '000004', '000008']
        },
        {
          name: '激进成长组合', 
          description: '适合激进型投资者，追求高收益',
          riskLevel: '高',
          expectedReturn: '12-18',
          funds: ['000002', '000003', '000009']
        },
        {
          name: '保守防御组合',
          description: '适合保守型投资者，注重本金安全',
          riskLevel: '低', 
          expectedReturn: '4-8',
          funds: ['000005', '000010', '000006']
        }
      ],
      
      // 自定义分析
      searchKeyword: '',
      searchResults: [],
      selectedFunds: [],
      riskOptions: [
        { value: 0.3, label: '保守' },
        { value: 0.5, label: '稳健' },
        { value: 0.7, label: '激进' }
      ],
      selectedRisk: 0.5,
      analyzing: false,
      analysisResult: null
    };
  },
  methods: {
    async searchFunds() {
      try {
        const params = { keyword: this.searchKeyword, limit: 20 };
        const response = await axios.get('/api/funds/search', { params });
        
        if (response.data.status === 'success') {
          this.searchResults = response.data.funds;
        }
      } catch (error) {
        console.error('搜索基金失败:', error);
        alert('搜索基金失败: ' + error.message);
      }
    },
    
    addFund(fund) {
      if (!this.selectedFunds.find(f => f.code === fund.code)) {
        this.selectedFunds.push(fund);
        this.searchResults = [];
        this.searchKeyword = '';
      }
    },
    
    removeFund(fundToRemove) {
      this.selectedFunds = this.selectedFunds.filter(fund => fund.code !== fundToRemove.code);
    },
    
    async selectRecommendedPortfolio(portfolio) {
      // 获取推荐组合中的基金详细信息
      const fundDetails = [];
      for (const fundCode of portfolio.funds) {
        try {
          const response = await axios.get(`/api/funds/${fundCode}`);
          if (response.data.status === 'success') {
            fundDetails.push({
              code: fundCode,
              name: response.data.basic_info.name,
              type: response.data.basic_info.type
            });
          }
        } catch (error) {
          console.warn(`获取基金 ${fundCode} 详情失败:`, error);
        }
      }
      
      this.selectedFunds = fundDetails;
      this.selectedRisk = portfolio.riskLevel === '低' ? 0.3 : portfolio.riskLevel === '高' ? 0.7 : 0.5;
      await this.startAnalysis();
    },
    
    async startAnalysis() {
      if (this.selectedFunds.length === 0) {
        alert('请至少选择一只基金');
        return;
      }
      
      try {
        this.analyzing = true;
        
        // 构建基金池数据
        const fundPool = {};
        for (const fund of this.selectedFunds) {
          try {
            const response = await axios.get(`/api/funds/${fund.code}`);
            if (response.data.status === 'success') {
              const returns = response.data.nav_history.map(item => item.daily_return);
              fundPool[fund.code] = { returns };
            }
          } catch (error) {
            console.warn(`获取基金 ${fund.code} 数据失败:`, error);
          }
        }
        
        if (Object.keys(fundPool).length === 0) {
          throw new Error('无法获取任何基金的历史数据');
        }
        
        // 执行完整分析流程
        const response = await axios.post('/api/analyze', {
          fund_pool: fundPool
        });
        
        if (response.data.status === 'success') {
          this.analysisResult = {
            portfolio: response.data.portfolio,
            portfolioMetrics: response.data.risk_report.risk_metrics,
            riskAssessment: response.data.risk_report.risk_assessment
          };
        } else {
          throw new Error(response.data.error);
        }
        
      } catch (error) {
        console.error('分析失败:', error);
        alert('分析失败: ' + error.message);
      } finally {
        this.analyzing = false;
      }
    }
  }
};
</script>