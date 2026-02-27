#!/usr/bin/env python3
"""
Data Agent - 基金数据抓取和处理
"""

import requests
import json
import time
import os
from typing import Dict, List, Optional
import logging

class DataAgent:
    """数据智能体：负责基金数据抓取、处理和缓存"""
    
    def __init__(self, cache_dir: str = "data_cache"):
        self.cache_dir = cache_dir
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # 创建缓存目录
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def _get_cache_path(self, fund_code: str) -> str:
        """获取缓存文件路径"""
        return os.path.join(self.cache_dir, f"{fund_code}.json")
    
    def _is_cache_valid(self, cache_path: str, max_age_hours: int = 24) -> bool:
        """检查缓存是否有效"""
        if not os.path.exists(cache_path):
            return False
        
        file_age = time.time() - os.path.getmtime(cache_path)
        return file_age < (max_age_hours * 3600)
    
    def _save_to_cache(self, fund_code: str, data: Dict):
        """保存数据到缓存"""
        cache_path = self._get_cache_path(fund_code)
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _load_from_cache(self, fund_code: str) -> Optional[Dict]:
        """从缓存加载数据"""
        cache_path = self._get_cache_path(fund_code)
        if os.path.exists(cache_path):
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load cache for {fund_code}: {e}")
                return None
        return None
    
    def fetch_fund_basic_info(self, fund_code: str) -> Optional[Dict]:
        """抓取基金基本信息（模拟天天基金API）"""
        # 检查缓存
        cache_data = self._load_from_cache(fund_code)
        if cache_data and 'basic_info' in cache_data:
            return cache_data['basic_info']
        
        try:
            # 模拟从天天基金获取数据
            # 实际项目中这里会调用真实的API
            basic_info = {
                'code': fund_code,
                'name': f"模拟基金{fund_code}",
                'type': '混合型',
                'manager': '模拟基金经理',
                'establishment_date': '2018-01-01',
                'size': 10.5,  # 亿元
                'rating': 4,
                'company': '模拟基金公司'
            }
            
            # 保存到缓存
            cache_data = cache_data or {}
            cache_data['basic_info'] = basic_info
            self._save_to_cache(fund_code, cache_data)
            
            return basic_info
            
        except Exception as e:
            self.logger.error(f"Failed to fetch basic info for {fund_code}: {e}")
            return None
    
    def fetch_fund_nav_history(self, fund_code: str, days: int = 1000) -> Optional[List[Dict]]:
        """抓取基金净值历史数据（模拟数据）"""
        # 检查缓存
        cache_data = self._load_from_cache(fund_code)
        if (cache_data and 'nav_history' in cache_data and 
            len(cache_data['nav_history']) >= days):
            return cache_data['nav_history'][:days]
        
        try:
            # 生成模拟净值数据
            import random
            nav_history = []
            current_nav = 1.0
            
            for i in range(days):
                # 模拟每日收益率（正态分布，均值0.001，标准差0.02）
                daily_return = random.gauss(0.001, 0.02)
                current_nav *= (1 + daily_return)
                
                nav_history.append({
                    'date': f"2023-{str(12 - (i // 30)).zfill(2)}-{str(30 - (i % 30)).zfill(2)}",
                    'nav': round(current_nav, 4),
                    'daily_return': daily_return
                })
            
            # 保存到缓存
            cache_data = cache_data or {}
            cache_data['nav_history'] = nav_history
            self._save_to_cache(fund_code, cache_data)
            
            return nav_history[:days]
            
        except Exception as e:
            self.logger.error(f"Failed to fetch NAV history for {fund_code}: {e}")
            return None
    
    def get_fund_pool(self, fund_codes: List[str]) -> Dict[str, Dict]:
        """获取基金池数据"""
        fund_pool = {}
        
        for fund_code in fund_codes:
            # 获取基本信息
            basic_info = self.fetch_fund_basic_info(fund_code)
            if not basic_info:
                continue
            
            # 获取净值历史
            nav_history = self.fetch_fund_nav_history(fund_code, days=500)
            if not nav_history:
                continue
            
            # 提取收益率序列
            returns = [item['daily_return'] for item in nav_history]
            
            fund_pool[fund_code] = {
                'basic_info': basic_info,
                'returns': returns,
                'nav_history': nav_history
            }
        
        return fund_pool
    
    def search_funds(self, keyword: str = "", limit: int = 50) -> List[Dict]:
        """搜索基金（返回模拟的热门基金列表）"""
        # 模拟热门基金列表
        popular_funds = [
            {'code': '000001', 'name': '华夏成长混合', 'type': '混合型', 'rating': 4},
            {'code': '000002', 'name': '易方达消费行业股票', 'type': '股票型', 'rating': 5},
            {'code': '000003', 'name': '嘉实新兴产业股票', 'type': '股票型', 'rating': 4},
            {'code': '000004', 'name': '富国天惠成长混合', 'type': '混合型', 'rating': 5},
            {'code': '000005', 'name': '兴全合润混合', 'type': '混合型', 'rating': 4},
            {'code': '000006', 'name': '中欧医疗健康混合', 'type': '混合型', 'rating': 4},
            {'code': '000007', 'name': '景顺长城新兴成长混合', 'type': '混合型', 'rating': 5},
            {'code': '000008', 'name': '汇添富价值精选混合', 'type': '混合型', 'rating': 4},
            {'code': '000009', 'name': '工银瑞信前沿医疗股票', 'type': '股票型', 'rating': 4},
            {'code': '000010', 'name': '广发稳健增长混合', 'type': '混合型', 'rating': 4},
            {'code': '161005', 'name': '富国天惠LOF', 'type': '混合型', 'rating': 5},
            {'code': '110022', 'name': '易方达消费行业股票', 'type': '股票型', 'rating': 5},
            {'code': '001632', 'name': '泓德泓富混合', 'type': '混合型', 'rating': 4},
            {'code': '003096', 'name': '中欧医疗健康混合C', 'type': '混合型', 'rating': 4},
            {'code': '005669', 'name': '前海开源公用事业股票', 'type': '股票型', 'rating': 5}
        ]
        
        if keyword:
            # 简单关键词匹配
            filtered_funds = [
                fund for fund in popular_funds 
                if keyword.lower() in fund['name'].lower() or keyword in fund['code']
            ]
            return filtered_funds[:limit]
        else:
            return popular_funds[:limit]
    
    def get_fund_list(self, page: int = 1, page_size: int = 20) -> Dict:
        """获取基金列表分页数据"""
        all_funds = self.search_funds()
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        
        paginated_funds = all_funds[start_idx:end_idx]
        
        return {
            'funds': paginated_funds,
            'total': len(all_funds),
            'page': page,
            'page_size': page_size,
            'total_pages': (len(all_funds) + page_size - 1) // page_size
        }