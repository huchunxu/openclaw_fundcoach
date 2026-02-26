"""
天天基金数据抓取模块（整合真实数据）

功能：
- 获取基金列表
- 抓取历史净值数据（3年）
- 获取基金基本信息（规模、类型、成立时间等）
- 数据缓存和更新机制
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import json
import time
from typing import List, Dict, Optional
from .fund_data_real import RealFundDataFetcher


class FundDataFetcher:
    """天天基金数据抓取器"""
    
    def __init__(self, cache_dir: str = "data/cache"):
        self.real_fetcher = RealFundDataFetcher(cache_dir)
        
    def get_fund_list(self, fund_type: str = "all") -> pd.DataFrame:
        """
        获取基金列表
        
        Args:
            fund_type: 基金类型筛选（股票型、混合型、债券型等）
            
        Returns:
            DataFrame包含基金代码、名称、类型等基本信息
        """
        return self.real_fetcher.get_fund_list_real(fund_type)
    
    def get_fund_nav_history(self, fund_code: str, days: int = 1095) -> pd.DataFrame:
        """
        获取基金历史净值数据
        
        Args:
            fund_code: 基金代码
            days: 获取天数（默认3年≈1095天）
            
        Returns:
            DataFrame包含日期、单位净值、累计净值等
        """
        return self.real_fetcher.get_fund_nav_history_real(fund_code, days)
    
    def get_fund_basic_info(self, fund_code: str) -> Dict:
        """
        获取基金基本信息
        
        Args:
            fund_code: 基金代码
            
        Returns:
            字典包含基金基本信息
        """
        return self.real_fetcher.get_fund_basic_info_real(fund_code)
    
    def _cache_fund_data(self, fund_code: str, data: pd.DataFrame):
        """缓存基金数据"""
        self.real_fetcher._cache_fund_data(fund_code, data)
    
    def load_cached_data(self, fund_code: str) -> Optional[pd.DataFrame]:
        """加载缓存的基金数据"""
        return self.real_fetcher.load_cached_data(fund_code)
    
    def batch_fetch_funds(self, fund_codes: List[str], use_cache: bool = True) -> Dict[str, pd.DataFrame]:
        """
        批量获取多只基金数据
        
        Args:
            fund_codes: 基金代码列表
            use_cache: 是否使用缓存
            
        Returns:
            字典，key为基金代码，value为净值数据DataFrame
        """
        return self.real_fetcher.batch_fetch_funds_real(fund_codes, use_cache)


if __name__ == "__main__":
    # 测试代码
    fetcher = FundDataFetcher()
    
    # 测试获取单只基金数据
    test_fund = "000001"
    nav_data = fetcher.get_fund_nav_history(test_fund)
    print(f"基金{test_fund}数据形状: {nav_data.shape}")
    print(nav_data.head())
    
    # 测试获取基金列表
    fund_list = fetcher.get_fund_list()
    print(f"基金列表形状: {fund_list.shape}")
    print(fund_list.head())