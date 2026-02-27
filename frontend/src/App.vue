<template>
  <div id="app" class="min-h-screen bg-gray-50">
    <!-- 头部导航 -->
    <header class="bg-white shadow">
      <div class="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
        <h1 class="text-3xl font-bold text-gray-900">OpenClaw FundCoach</h1>
        <p class="mt-2 text-gray-600">中国公募基金量化组合研究与模拟智能体</p>
      </div>
    </header>
    
    <!-- 主要内容 -->
    <main class="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
      <!-- 导航选项卡 -->
      <div class="border-b border-gray-200 mb-8">
        <nav class="-mb-px flex space-x-8">
          <button
            v-for="(tab, index) in tabs"
            :key="index"
            @click="activeTab = index"
            :class="[
              activeTab === index
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
              'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm'
            ]"
          >
            {{ tab }}
          </button>
        </nav>
      </div>
      
      <!-- 选项卡内容 -->
      <div v-if="activeTab === 0">
        <SmartAnalyzer />
      </div>
      <div v-else-if="activeTab === 1">
        <FundList @fund-selected="handleFundSelected" />
      </div>
      <div v-else-if="activeTab === 2">
        <StrategyAnalyzer :selected-fund="selectedFund" />
      </div>
      <div v-else-if="activeTab === 3">
        <PortfolioOptimizer />
      </div>
      <div v-else-if="activeTab === 4">
        <RiskAnalyzer />
      </div>
    </main>
    
    <!-- 页脚 -->
    <footer class="bg-white mt-12 border-t border-gray-200">
      <div class="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
        <p class="text-center text-gray-500 text-sm">
          历史数据仅供参考，不构成投资建议。投资有风险，入市需谨慎。
        </p>
      </div>
    </footer>
  </div>
</template>

<script>
import SmartAnalyzer from './components/SmartAnalyzer.vue';
import FundList from './components/FundList.vue';
import StrategyAnalyzer from './components/StrategyAnalyzer.vue';
import PortfolioOptimizer from './components/PortfolioOptimizer.vue';
import RiskAnalyzer from './components/RiskAnalyzer.vue';

export default {
  name: 'App',
  components: {
    SmartAnalyzer,
    FundList,
    StrategyAnalyzer,
    PortfolioOptimizer,
    RiskAnalyzer
  },
  data() {
    return {
      activeTab: 0,
      tabs: ['智能分析', '基金列表', '策略分析', '组合优化', '风险分析'],
      selectedFund: null
    };
  },
  methods: {
    handleFundSelected(fund) {
      this.selectedFund = fund;
      this.activeTab = 2; // 切换到策略分析页面
    }
  }
};
</script>