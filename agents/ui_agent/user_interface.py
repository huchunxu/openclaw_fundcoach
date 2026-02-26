"""
用户交互界面模块

功能：
- 自动模式/手动模式切换
- 基金代码输入处理
- 用户偏好设置
- 交互式参数配置
"""

import pandas as pd
from typing import Dict, List, Optional, Tuple


class UserInterface:
    """用户交互界面"""
    
    def __init__(self):
        self.mode = 'auto'  # 'auto' or 'manual'
        self.user_preferences = {
            'risk_tolerance': 'medium',  # 'low', 'medium', 'high'
            'investment_horizon': 3,    # years
            'max_drawdown_limit': -0.25,
            'preferred_sectors': [],
            'excluded_funds': []
        }
        self.fund_pool = []
        
    def switch_mode(self, mode: str) -> bool:
        """
        切换工作模式
        
        Args:
            mode: 'auto' 或 'manual'
            
        Returns:
            切换是否成功
        """
        if mode in ['auto', 'manual']:
            self.mode = mode
            return True
        return False
    
    def process_fund_input(self, fund_codes: List[str]) -> List[str]:
        """
        处理用户输入的基金代码
        
        Args:
            fund_codes: 基金代码列表
            
        Returns:
            验证后的基金代码列表
        """
        validated_codes = []
        
        for code in fund_codes:
            # 基本验证：6位数字
            if isinstance(code, str) and len(code) == 6 and code.isdigit():
                # 检查是否在排除列表中
                if code not in self.user_preferences['excluded_funds']:
                    validated_codes.append(code)
                    
        return validated_codes
    
    def set_user_preferences(self, preferences: Dict) -> None:
        """
        设置用户偏好
        
        Args:
            preferences: 用户偏好字典
        """
        valid_keys = ['risk_tolerance', 'investment_horizon', 'max_drawdown_limit', 
                     'preferred_sectors', 'excluded_funds']
        
        for key, value in preferences.items():
            if key in valid_keys:
                self.user_preferences[key] = value
    
    def get_auto_mode_config(self) -> Dict:
        """
        获取自动模式配置
        
        Returns:
            自动模式配置字典
        """
        config = {
            'mode': 'auto',
            'risk_tolerance': self.user_preferences['risk_tolerance'],
            'investment_horizon': self.user_preferences['investment_horizon'],
            'max_drawdown_limit': self.user_preferences['max_drawdown_limit'],
            'preferred_sectors': self.user_preferences['preferred_sectors'],
            'excluded_funds': self.user_preferences['excluded_funds']
        }
        return config
    
    def get_manual_mode_config(self, fund_codes: List[str]) -> Dict:
        """
        获取手动模式配置
        
        Args:
            fund_codes: 用户指定的基金代码列表
            
        Returns:
            手动模式配置字典
        """
        validated_codes = self.process_fund_input(fund_codes)
        
        config = {
            'mode': 'manual',
            'fund_codes': validated_codes,
            'max_drawdown_limit': self.user_preferences['max_drawdown_limit']
        }
        return config
    
    def validate_user_input(self, input_data: Dict) -> Tuple[bool, str]:
        """
        验证用户输入
        
        Args:
            input_data: 用户输入数据
            
        Returns:
            (是否有效, 错误信息)
        """
        mode = input_data.get('mode', 'auto')
        
        if mode == 'manual':
            fund_codes = input_data.get('fund_codes', [])
            if not fund_codes:
                return False, "手动模式需要至少一个基金代码"
                
            validated_codes = self.process_fund_input(fund_codes)
            if not validated_codes:
                return False, "提供的基金代码无效"
                
        elif mode == 'auto':
            # 自动模式基本验证
            risk_tolerance = input_data.get('risk_tolerance', 'medium')
            if risk_tolerance not in ['low', 'medium', 'high']:
                return False, "风险偏好必须是 low, medium, 或 high"
                
        else:
            return False, "模式必须是 auto 或 manual"
            
        return True, ""
    
    def get_interaction_flow(self, user_input: Dict) -> Dict:
        """
        获取交互流程配置
        
        Args:
            user_input: 用户输入
            
        Returns:
            完整的交互流程配置
        """
        is_valid, error_msg = self.validate_user_input(user_input)
        
        if not is_valid:
            return {'error': error_msg, 'valid': False}
            
        mode = user_input.get('mode', 'auto')
        
        if mode == 'manual':
            config = self.get_manual_mode_config(user_input.get('fund_codes', []))
        else:
            # 更新用户偏好
            self.set_user_preferences(user_input)
            config = self.get_auto_mode_config()
            
        config['valid'] = True
        return config