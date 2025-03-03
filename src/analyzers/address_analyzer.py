#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
地址分析器模块 - 分析以太坊地址的交易行为和模式
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import pandas as pd
from clickhouse_driver import Client

logger = logging.getLogger(__name__)

class AddressAnalyzer:
    """以太坊地址分析器 - 提供全面的地址分析功能"""

    def __init__(self, clickhouse_config: Dict[str, Any]):
        """初始化分析器

        Args:
            clickhouse_config: ClickHouse数据库配置
        """
        self.clickhouse_client = Client(
            host=clickhouse_config.get('host'),
            port=clickhouse_config.get('port'),
            user=clickhouse_config.get('user'),
            password=clickhouse_config.get('password'),
            database=clickhouse_config.get('database')
        )

    def close(self):
        """关闭数据库连接"""
        if self.clickhouse_client:
            self.clickhouse_client = None

    def get_top_addresses_by_value(self, 
                                 limit: int = 10, 
                                 time_range: Optional[timedelta] = None) -> List[Dict[str, Any]]:
        """获取按净值流入排序的顶级地址

        Args:
            limit: 返回的地址数量
            time_range: 可选的时间范围过滤器

        Returns:
            地址列表，包含地址和相关统计信息
        """
        time_filter = ""
        params = {'limit': limit}
        
        if time_range:
            time_filter = """
            AND transaction_timestamp >= %(start_time)s
            """
            params['start_time'] = datetime.now() - time_range

        query = f"""
        WITH (
            SELECT address, sum(value) as received
            FROM transactions
            WHERE to_address = address
            {time_filter}
            GROUP BY address
        ) as inflow,
        (
            SELECT from_address as address, sum(value) as sent
            FROM transactions
            WHERE from_address = address
            {time_filter}
            GROUP BY address
        ) as outflow
        SELECT 
            COALESCE(inflow.address, outflow.address) as address,
            COALESCE(inflow.received, 0) - COALESCE(outflow.sent, 0) as net_value,
            COALESCE(inflow.received, 0) as total_received,
            COALESCE(outflow.sent, 0) as total_sent
        FROM inflow
        FULL OUTER JOIN outflow ON inflow.address = outflow.address
        ORDER BY net_value DESC
        LIMIT %(limit)s
        """
        
        results = self.clickhouse_client.execute(query, params)
        
        return [
            {
                'address': row[0],
                'net_value': float(row[1]),
                'total_received': float(row[2]),
                'total_sent': float(row[3])
            }
            for row in results
        ]

    def get_address_activity_pattern(self, 
                                   address: str, 
                                   time_window: timedelta = timedelta(days=30)
                                   ) -> Dict[str, Any]:
        """分析地址的活动模式

        Args:
            address: 要分析的地址
            time_window: 分析的时间窗口

        Returns:
            地址活动模式分析结果
        """
        start_time = datetime.now() - time_window
        
        query = """
        SELECT
            toStartOfHour(transaction_timestamp) as hour,
            count() as tx_count,
            sum(case when from_address = %(address)s then 1 else 0 end) as out_tx_count,
            sum(case when to_address = %(address)s then 1 else 0 end) as in_tx_count,
            sum(case when from_address = %(address)s then value else 0 end) as out_value,
            sum(case when to_address = %(address)s then value else 0 end) as in_value
        FROM transactions
        WHERE (from_address = %(address)s OR to_address = %(address)s)
            AND transaction_timestamp >= %(start_time)s
        GROUP BY hour
        ORDER BY hour
        """
        
        results = self.clickhouse_client.execute(
            query,
            {
                'address': address,
                'start_time': start_time
            }
        )
        
        # 转换为pandas DataFrame进行时间序列分析
        df = pd.DataFrame(results, columns=[
            'hour', 'tx_count', 'out_tx_count', 'in_tx_count',
            'out_value', 'in_value'
        ])
        
        # 计算基本统计信息
        stats = {
            'total_transactions': int(df['tx_count'].sum()),
            'avg_daily_transactions': float(df['tx_count'].mean() * 24),
            'total_outgoing': float(df['out_value'].sum()),
            'total_incoming': float(df['in_value'].sum()),
            'net_flow': float(df['in_value'].sum() - df['out_value'].sum()),
            'active_hours': len(df[df['tx_count'] > 0]),
            'most_active_hour': df.loc[df['tx_count'].idxmax(), 'hour'].strftime('%Y-%m-%d %H:00:00'),
            'max_hourly_transactions': int(df['tx_count'].max())
        }
        
        return stats

    def find_similar_addresses(self, 
                             address: str, 
                             min_similarity: float = 0.7,
                             limit: int = 10) -> List[Dict[str, Any]]:
        """查找具有相似交易模式的地址

        Args:
            address: 目标地址
            min_similarity: 最小相似度阈值
            limit: 返回结果数量

        Returns:
            相似地址列表
        """
        # 获取目标地址的交易模式
        target_pattern = self.get_address_activity_pattern(address)
        
        # 查找交易量相近的地址
        query = """
        WITH (
            SELECT count() as tx_count
            FROM transactions
            WHERE from_address = %(address)s OR to_address = %(address)s
        ) as target_count
        
        SELECT 
            address,
            tx_count,
            abs(tx_count - target_count) / target_count as difference
        FROM (
            SELECT
                address,
                count() as tx_count
            FROM (
                SELECT from_address as address
                FROM transactions
                WHERE from_address != %(address)s
                UNION ALL
                SELECT to_address as address
                FROM transactions
                WHERE to_address != %(address)s
            )
            GROUP BY address
            HAVING tx_count >= target_count * 0.5
                AND tx_count <= target_count * 1.5
        )
        ORDER BY difference ASC
        LIMIT %(limit)s
        """
        
        results = self.clickhouse_client.execute(
            query,
            {
                'address': address,
                'limit': limit * 2  # 获取更多候选地址进行详细比较
            }
        )
        
        similar_addresses = []
        for row in results:
            candidate_address = row[0]
            candidate_pattern = self.get_address_activity_pattern(candidate_address)
            
            # 计算相似度
            similarity = self._calculate_pattern_similarity(target_pattern, candidate_pattern)
            
            if similarity >= min_similarity:
                similar_addresses.append({
                    'address': candidate_address,
                    'similarity': similarity,
                    'pattern': candidate_pattern
                })
        
        # 按相似度排序并限制返回数量
        similar_addresses.sort(key=lambda x: x['similarity'], reverse=True)
        return similar_addresses[:limit]

    def _calculate_pattern_similarity(self, 
                                   pattern1: Dict[str, Any], 
                                   pattern2: Dict[str, Any]) -> float:
        """计算两个地址模式的相似度

        Args:
            pattern1: 第一个地址的模式
            pattern2: 第二个地址的模式

        Returns:
            相似度分数 (0-1)
        """
        # 计算交易量相似度
        tx_similarity = 1 - abs(pattern1['avg_daily_transactions'] - pattern2['avg_daily_transactions']) / \
                           max(pattern1['avg_daily_transactions'], pattern2['avg_daily_transactions'])
        
        # 计算活跃时间相似度
        time_similarity = 1 - abs(pattern1['active_hours'] - pattern2['active_hours']) / \
                             max(pattern1['active_hours'], pattern2['active_hours'])
        
        # 计算交易金额模式相似度
        value_similarity = 1 - abs(pattern1['net_flow'] - pattern2['net_flow']) / \
                             max(abs(pattern1['net_flow']), abs(pattern2['net_flow']))
        
        # 综合评分
        return (tx_similarity * 0.4 + time_similarity * 0.3 + value_similarity * 0.3) 