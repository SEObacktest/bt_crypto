import os
import sys
import json
from typing import Dict, List

class BacktestConfig:
    """处理回测相关的配置"""
    def __init__(self, json_path: str = "db.json"):
        with open(json_path, 'r') as f:
            self.config = json.load(f)
    
    def get_pairs(self) -> List[str]:
        """获取所有配置的交易对"""
        return list(self.config['data']['pairs'].keys())
    def get_strategies(self)->List[str]:
        return list(self.config['strategy'].keys())
    
    def get_pair_config(self, pair: str) -> Dict:
        """获取指定交易对的配置"""
        return self.config['data']['pairs'][pair]
    
    def get_cerebro_config(self) -> Dict:
        """获取cerebro的基本配置"""
        return self.config['cerebro']
    
    def get_strategy_config(self, strategy: str) -> Dict:
        """获取指定策略的配置"""
        return self.config['strategy'][strategy]

def load_configs(json_path="db.json"):
    """一次性加载所有配置"""
    backtest = BacktestConfig(json_path)
    return backtest
