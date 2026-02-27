<template>
  <div class="risk-analyzer">
    <h2 class="text-2xl font-bold mb-4">风险分析器</h2>
    
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- 组合配置区域 -->
      <div class="lg:col-span-2 bg-white p-6 rounded-lg shadow">
        <h3 class="text-lg font-semibold mb-4">组合配置</h3>
        <div class="space-y-4">
          <div v-for="(position, index) in portfolio" :key="index" class="flex space-x-2">
            <input 
              v-model="position.fundCode"
              type="text" 
              class="block w-24 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              placeholder="代码"
            />
            <input 
              v-model="position.weight"
              type="number" 
              step="0.01"
              min="0"
              max="1"
              class="block w-24 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              placeholder="权重"
            />
            <textarea 
              v-model="position.returns"
              rows="2"
              class="block flex-1 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              placeholder='[0.01, -0.02, 0.03, ...]'
            ></textarea>
            <button 
              @click="removePosition(index)"
              class="bg-red-600 hover:bg-red-700 text-white px-2 rounded-md"
            >
              ×
            </button>
          </div>
          
          <button 
            @click="addPosition"
            class="bg-gray-600 hover:bg-gray-700 text-white font-medium py-1 px-3 rounded-md"
          >
            添加持仓
          </button>
        </div>
        
        <button 
          @click="analyzeRisk" 
          :disabled="analyzingRisk"
          class="mt-6 w-full bg-purple-600 hover:bg-purple-700 text-white font-medium py-2 px-4 rounded-md transition duration-150 ease-in-out"
        >
          {{ analyzingRisk ? '分析中...' : '分析风险' }}
        </button>
      </div>
      
      <!-- 风险分析结果区域 -->
      <div class="bg-white p-6 rounded-lg shadow" v-if="riskAnalysisResult">
        <h3 class="text-lg font-semibold mb-4">风险分析结果</h3>
        
        <!-- 风险等级 -->
        <div class="mb-4">
          <div class="flex items-center justify-between">
            <span class="font-medium">风险等级:</span>
            <span :class="{
              'text-green-600': riskAnalysisResult.risk_report.risk_assessment.risk_level === 'low',
              'text-yellow-600': riskAnalysisResult.risk_report.risk_assessment.risk_level === 'medium',
              'text-red-600': riskAnalysisResult.risk_report.risk_assessment.risk_level === 'high'
            }" class="font-bold capitalize">
              {{ riskAnalysisResult.risk_report.risk_assessment.risk_level }}
            </span>
          </div>
        </div>
        
        <!-- 核心指标 -->
        <div class="space-y-3 mb-4">
          <div class="flex justify-between">
            <span>年化收益率:</span>
            <span>{{ (riskAnalysisResult.risk_report.risk_metrics.annual_return * 100).toFixed(2) }}%</span>
          </div>
          <div class="flex justify-between">
            <span>波动率:</span>
            <span>{{ (riskAnalysisResult.risk_report.risk_metrics.volatility * 100).toFixed(2) }}%</span>
          </div>
          <div class="flex justify-between">
            <span>夏普率:</span>
            <span>{{ riskAnalysisResult.risk_report.risk_metrics.sharpe_ratio.toFixed(3) }}</span>
          </div>
          <div class="flex justify-between">
            <span>最大回撤:</span>
            <span class="text-red-600">{{ (riskAnalysisResult.risk_report.risk_metrics.max_drawdown * 100).toFixed(2) }}%</span>
          </div>
        </div>
        
        <!-- 风险提示 -->
        <div class="border-t pt-4">
          <h4 class="font-medium mb-2">风险提示:</h4>
          <div class="text-sm text-gray-700 space-y-1">
            <div v-if="riskAnalysisResult.risk_report.risk_assessment.alerts.length > 0">
              <div v-for="(alert, index) in riskAnalysisResult.risk_report.risk_assessment.alerts" :key="index" class="text-red-600">
                ⚠️ {{ alert }}
              </div>
            </div>
            <div v-else>
              ✅ 组合风险在可接受范围内
            </div>
            
            <div class="mt-2 italic text-gray-600">
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
  name: 'RiskAnalyzer',
  data() {
    return {
      portfolio: [
        { fundCode: '', weight: '', returns: '' }
      ],
      analyzingRisk: false,
      riskAnalysisResult: null
    };
  },
  methods: {
    addPosition() {
      this.portfolio.push({ fundCode: '', weight: '', returns: '' });
    },
    removePosition(index) {
      if (this.portfolio.length > 1) {
        this.portfolio.splice(index, 1);
      }
    },
    async analyzeRisk() {
      try {
        // 验证输入
        const validPositions = this.portfolio.filter(pos => 
          pos.fundCode && pos.weight !== '' && pos.returns
        );
        
        if (validPositions.length === 0) {
          alert('请至少输入一个有效的持仓');
          return;
        }
        
        // 构建组合权重和基金池
        const portfolioWeights = {};
        const fundPool = {};
        let totalWeight = 0;
        
        for (const pos of validPositions) {
          const weight = parseFloat(pos.weight);
          if (isNaN(weight) || weight <= 0) {
            alert(`持仓 ${pos.fundCode} 的权重无效`);
            return;
          }
          
          portfolioWeights[pos.fundCode] = weight;
          totalWeight += weight;
          
          try {
            const returns = JSON.parse(pos.returns);
            fundPool[pos.fundCode] = { returns };
          } catch (e) {
            alert(`基金 ${pos.fundCode} 的收益率数据格式错误`);
            return;
          }
        }
        
        // 检查权重总和
        if (Math.abs(totalWeight - 1.0) > 0.01) {
          alert('持仓权重总和应该接近1.0（当前: ' + totalWeight.toFixed(3) + '）');
          return;
        }
        
        this.analyzingRisk = true;
        
        const response = await axios.post('/api/risk', {
          portfolio_weights: portfolioWeights,
          fund_pool: fundPool
        });
        
        if (response.data.status === 'success') {
          this.riskAnalysisResult = response.data;
        } else {
          throw new Error(response.data.error);
        }
      } catch (error) {
        console.error('风险分析失败:', error);
        alert('风险分析失败: ' + error.message);
      } finally {
        this.analyzingRisk = false;
      }
    }
  }
};
</script>