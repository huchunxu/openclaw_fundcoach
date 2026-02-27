<template>
  <div class="portfolio-optimizer">
    <h2 class="text-2xl font-bold mb-4">组合优化器</h2>
    
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- 基金池输入区域 -->
      <div class="lg:col-span-2 bg-white p-6 rounded-lg shadow">
        <h3 class="text-lg font-semibold mb-4">基金池配置</h3>
        <div class="space-y-4">
          <div v-for="(fund, index) in fundPool" :key="index" class="flex space-x-2">
            <input 
              v-model="fund.code"
              type="text" 
              class="block w-24 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              placeholder="代码"
            />
            <textarea 
              v-model="fund.returns"
              rows="2"
              class="block flex-1 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              placeholder='[0.01, -0.02, 0.03, ...]'
            ></textarea>
            <button 
              @click="removeFund(index)"
              class="bg-red-600 hover:bg-red-700 text-white px-2 rounded-md"
            >
              ×
            </button>
          </div>
          
          <button 
            @click="addFund"
            class="bg-gray-600 hover:bg-gray-700 text-white font-medium py-1 px-3 rounded-md"
          >
            添加基金
          </button>
        </div>
        
        <div class="mt-6">
          <label class="block text-sm font-medium text-gray-700 mb-2">风险容忍度</label>
          <input 
            v-model="riskTolerance"
            type="range" 
            min="0" 
            max="1" 
            step="0.1"
            class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
          />
          <div class="flex justify-between text-sm text-gray-600">
            <span>保守 (0)</span>
            <span>中等 (0.5)</span>
            <span>激进 (1)</span>
          </div>
          <div class="text-center mt-1">{{ riskTolerance }}</div>
        </div>
        
        <button 
          @click="optimizePortfolio" 
          :disabled="optimizing"
          class="mt-6 w-full bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-4 rounded-md transition duration-150 ease-in-out"
        >
          {{ optimizing ? '优化中...' : '优化组合' }}
        </button>
      </div>
      
      <!-- 优化结果区域 -->
      <div class="bg-white p-6 rounded-lg shadow" v-if="optimizationResult">
        <h3 class="text-lg font-semibold mb-4">优化结果</h3>
        <div class="space-y-4">
          <div v-for="(weight, fundCode) in optimizationResult.portfolio" :key="fundCode">
            <div class="flex justify-between">
              <span class="font-medium">{{ fundCode }}</span>
              <span>{{ (weight * 100).toFixed(2) }}%</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2 mt-1">
              <div 
                class="bg-blue-600 h-2 rounded-full" 
                :style="{ width: (weight * 100) + '%' }"
              ></div>
            </div>
          </div>
          
          <div class="border-t pt-4">
            <h4 class="font-medium mb-2">组合统计:</h4>
            <div class="text-sm space-y-1">
              <div>基金数量: {{ Object.keys(optimizationResult.portfolio).length }}</div>
              <div>权重总和: {{ portfolioSum.toFixed(4) }}</div>
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
  name: 'PortfolioOptimizer',
  data() {
    return {
      fundPool: [
        { code: '', returns: '' }
      ],
      riskTolerance: 0.5,
      optimizing: false,
      optimizationResult: null
    };
  },
  computed: {
    portfolioSum() {
      if (!this.optimizationResult) return 0;
      return Object.values(this.optimizationResult.portfolio).reduce((sum, weight) => sum + weight, 0);
    }
  },
  methods: {
    addFund() {
      this.fundPool.push({ code: '', returns: '' });
    },
    removeFund(index) {
      if (this.fundPool.length > 1) {
        this.fundPool.splice(index, 1);
      }
    },
    async optimizePortfolio() {
      try {
        // 验证输入
        const validFunds = this.fundPool.filter(fund => 
          fund.code && fund.returns
        );
        
        if (validFunds.length === 0) {
          alert('请至少输入一只有效的基金');
          return;
        }
        
        // 构建基金池数据
        const fundPoolData = {};
        for (const fund of validFunds) {
          try {
            const returns = JSON.parse(fund.returns);
            fundPoolData[fund.code] = { returns };
          } catch (e) {
            alert(`基金 ${fund.code} 的收益率数据格式错误`);
            return;
          }
        }
        
        this.optimizing = true;
        
        const response = await axios.post('/api/optimize', {
          fund_pool: fundPoolData,
          risk_tolerance: parseFloat(this.riskTolerance)
        });
        
        if (response.data.status === 'success') {
          this.optimizationResult = response.data;
        } else {
          throw new Error(response.data.error);
        }
      } catch (error) {
        console.error('优化失败:', error);
        alert('优化失败: ' + error.message);
      } finally {
        this.optimizing = false;
      }
    }
  }
};
</script>