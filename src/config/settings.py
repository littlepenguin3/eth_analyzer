#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置模块 - 管理分析器的配置参数
"""

import os
import yaml
from typing import Dict, Any

class Settings:
    """配置管理类"""
    
    def __init__(self, config_path: str = None):
        """初始化配置

        Args:
            config_path: 配置文件路径，如果为None则使用默认路径
        """
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), '../../config.yaml')
            
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件

        Returns:
            配置字典
        """
        if not os.path.exists(self.config_path):
            return self._get_default_config()
            
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置

        Returns:
            默认配置字典
        """
        return {
            'clickhouse': {
                'host': 'localhost',
                'port': 9000,
                'user': 'default',
                'password': '',
                'database': 'ethereum'
            },
            'analysis': {
                'cache_enabled': True,
                'cache_ttl': 3600,  # 缓存过期时间（秒）
                'batch_size': 1000,  # 批处理大小
                'max_workers': 4     # 最大工作线程数
            },
            'logging': {
                'level': 'INFO',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            }
        }
    
    def get_clickhouse_config(self) -> Dict[str, Any]:
        """获取ClickHouse配置

        Returns:
            ClickHouse配置字典
        """
        return self.config.get('clickhouse', self._get_default_config()['clickhouse'])
    
    def get_analysis_config(self) -> Dict[str, Any]:
        """获取分析配置

        Returns:
            分析配置字典
        """
        return self.config.get('analysis', self._get_default_config()['analysis'])
    
    def get_logging_config(self) -> Dict[str, Any]:
        """获取日志配置

        Returns:
            日志配置字典
        """
        return self.config.get('logging', self._get_default_config()['logging']) 