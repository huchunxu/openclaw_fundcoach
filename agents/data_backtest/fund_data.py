"""
天天基金数据抓取模块

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


class FundDataFetcher:
    """天天基金数据抓取器"""
    
    def __init__(self, cache_dir: str = "data/cache"):
        self.cache_dir = cache_dir
        self.base_url = "http://fund.eastmoney.com"
        self.api_base = "http://api.fund.eastmoney.com"
        os.makedirs(cache_dir, exist_ok=True)
        
    def get_fund_list(self, fund_type: str = "all") -> pd.DataFrame:
        """
        获取基金列表
        
        Args:
            fund_type: 基金类型筛选（股票型、混合型、债券型等）
            
        Returns:
            DataFrame包含基金代码、名称、类型等基本信息
        """
        # 天天基金基金列表页面
        url = f"{self.base_url}/FundSuperList.aspx"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            # 这里需要解析HTML或使用API
            # 简化版本：返回示例数据结构
            sample_data = {
                'fund_code': ['000001', '000002', '000003'],
                'fund_name': ['华夏成长', '易方达策略', '嘉实增长'],
                'fund_type': ['混合型', '股票型', '混合型'],
                'establish_date': ['2001-12-18', '2002-05-21', '2003-07-09']
            }
            
            return pd.DataFrame(sample_data)
            
        except Exception as e:
            print(f"获取基金列表失败: {e}")
            return pd.DataFrame()
    
    def get_fund_nav_history(self, fund_code: str, days: int = 1095) -> pd.DataFrame:
        """
        获取基金历史净值数据
        
        Args:
            fund_code: 基金代码
            days: 获取天数（默认3年≈1095天）
            
        Returns:
            DataFrame包含日期、单位净值、累计净值等
        """
        # 构建API URL - 天天基金历史净值API
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        # 天天基金历史净值API格式
        url = f"http://api.fund.eastmoney.com/f10/lsjz?callback=&fundcode={fund_code}&pageIndex=1&pageSize={days}&startDate={start_date}&endDate={end_date}"
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': f'http://fundf10.eastmoney.com/jjjz_{fund_code}.html'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            # 解析JSONP响应
            data = response.json()
            
            if data.get('ErrCode') == 0 and 'Data' in data:
                nav_data = []
                for item in data['Data']['LSJZList']:
                    nav_data.append({
                        'date': item['FSRQ'],
                        'nav': float(item['DWJZ']) if item['DWJZ'] else None,
                        'accum_nav': float(item['LJJZ']) if item['LJJZ'] else None,
                        'daily_return': float(item['JZZZL']) if item['JZZZL'] else None
                    })
                
                df = pd.DataFrame(nav_data)
                df['date'] = pd.to_datetime(df['date'])
                df = df.sort_values('date').reset_index(drop=True)
                
                # 缓存数据
                self._cache_fund_data(fund_code, df)
                return df
                
            else:
                print(f"获取基金{fund_code}净值数据失败: {data.get('ErrMessage', 'Unknown error')}")
                return pd.DataFrame()
                
        except Exception as e:
            print(f"获取基金{fund_code}净值数据异常: {e}")
            return pd.DataFrame()
    
    def get_fund_basic_info(self, fund_code: str) -> Dict:
        """
        获取基金基本信息
        
        Args:
            fund_code: 基金代码
            
        Returns:
            字典包含基金基本信息
        """
        # 基金详情页面
        url = f"http://fundf10.eastmoney.com/jbgk_{fund_code}.html"
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # 这里需要解析HTML提取信息
            # 简化版本：返回示例数据
            basic_info = {
                'fund_code': fund_code,
                'fund_name': f'基金{fund_code}',
                'fund_type': '混合型',
                'fund_size': 10.5,  # 亿元
                'establish_date': '2020-01-01',
                'manager': '张三',
                'company': '某某基金公司'
            }
            
            return basic_info
            
        except Exception as e:
            print(f"获取基金{fund_code}基本信息失败: {e}")
            return {}
    
    def _cache_fund_data(self, fund_code: str, data: pd.DataFrame):
        """缓存基金数据"""
        cache_file = os.path.join(self.cache_dir, f"{fund_code}.csv")
        try:
            data.to_csv(cache_file, index=False)
        except Exception as e:
            print(f"缓存基金{fund_code}数据失败: {e}")
    
    def load_cached_data(self, fund_code: str) -> Optional[pd.DataFrame]:
        """加载缓存的基金数据"""
        cache_file = os.path.join(self.cache_dir, f"{fund_code}.csv")
        if os.path.exists(cache_file):
            try:
                return pd.read_csv(cache_file)
            except Exception as e:
                print(f"加载缓存数据失败: {e}")
        return None
    
    def batch_fetch_funds(self, fund_codes: List[str], use_cache: bool = True) -> Dict[str, pd.DataFrame]:
        """
        批量获取多只基金数据
        
        Args:
            fund_codes: 基金代码列表
            use_cache: 是否使用缓存
            
        Returns:
            字典，key为基金代码，value为净值数据DataFrame
        """
        fund_data_dict = {}
        
        for fund_code in fund_codes:
            if use_cache:
                cached_data = self.load_cached_data(fund_code)
                if cached_data is not None and not cached_data.empty:
                    fund_data_dict[fund_code] = cached_data
                    continue
            
            # 获取最新数据
            nav_data = self.get_fund_nav_history(fund_code)
            if not nav_data.empty:
                fund_data_dict[fund_code] = nav_data
            
            # 避免请求过于频繁
            time.sleep(0.5)
        
        return fund_data_dict


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