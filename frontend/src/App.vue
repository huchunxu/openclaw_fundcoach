<template>
  <div id="app" class="min-h-screen bg-gray-50">
    <!-- 头部导航 -->
    <header class="bg-white shadow-sm">
      <div class="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
        <h1 class="text-3xl font-bold text-gray-900">基金智能助手</h1>
        <p class="mt-2 text-gray-600">帮您轻松选择优质基金，智能配置投资组合</p>
      </div>
    </header>
    
    <!-- 主要内容 -->
    <main class="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
      <UserFriendlyAnalyzer />
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
import UserFriendlyAnalyzer from './components/UserFriendlyAnalyzer.vue';

export default {
  name: 'App',
  components: {
    UserFriendlyAnalyzer
  }
};
</script>