<template>
  <div class="user-friendly-analyzer">
    <!-- 主标题 -->
    <div class="text-center mb-8">
      <h1 class="text-4xl font-bold text-gray-900 mb-4">基金智能助手</h1>
      <p class="text-xl text-gray-600 max-w-2xl mx-auto">
        帮您轻松选择优质基金，智能配置投资组合
      </p>
    </div>
    
    <!-- 使用步骤引导 -->
    <div class="bg-white rounded-2xl shadow-lg p-8 mb-8">
      <div class="text-center mb-6">
        <h2 class="text-2xl font-semibold text-gray-800 mb-2">三步完成智能分析</h2>
        <p class="text-gray-600">简单易用，无需专业知识</p>
      </div>
      
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div class="text-center">
          <div class="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <span class="text-2xl font-bold text-blue-600">1</span>
          </div>
          <h3 class="font-medium text-gray-800 mb-2">选择基金</h3>
          <p class="text-gray-600 text-sm">从热门基金中选择，或搜索您感兴趣的基金</p>
        </div>
        
        <div class="text-center">
          <div class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <span class="text-2xl font-bold text-green-600">2</span>
          </div>
          <h3 class="font-medium text-gray-800 mb-2">选择风格</h3>
          <p class="text-gray-600 text-sm">根据您的风险偏好选择投资风格</p>
        </div>
        
        <div class="text-center">
          <div class="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <span class="text-2xl font-bold text-purple-600">3</span>
          </div>
          <h3 class="font-medium text-gray-800 mb-2">查看结果</h3>
          <p class="text-gray-600 text-sm">获取个性化投资建议和风险提示</p>
        </div>
      </div>
    </div>
    
    <!-- 热门基金推荐 -->
    <div class="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl p-8 mb-8">
      <h2 class="text-2xl font-semibold text-gray-800 mb-6 text-center">🔥 热门基金推荐</h2>
      
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        <div 
          v-for="(fund, index) in hotFunds" 
          :key="index"
          @click="selectHotFund(fund)"
          class="bg-white rounded-xl p-4 shadow hover:shadow-md transition-shadow cursor-pointer transform hover:scale-105"
        >
          <div class="flex items-center justify-between mb-2">
            <div>
              <div class="font-bold text-gray-900 text-lg">{{ fund.code }}</div>
              <div class="text-gray-600 text-sm mt-1">{{ fund.name }}</div>
            </div>
            <div class="text-yellow-500">
              <svg v-for="i in 5" :key="i" class="h-5 w-5 inline" :class="i <= fund.rating ? 'text-yellow-400' : 'text-gray-300'" fill="currentColor" viewBox="0 0 20 20">
                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
              </svg>
            </div>
          </div>
          <div class="flex justify-between text-sm">
            <span class="text-gray-500">{{ fund.type }}</span>
            <span class="text-green-600 font-medium">评级{{ fund.rating }}星</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 自定义选择区域 -->
    <div class="bg-white rounded-2xl shadow-lg p-8 mb-8">
      <h2 class="text-2xl font-semibold text-gray-800 mb-6 text-center">🔍 自定义选择</h2>
      
      <!-- 搜索框 -->
      <div class="mb-6">
        <label class="block text-lg font-medium text-gray-800 mb-3">搜索基金</label>
        <div class="flex space-x-4">
          <input 
            v-model="searchKeyword"
            @keyup.enter="searchFunds"
            type="text" 
            class="flex-1 rounded-xl border-2 border-gray-200 px-4 py-3 text-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
            placeholder="输入基金代码或名称，例如：易方达消费行业"
          />
          <button 
            @click="searchFunds"
            class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-xl font-medium text-lg transition-colors"
          >
            搜索
          </button>
        </div>
      </div>
      
      <!-- 搜索结果 -->
      <div v-if="searchResults.length > 0" class="mb-6">
        <h3 class="text-lg font-medium text-gray-800 mb-3">搜索结果</h3>
        <div class="max-h-60 overflow-y-auto border rounded-lg">
          <div 
            v-for="fund in searchResults" 
            :key="fund.code"
            @click="addFund(fund)"
            class="flex items-center p-4 hover:bg-gray-50 cursor-pointer border-b border-gray-100 last:border-b-0"
          >
            <div class="mr-4">
              <svg v-for="i in 5" :key="i" class="h-5 w-5 inline" :class="i <= fund.rating ? 'text-yellow-400' : 'text-gray-300'" fill="currentColor" viewBox="0 0 20 20">
                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
              </svg>
            </div>
            <div class="flex-1">
              <div class="font-bold text-gray-900">{{ fund.code }}</div>
              <div class="text-gray-600">{{ fund.name }}</div>
              <div class="text-sm text-gray-500">{{ fund.type }}</div>
            </div>
            <div class="text-green-600 font-medium">评级{{ fund.rating }}星</div>
          </div>
        </div>
      </div>
      
      <!-- 已选择基金 -->
      <div v-if="selectedFunds.length > 0" class="mb-6">
        <h3 class="text-lg font-medium text-gray-800 mb-3">已选择的基金 ({{ selectedFunds.length }})</h3>
        <div class="flex flex-wrap gap-3">
          <div 
            v-for="fund in selectedFunds" 
            :key="fund.code"
            class="bg-blue-100 text-blue-800 px-4 py-2 rounded-full flex items-center"
          >
            <span class="font-medium">{{ fund.code }}</span>
            <span class="ml-2 text-sm">{{ fund.name }}</span>
            <button 
              @click="removeFund(fund)" 
              class="ml-3 text-blue-600 hover:text-blue-800 font-bold"
            >
              ×
            </button>
          </div>
        </div>
      </div>
      
      <!-- 投资风格选择 -->
      <div class="mb-8">
        <label class="block text-lg font-medium text-gray-800 mb-3">选择您的投资风格</label>
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <button 
            v-for="style in investmentStyles" 
            :key="style.value"
            @click="selectedStyle = style.value"
            :class="[
              selectedStyle === style.value 
                ? 'bg-green-600 text-white border-green-600' 
                : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50',
              'border-2 rounded-xl p-6 text-center transition-all'
            ]"
          >
            <div class="text-2xl mb-2">{{ style.icon }}</div>
            <div class="font-bold text-lg mb-1">{{ style.name }}</div>
            <div class="text-sm">{{ style.description }}</div>
          </button>
        </div>
      </div>
      
      <!-- 开始分析按钮 -->
      <div class="text-center">
        <button 
          @click="startAnalysis"
          :disabled="selectedFunds.length === 0 || analyzing"
          class="bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700 text-white font-bold py-4 px-12 rounded-xl text-xl transition-all transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg"
        >
          {{ analyzing ? '分析中...' : '🚀 开始智能分析' }}
        </button>
        <p class="text-gray-500 text-sm mt-3">分析完成后，您将获得个性化的投资建议</p>
      </div>
    </div>
    
    <!-- 分析结果区域 -->
    <div v-if="analysisResult" class="bg-white rounded-2xl shadow-lg p-8">
      <div class="text-center mb-6">
        <h2 class="text-3xl font-bold text-gray-800 mb-2">📊 您的投资分析报告</h2>
        <p class="text-gray-600">基于{{ selectedFunds.length }}只基金的智能分析</p>
      </div>
      
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <!-- 预期收益 -->
        <div class="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl p-6">
          <div class="flex items-center mb-4">
            <div class="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mr-4">
              <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path>
              </svg>
            </div>
            <div>
              <h3 class="text-lg font-semibold text-gray-800">预期收益</h3>
              <p class="text-gray-600 text-sm">基于历史数据估算</p>
            </div>
          </div>
          <div class="text-3xl font-bold text-green-600 mb-2">{{ expectedReturn }}%</div>
          <p class="text-gray-600 text-sm">年化预期收益率</p>
        </div>
        
        <!-- 风险等级 -->
        <div class="bg-gradient-to-br from-yellow-50 to-orange-50 rounded-xl p-6">
          <div class="flex items-center mb-4">
            <div class="w-12 h-12 bg-yellow-100 rounded-full flex items-center justify-center mr-4">
              <svg class="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
              </svg>
            </div>
            <div>
              <h3 class="text-lg font-semibold text-gray-800">风险等级</h3>
              <p class="text-gray-600 text-sm">可能面临的最大亏损</p>
            </div>
          </div>
          <div class="text-3xl font-bold text-red-600 mb-2">{{ maxDrawdown }}%</div>
          <p class="text-gray-600 text-sm">在极端情况下可能的最大亏损</p>
        </div>
      </div>
      
      <!-- 组合配置 -->
      <div class="mt-8">
        <h3 class="text-xl font-semibold text-gray-800 mb-4 text-center">您的智能配置方案</h3>
        <div class="space-y-4">
          <div v-for="(weight, fundCode) in analysisResult.portfolio" :key="fundCode" class="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div class="flex items-center">
              <div class="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center mr-4">
                <span class="font-bold text-blue-600">{{ fundCode.slice(-2) }}</span>
              </div>
              <div>
                <div class="font-medium text-gray-800">{{ getFundName(fundCode) }}</div>
                <div class="text-sm text-gray-600">{{ fundCode }}</div>
              </div>
            </div>
            <div class="text-right">
              <div class="font-bold text-lg text-gray-800">{{ (weight * 100).toFixed(1) }}%</div>
              <div class="w-32 bg-gray-200 rounded-full h-2 mt-1">
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
      <div class="mt-8 p-6 bg-red-50 border border-red-200 rounded-xl">
        <div class="flex items-center mb-3">
          <svg class="w-6 h-6 text-red-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
          </svg>
          <h3 class="text-lg font-semibold text-red-800">重要风险提示</h3>
        </div>
        <div class="text-red-700 space-y-2">
          <p>• 基金投资有风险，过往业绩不代表未来表现</p>
          <p>• 根据您的投资风格，该组合属于<strong>{{ investmentStyleText }}</strong>类型</p>
          <p>• 在市场极端情况下，可能出现{{ maxDrawdown }}%的亏损</p>
          <p class="italic mt-3">本分析基于历史数据，仅供参考，不构成投资建议。投资前请仔细阅读基金合同和招募说明书。</p>
        </div>
      </div>
      
      <!-- 操作按钮 -->
      <div class="mt-8 text-center">
        <button 
          @click="resetAnalysis"
          class="bg-gray-600 hover:bg-gray-700 text-white font-medium py-3 px-8 rounded-xl transition-colors"
        >
          重新分析
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'UserFriendlyAnalyzer',
  data() {
    return {
      // 热门基金（精选20只）
      hotFunds: [
        { code: '000002', name: '易方达消费行业股票', type: '股票型', rating: 5 },
        { code: '000004', name: '富国天惠成长混合', type: '混合型', rating: 5 },
        { code: '000007', name: '景顺长城新兴成长混合', type: '混合型', rating: 5 },
        { code: '005669', name: '前海开源公用事业股票', type: '股票型', rating: 5 },
        { code: '005827', name: '易方达蓝筹精选混合', type: '混合型', rating: 5 },
        { code: '006751', name: '富国互联科技股票', type: '股票型', rating: 5 },
        { code: '161005', name: '富国天惠LOF', type: '混合型', rating: 5 },
        { code: '110022', name: '易方达消费行业股票A', type: '股票型', rating: 5 },
        { code: '260108', name: '景顺长城新兴成长混合', type: '混合型', rating: 5 },
        { code: '001744', name: '诺安成长混合', type: '混合型', rating: 4 },
        { code: '001616', name: '嘉实环保低碳股票', type: '股票型', rating: 4 },
        { code: '000001', name: '华夏成长混合', type: '混合型', rating: 4 },
        { code: '000003', name: '嘉实新兴产业股票', type: '股票型', rating: 4 },
        { code: '000005', name: '兴全合润混合', type: '混合型', rating: 4 },
        { code: '000006', name: '中欧医疗健康混合', type: '混合型', rating: 4 },
        { code: '000008', name: '汇添富价值精选混合', type: '混合型', rating: 4 },
        { code: '000009', name: '工银瑞信前沿医疗股票', type: '股票型', rating: 4 },
        { code: '000010', name: '广发稳健增长混合', type: '混合型', rating: 4 },
        { code: '001632', name: '泓德泓富混合', type: '混合型', rating: 4 },
        { code: '003096', name: '中欧医疗健康混合C', type: '混合型', rating: 4 }
      ],
      
      // 投资风格选项
      investmentStyles: [
        {
          value: 'conservative',
          name: '保守型',
          icon: '🛡️',
          description: '注重本金安全，接受较低收益',
          riskLevel: 0.3
        },
        {
          value: 'balanced',
          name: '稳健型', 
          icon: '⚖️',
          description: '平衡收益与风险，适合大多数投资者',
          riskLevel: 0.5
        },
        {
          value: 'aggressive',
          name: '激进型',
          icon: '🚀',
          description: '追求高收益，能承受较大波动',
          riskLevel: 0.7
        }
      ],
      
      // 用户输入
      searchKeyword: '',
      searchResults: [],
      selectedFunds: [],
      selectedStyle: 'balanced',
      
      // 分析状态
      analyzing: false,
      analysisResult: null
    };
  },
  computed: {
    expectedReturn() {
      if (!this.analysisResult) return '0';
      const annualReturn = this.analysisResult.portfolioMetrics.annual_return;
      return (annualReturn * 100).toFixed(1);
    },
    maxDrawdown() {
      if (!this.analysisResult) return '0';
      const drawdown = this.analysisResult.portfolioMetrics.max_drawdown;
      return (Math.abs(drawdown) * 100).toFixed(1);
    },
    investmentStyleText() {
      const styleMap = {
        'conservative': '保守型',
        'balanced': '稳健型', 
        'aggressive': '激进型'
      };
      return styleMap[this.selectedStyle] || '稳健型';
    }
  },
  methods: {
    async searchFunds() {
      if (!this.searchKeyword.trim()) {
        this.searchResults = [];
        return;
      }
      
      try {
        const params = { keyword: this.searchKeyword, limit: 10 };
        const response = await axios.get('/api/funds/search', { params });
        
        if (response.data.status === 'success') {
          this.searchResults = response.data.funds;
        }
      } catch (error) {
        console.error('搜索基金失败:', error);
        alert('搜索基金失败，请稍后重试');
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
    
    selectHotFund(fund) {
      if (!this.selectedFunds.find(f => f.code === fund.code)) {
        this.selectedFunds.push(fund);
      }
    },
    
    getFundName(fundCode) {
      const selectedFund = this.selectedFunds.find(f => f.code === fundCode);
      if (selectedFund) {
        return selectedFund.name;
      }
      
      const hotFund = this.hotFunds.find(f => f.code === fundCode);
      if (hotFund) {
        return hotFund.name;
      }
      
      return `基金${fundCode}`;
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
        
        // 获取风险偏好
        const selectedStyleObj = this.investmentStyles.find(s => s.value === this.selectedStyle);
        const riskTolerance = selectedStyleObj ? selectedStyleObj.riskLevel : 0.5;
        
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
        alert('分析失败，请稍后重试');
      } finally {
        this.analyzing = false;
      }
    },
    
    resetAnalysis() {
      this.analysisResult = null;
      this.selectedFunds = [];
      this.selectedStyle = 'balanced';
    }
  }
};
</script>