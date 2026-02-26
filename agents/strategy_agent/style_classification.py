"""
风格分类模块

功能：
- 基金类型分类（股票型、混合型、债券型等）
- 市值风格分类（大盘、中盘、小盘）
- 投资风格分类（价值、成长、平衡）
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional


class StyleClassification:
    """风格分类器"""
    
    def __init__(self):
        # 基金类型映射
        self.fund_type_mapping = {
            '股票型': 'equity',
            '混合型': 'balanced', 
            '债券型': 'bond',
            '货币型': 'money_market',
            '指数型': 'index',
            'QDII': 'qdii'
        }
        
        # 市值分类阈值（亿元）
        self.market_cap_thresholds = {
            'large_cap': 100,    # 大盘：>100亿
            'mid_cap': 10,       # 中盘：10-100亿  
            'small_cap': 0       # 小盘：<10亿
        }
        
    def classify_fund_type(self, fund_data: Dict) -> str:
        """
        分类基金类型
        """
        fund_type = fund_data.get('fund_type', '未知')
        return self.fund_type_mapping.get(fund_type, 'unknown')
    
    def classify_market_cap_style(self, fund_data: Dict) -> str:
        """
        分类市值风格
        """
        fund_size = fund_data.get('fund_size', 0)
        
        if fund_size >= self.market_cap_thresholds['large_cap']:
            return 'large_cap'
        elif fund_size >= self.market_cap_thresholds['mid_cap']:
            return 'mid_cap'
        else:
            return 'small_cap'
    
    def classify_investment_style(self, factors: Dict[str, float]) -> str:
        """
        分类投资风格（基于因子得分）
        """
        value_score = factors.get('value', 0)
        growth_score = factors.get('growth', 0)
        
        # 简化逻辑：比较价值和成长因子
        if abs(value_score - growth_score) < 0.2:
            return 'balanced'
        elif value_score > growth_score:
            return 'value'
        else:
            return 'growth'
    
    def classify_fund_comprehensive(self, fund_code: str, fund_data: Dict, 
                                  factors: Dict[str, float]) -> Dict:
        """
        综合风格分类
        """
        classification = {
            'fund_code': fund_code,
            'fund_type': self.classify_fund_type(fund_data),
            'market_cap_style': self.classify_market_cap_style(fund_data),
            'investment_style': self.classify_investment_style(factors)
        }
        
        return classification
    
    def classify_multiple_funds(self, fund_data_dict: Dict[str, Dict], 
                               factors_dict: Dict[str, Dict[str, float]]) -> pd.DataFrame:
        """
        对多只基金进行综合分类
        """
        classifications = []
        
        for fund_code in fund_data_dict.keys():
            if fund_code in factors_dict:
                classification = self.classify_fund_comprehensive(
                    fund_code, fund_data_dict[fund_code], factors_dict[fund_code]
                )
                classifications.append(classification)
        
        if not classifications:
            return pd.DataFrame()
            
        return pd.DataFrame(classifications)