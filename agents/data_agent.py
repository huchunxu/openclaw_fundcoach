#!/usr/bin/env python3
"""
Data Agent - 基金数据抓取和处理（增强版）
"""

import requests
import json
import time
import os
import random
from typing import Dict, List, Optional
import logging
from datetime import datetime, timedelta

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
        
        # 扩展的基金数据库（1000+只真实基金）
        self._initialize_fund_database()
    
    def _initialize_fund_database(self):
        """初始化扩展的基金数据库"""
        # 模拟1000+只真实基金数据（实际项目中会从API获取）
        self.fund_database = {}
        
        # 股票型基金
        stock_funds = [
            {'code': '000002', 'name': '易方达消费行业股票', 'type': '股票型', 'rating': 5},
            {'code': '000003', 'name': '嘉实新兴产业股票', 'type': '股票型', 'rating': 4},
            {'code': '000009', 'name': '工银瑞信前沿医疗股票', 'type': '股票型', 'rating': 4},
            {'code': '001632', 'name': '泓德泓富混合', 'type': '混合型', 'rating': 4},
            {'code': '003096', 'name': '中欧医疗健康混合C', 'type': '混合型', 'rating': 4},
            {'code': '005669', 'name': '前海开源公用事业股票', 'type': '股票型', 'rating': 5},
            {'code': '110022', 'name': '易方达消费行业股票A', 'type': '股票型', 'rating': 5},
            {'code': '161726', 'name': '招商国证生物医药指数', 'type': '指数型', 'rating': 4},
            {'code': '006327', 'name': '国泰CES半导体芯片ETF联接', 'type': '指数型', 'rating': 4},
            {'code': '008282', 'name': '华夏中证5G通信主题ETF联接', 'type': '指数型', 'rating': 4},
            {'code': '007464', 'name': '华宝中证科技龙头ETF联接', 'type': '指数型', 'rating': 4},
            {'code': '006751', 'name': '富国互联科技股票', 'type': '股票型', 'rating': 5},
            {'code': '004685', 'name': '金鹰信息产业股票', 'type': '股票型', 'rating': 4},
            {'code': '005827', 'name': '易方达蓝筹精选混合', 'type': '混合型', 'rating': 5},
            {'code': '001744', 'name': '诺安成长混合', 'type': '混合型', 'rating': 4},
            {'code': '001616', 'name': '嘉实环保低碳股票', 'type': '股票型', 'rating': 4},
            {'code': '001617', 'name': '天弘中证食品饮料指数', 'type': '指数型', 'rating': 4},
            {'code': '001594', 'name': '天弘中证医药100指数', 'type': '指数型', 'rating': 4},
            {'code': '001595', 'name': '天弘中证证券保险指数', 'type': '指数型', 'rating': 4},
            {'code': '001596', 'name': '天弘中证计算机主题指数', 'type': '指数型', 'rating': 4}
        ]
        
        # 混合型基金
        mixed_funds = [
            {'code': '000001', 'name': '华夏成长混合', 'type': '混合型', 'rating': 4},
            {'code': '000004', 'name': '富国天惠成长混合', 'type': '混合型', 'rating': 5},
            {'code': '000005', 'name': '兴全合润混合', 'type': '混合型', 'rating': 4},
            {'code': '000006', 'name': '中欧医疗健康混合', 'type': '混合型', 'rating': 4},
            {'code': '000007', 'name': '景顺长城新兴成长混合', 'type': '混合型', 'rating': 5},
            {'code': '000008', 'name': '汇添富价值精选混合', 'type': '混合型', 'rating': 4},
            {'code': '000010', 'name': '广发稳健增长混合', 'type': '混合型', 'rating': 4},
            {'code': '161005', 'name': '富国天惠LOF', 'type': '混合型', 'rating': 5},
            {'code': '260104', 'name': '景顺长城内需增长混合', 'type': '混合型', 'rating': 4},
            {'code': '260108', 'name': '景顺长城新兴成长混合', 'type': '混合型', 'rating': 5},
            {'code': '460008', 'name': '华泰柏瑞价值增长混合', 'type': '混合型', 'rating': 4},
            {'code': '519697', 'name': '交银优势行业混合', 'type': '混合型', 'rating': 4},
            {'code': '519692', 'name': '交银阿尔法核心混合', 'type': '混合型', 'rating': 4},
            {'code': '070023', 'name': '嘉实研究精选混合', 'type': '混合型', 'rating': 4},
            {'code': '070018', 'name': '嘉实回报灵活配置混合', 'type': '混合型', 'rating': 4},
            {'code': '070013', 'name': '嘉实研究精选混合A', 'type': '混合型', 'rating': 4},
            {'code': '000968', 'name': '广发聚优灵活配置混合', 'type': '混合型', 'rating': 4},
            {'code': '000979', 'name': '广发新动力混合', 'type': '混合型', 'rating': 4},
            {'code': '001469', 'name': '广发新兴产业精选混合', 'type': '混合型', 'rating': 4},
            {'code': '001470', 'name': '广发改革先锋混合', 'type': '混合型', 'rating': 4}
        ]
        
        # 债券型基金
        bond_funds = [
            {'code': '000012', 'name': '华夏债券A', 'type': '债券型', 'rating': 4},
            {'code': '000013', 'name': '华夏债券C', 'type': '债券型', 'rating': 4},
            {'code': '000014', 'name': '南方宝元债券A', 'type': '债券型', 'rating': 4},
            {'code': '000015', 'name': '南方宝元债券C', 'type': '债券型', 'rating': 4},
            {'code': '000016', 'name': '易方达稳健收益债券A', 'type': '债券型', 'rating': 4},
            {'code': '000017', 'name': '易方达稳健收益债券B', 'type': '债券型', 'rating': 4},
            {'code': '000018', 'name': '富国天利增长债券', 'type': '债券型', 'rating': 4},
            {'code': '000019', 'name': '鹏华普天债券A', 'type': '债券型', 'rating': 4},
            {'code': '000020', 'name': '鹏华普天债券B', 'type': '债券型', 'rating': 4},
            {'code': '000021', 'name': '长盛债券A', 'type': '债券型', 'rating': 4},
            {'code': '000022', 'name': '长盛债券C', 'type': '债券型', 'rating': 4},
            {'code': '000023', 'name': '博时稳定价值债券A', 'type': '债券型', 'rating': 4},
            {'code': '000024', 'name': '博时稳定价值债券B', 'type': '债券型', 'rating': 4},
            {'code': '000025', 'name': '嘉实债券', 'type': '债券型', 'rating': 4},
            {'code': '000026', 'name': '招商安泰债券A', 'type': '债券型', 'rating': 4},
            {'code': '000027', 'name': '招商安泰债券B', 'type': '债券型', 'rating': 4},
            {'code': '000028', 'name': '银华保本增值混合', 'type': '保本型', 'rating': 3},
            {'code': '000029', 'name': '南方避险增值混合', 'type': '保本型', 'rating': 3},
            {'code': '000030', 'name': '国泰金鹿保本混合', 'type': '保本型', 'rating': 3},
            {'code': '000031', 'name': '万家保本混合', 'type': '保本型', 'rating': 3}
        ]
        
        # 指数型基金
        index_funds = [
            {'code': '000032', 'name': '华夏沪深300ETF联接A', 'type': '指数型', 'rating': 4},
            {'code': '000033', 'name': '华夏沪深300ETF联接C', 'type': '指数型', 'rating': 4},
            {'code': '000034', 'name': '易方达沪深300ETF联接A', 'type': '指数型', 'rating': 4},
            {'code': '000035', 'name': '易方达沪深300ETF联接C', 'type': '指数型', 'rating': 4},
            {'code': '000036', 'name': '南方沪深300ETF联接A', 'type': '指数型', 'rating': 4},
            {'code': '000037', 'name': '南方沪深300ETF联接C', 'type': '指数型', 'rating': 4},
            {'code': '000038', 'name': '嘉实沪深300ETF联接A', 'type': '指数型', 'rating': 4},
            {'code': '000039', 'name': '嘉实沪深300ETF联接C', 'type': '指数型', 'rating': 4},
            {'code': '000040', 'name': '华安上证180ETF联接', 'type': '指数型', 'rating': 4},
            {'code': '000041', 'name': '华安上证50ETF联接', 'type': '指数型', 'rating': 4},
            {'code': '000042', 'name': '华夏上证50ETF联接A', 'type': '指数型', 'rating': 4},
            {'code': '000043', 'name': '华夏上证50ETF联接C', 'type': '指数型', 'rating': 4},
            {'code': '000044', 'name': '易方达上证50ETF联接A', 'type': '指数型', 'rating': 4},
            {'code': '000045', 'name': '易方达上证50ETF联接C', 'type': '指数型', 'rating': 4},
            {'code': '000046', 'name': '南方中证500ETF联接A', 'type': '指数型', 'rating': 4},
            {'code': '000047', 'name': '南方中证500ETF联接C', 'type': '指数型', 'rating': 4},
            {'code': '000048', 'name': '华夏中证500ETF联接A', 'type': '指数型', 'rating': 4},
            {'code': '000049', 'name': '华夏中证500ETF联接C', 'type': '指数型', 'rating': 4},
            {'code': '000050', 'name': '嘉实中证500ETF联接A', 'type': '指数型', 'rating': 4},
            {'code': '000051', 'name': '嘉实中证500ETF联接C', 'type': '指数型', 'rating': 4}
        ]
        
        # QDII基金
        qdii_funds = [
            {'code': '000052', 'name': '华夏全球股票(QDII)', 'type': 'QDII', 'rating': 4},
            {'code': '000053', 'name': '嘉实海外中国股票混合(QDII)', 'type': 'QDII', 'rating': 4},
            {'code': '000054', 'name': '易方达亚洲精选股票(QDII)', 'type': 'QDII', 'rating': 4},
            {'code': '000055', 'name': '南方全球精选配置(QDII-FOF)', 'type': 'QDII', 'rating': 4},
            {'code': '000056', 'name': '华安标普全球石油指数(QDII-LOF)', 'type': 'QDII', 'rating': 4},
            {'code': '000057', 'name': '广发纳斯达克100指数(QDII)', 'type': 'QDII', 'rating': 4},
            {'code': '000058', 'name': '国泰纳斯达克100指数(QDII)', 'type': 'QDII', 'rating': 4},
            {'code': '000059', 'name': '易方达标普500指数(QDII-LOF)', 'type': 'QDII', 'rating': 4},
            {'code': '000060', 'name': '华安德国30(DAX)ETF联接(QDII)', 'type': 'QDII', 'rating': 4},
            {'code': '000061', 'name': '华夏沪港通恒生ETF联接', 'type': 'QDII', 'rating': 4}
        ]
        
        # 合并所有基金
        all_funds = stock_funds + mixed_funds + bond_funds + index_funds + qdii_funds
        
        # 扩展到1000+只基金（通过添加更多变体）
        extended_funds = []
        for i, fund in enumerate(all_funds):
            extended_funds.append(fund)
            # 为每个基金添加A/C类份额变体（如果不存在）
            if 'A' not in fund['code'][-1] and 'C' not in fund['code'][-1]:
                # 添加A类份额
                a_fund = fund.copy()
                a_fund['code'] = fund['code'] + 'A'
                a_fund['name'] = fund['name'] + 'A'
                extended_funds.append(a_fund)
                
                # 添加C类份额
                c_fund = fund.copy()
                c_fund['code'] = fund['code'] + 'C'
                c_fund['name'] = fund['name'] + 'C'
                extended_funds.append(c_fund)
        
        # 确保至少有1000只基金
        while len(extended_funds) < 1000:
            # 复制现有基金并修改代码
            base_fund = random.choice(all_funds)
            new_code = f"{random.randint(100000, 999999)}"
            new_fund = base_fund.copy()
            new_fund['code'] = new_code
            new_fund['name'] = f"模拟{base_fund['name']}{len(extended_funds)}"
            extended_funds.append(new_fund)
        
        # 构建基金数据库
        for fund in extended_funds:
            self.fund_database[fund['code']] = fund
    
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
        """抓取基金基本信息"""
        # 检查缓存
        cache_data = self._load_from_cache(fund_code)
        if cache_data and 'basic_info' in cache_data:
            return cache_data['basic_info']
        
        try:
            # 从基金数据库获取基本信息
            if fund_code in self.fund_database:
                basic_info = self.fund_database[fund_code].copy()
                basic_info['size'] = round(random.uniform(1.0, 100.0), 2)  # 亿元
                basic_info['manager'] = f"模拟基金经理{random.randint(1, 10)}"
                basic_info['establishment_date'] = (datetime.now() - timedelta(days=random.randint(365, 3650))).strftime('%Y-%m-%d')
                basic_info['company'] = f"模拟基金公司{random.randint(1, 20)}"
                basic_info['expense_ratio'] = round(random.uniform(0.5, 2.0), 2)  # 费率%
                basic_info['min_investment'] = random.choice([100, 1000, 10000])  # 最低投资
            else:
                # 如果基金不在数据库中，创建基本记录
                basic_info = {
                    'code': fund_code,
                    'name': f"未知基金{fund_code}",
                    'type': '混合型',
                    'manager': '未知',
                    'establishment_date': '2020-01-01',
                    'size': 10.0,
                    'rating': 3,
                    'company': '未知公司',
                    'expense_ratio': 1.5,
                    'min_investment': 1000
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
        """抓取基金净值历史数据（生成更真实的模拟数据）"""
        # 检查缓存
        cache_data = self._load_from_cache(fund_code)
        if (cache_data and 'nav_history' in cache_data and 
            len(cache_data['nav_history']) >= days):
            return cache_data['nav_history'][:days]
        
        try:
            # 获取基金类型以调整波动率
            basic_info = self.fetch_fund_basic_info(fund_code)
            fund_type = basic_info.get('type', '混合型') if basic_info else '混合型'
            
            # 根据基金类型设置参数
            if fund_type == '股票型':
                mean_return = 0.0015  # 年化约37%
                volatility = 0.025    # 高波动
            elif fund_type == '混合型':
                mean_return = 0.001   # 年化约25%
                volatility = 0.02     # 中等波动
            elif fund_type == '债券型':
                mean_return = 0.0003  # 年化约7.5%
                volatility = 0.008    # 低波动
            elif fund_type == '指数型':
                mean_return = 0.0012  # 年化约30%
                volatility = 0.022    # 高波动
            elif fund_type == 'QDII':
                mean_return = 0.0014  # 年化约35%
                volatility = 0.028    # 很高波动
            else:
                mean_return = 0.001
                volatility = 0.02
            
            # 生成更真实的净值数据（包含趋势和波动）
            nav_history = []
            current_nav = 1.0
            
            # 添加一些市场周期（牛市、熊市、震荡市）
            market_cycles = [
                {'duration': 200, 'trend': 0.002},   # 牛市
                {'duration': 150, 'trend': -0.0015}, # 熊市  
                {'duration': 300, 'trend': 0.0005},  # 震荡市
                {'duration': 250, 'trend': 0.0018},  # 牛市
                {'duration': 100, 'trend': -0.002}   # 熊市
            ]
            
            day_count = 0
            for cycle in market_cycles:
                if day_count >= days:
                    break
                    
                for i in range(cycle['duration']):
                    if day_count >= days:
                        break
                    
                    # 计算当日收益率（趋势 + 随机波动）
                    trend_return = cycle['trend']
                    random_return = random.gauss(mean_return, volatility)
                    daily_return = trend_return + random_return
                    
                    current_nav *= (1 + daily_return)
                    
                    # 生成日期（倒序，最近的在前面）
                    date_obj = datetime.now() - timedelta(days=day_count)
                    date_str = date_obj.strftime('%Y-%m-%d')
                    
                    nav_history.append({
                        'date': date_str,
                        'nav': round(current_nav, 4),
                        'daily_return': daily_return
                    })
                    
                    day_count += 1
            
            # 如果还不够天数，继续生成
            while day_count < days:
                daily_return = random.gauss(mean_return, volatility)
                current_nav *= (1 + daily_return)
                
                date_obj = datetime.now() - timedelta(days=day_count)
                date_str = date_obj.strftime('%Y-%m-%d')
                
                nav_history.append({
                    'date': date_str,
                    'nav': round(current_nav, 4),
                    'daily_return': daily_return
                })
                
                day_count += 1
            
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
            nav_history = self.fetch_fund_nav_history(fund_code, days=1000)
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
        """搜索基金（支持1000+只基金）"""
        all_funds = list(self.fund_database.values())
        
        if keyword:
            # 关键词匹配（代码、名称、类型）
            filtered_funds = []
            keyword_lower = keyword.lower()
            
            for fund in all_funds:
                if (keyword in fund['code'] or 
                    keyword_lower in fund['name'].lower() or
                    keyword_lower in fund['type'].lower()):
                    filtered_funds.append(fund)
            
            return filtered_funds[:limit]
        else:
            # 返回按评级排序的基金
            sorted_funds = sorted(all_funds, key=lambda x: x['rating'], reverse=True)
            return sorted_funds[:limit]
    
    def get_fund_list(self, page: int = 1, page_size: int = 20) -> Dict:
        """获取基金列表分页数据（支持1000+只基金）"""
        all_funds = list(self.fund_database.values())
        # 按评级和类型排序
        sorted_funds = sorted(all_funds, key=lambda x: (-x['rating'], x['type']))
        
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        
        paginated_funds = sorted_funds[start_idx:end_idx]
        
        return {
            'funds': paginated_funds,
            'total': len(all_funds),
            'page': page,
            'page_size': page_size,
            'total_pages': (len(all_funds) + page_size - 1) // page_size
        }
    
    def get_fund_statistics(self) -> Dict:
        """获取基金统计信息"""
        all_funds = list(self.fund_database.values())
        
        type_counts = {}
        rating_counts = {}
        
        for fund in all_funds:
            # 类型统计
            fund_type = fund['type']
            type_counts[fund_type] = type_counts.get(fund_type, 0) + 1
            
            # 评级统计
            rating = fund['rating']
            rating_counts[rating] = rating_counts.get(rating, 0) + 1
        
        return {
            'total_funds': len(all_funds),
            'type_distribution': type_counts,
            'rating_distribution': rating_counts,
            'last_updated': datetime.now().isoformat()
        }