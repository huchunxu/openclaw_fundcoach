<template>
  <div class="strategy-analyzer">
    <h2 class="text-2xl font-bold mb-4">基金策略分析</h2>
    
    <!-- 已选择的基金信息 -->
    <div v-if="selectedFund" class="mb-6 bg-blue-50 p-4 rounded-lg">
      <h3 class="text-lg font-semibold mb-2">已选择基金</h3>
      <p class="text-blue-800">{{ selectedFund.code }} - {{ selectedFund.name }}</p>
      <button 
        @click="analyzeSelectedFund" 
        :disabled="analyzing"
        class="mt-2 bg-blue-600 hover:bg-blue-700 text-white font-medium py-1 px-3 rounded-md"
      >
        {{ analyzing ? '分析中...' : '分析选中基金' }}
      </button>
    </div>
    
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <!-- 基金输入区域 -->
      <div class="bg-white p-6 rounded-lg shadow">
        <h3 class="text-lg font-semibold mb-4">输入基金数据</h3>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700">基金代码</label>
            <input 
              v-model="fundCode" 
              type="text" 
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              placeholder="例如: 000001"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700">历史收益率数据 (JSON格式)</label>
            <textarea 
              v-model="fundReturns" 
              rows="6"
              class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              placeholder='[0.01, -0.02, 0.03, ...]'
            ></textarea>
          </div>
          
          <button 
            @click="analyzeFund" 
            :disabled="analyzing"
            class="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-md transition duration-150 ease-in-out"
          >
            {{ analyzing ? '分析中...' : '分析基金' }}
          </button>
        </div>
      </div>
      
      <!-- 分析结果区域 -->
      <div class="bg-white p-6 rounded-lg shadow" v-if="analysisResult">
        <h3 class="text-lg font-semibold mb-4">分析结果</h3>
        <div class="space-y-4">
          <div class="flex justify-between">
            <span class="text-gray-600">综合得分:</span>
            <span class="font-semibold">{{ analysisResult.score.toFixed(3) }}</span>
          </div>
          
          <div class="flex justify-between">
            <span class="text-gray-600">风格分类:</span>
            <span class="font-semibold capitalize">{{ analysisResult.style }}</span>
          </div>
          
          <div class="border-t pt-4">
            <h4 class="font-medium mb-2">因子详情:</h4>
            <div class="grid grid-cols-2 gap-2 text-sm">
              <div>一年收益: {{ analysisResult.factors.return_1y.toFixed(4) }}</div>
              <div>夏普率: {{ analysisResult.factors.sharpe_ratio.toFixed(4) }}</div>
              <div>最大回撤: {{ (analysisResult.factors.max_drawdown * 100).toFixed(2) }}%</div>
              <div>波动率: {{ (analysisResult.factors.volatility * 100).toFixed(2) }}%</div>
              <div>收益一致性: {{ (analysisResult.factors.consistency * 100).toFixed(2) }}%</div>
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
  name: 'StrategyAnalyzer',
  props: {
    selectedFund: {
      type: Object,
      default: null
    }
  },
  data() {
    return {
      fundCode: '',
      fundReturns: '',
      analyzing: false,
      analysisResult: null
    };
  },
  methods: {
    async analyzeFund() {
      if (!this.fundCode || !this.fundReturns) {
        alert('请输入完整的基金信息');
        return;
      }
      
      try {
        this.analyzing = true;
        const returns = JSON.parse(this.fundReturns);
        
        const response = await axios.post('/api/factors', {
          fund_data: { returns }
        });
        
        if (response.data.status === 'success') {
          this.analysisResult = response.data;
        } else {
          throw new Error(response.data.error);
        }
      } catch (error) {
        console.error('分析失败:', error);
        alert('分析失败: ' + error.message);
      } finally {
        this.analyzing = false;
      }
    },
    async analyzeSelectedFund() {
      if (!this.selectedFund) return;
      
      try {
        this.analyzing = true;
        
        // 获取基金详细数据
        const response = await axios.get(`/api/funds/${this.selectedFund.code}`);
        
        if (response.data.status === 'success') {
          const returns = response.data.nav_history.map(item => item.daily_return);
          
          const factorResponse = await axios.post('/api/factors', {
            fund_data: { returns }
          });
          
          if (factorResponse.data.status === 'success') {
            this.analysisResult = factorResponse.data;
          } else {
            throw new Error(factorResponse.data.error);
          }
        } else {
          throw new Error(response.data.error);
        }
      } catch (error) {
        console.error('分析选中基金失败:', error);
        alert('分析选中基金失败: ' + error.message);
      } finally {
        this.analyzing = false;
      }
    }
  }
};
</script>