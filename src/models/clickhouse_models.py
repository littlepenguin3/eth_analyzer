#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ClickHouse数据模型 - 存储区块链原始数据
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from decimal import Decimal

@dataclass
class Block:
    """区块数据模型"""
    number: int
    hash: str
    parent_hash: str
    nonce: str
    sha3_uncles: str
    logs_bloom: str
    transactions_root: str
    state_root: str
    receipts_root: str
    miner: str
    difficulty: int
    total_difficulty: int
    size: int
    extra_data: str
    gas_limit: int
    gas_used: int
    timestamp: datetime
    transaction_count: int
    base_fee_per_gas: Optional[int] = None
    withdrawals_root: Optional[str] = None
    withdrawals: List[str] = None

    @classmethod
    def create_table_sql(cls) -> str:
        return """
        CREATE TABLE IF NOT EXISTS blocks (
            number UInt64,
            hash String,
            parent_hash String,
            nonce String,
            sha3_uncles String,
            logs_bloom String,
            transactions_root String,
            state_root String,
            receipts_root String,
            miner String,
            difficulty UInt256,
            total_difficulty UInt256,
            size UInt64,
            extra_data String,
            gas_limit UInt64,
            gas_used UInt64,
            timestamp DateTime,
            transaction_count UInt32,
            base_fee_per_gas Nullable(UInt64),
            withdrawals_root Nullable(String),
            withdrawals Array(String)
        ) ENGINE = MergeTree()
        ORDER BY (number)
        """

@dataclass
class Transaction:
    """交易数据模型"""
    hash: str
    block_number: int
    from_address: str
    to_address: Optional[str]
    value: Decimal
    gas: int
    gas_price: int
    input: str
    nonce: int
    transaction_index: int
    type: int
    max_fee_per_gas: Optional[int] = None
    max_priority_fee_per_gas: Optional[int] = None
    transaction_timestamp: datetime = None

    @classmethod
    def create_table_sql(cls) -> str:
        return """
        CREATE TABLE IF NOT EXISTS transactions (
            hash String,
            block_number UInt64,
            from_address String,
            to_address Nullable(String),
            value Decimal128(0),
            gas UInt64,
            gas_price UInt64,
            input String,
            nonce UInt64,
            transaction_index UInt32,
            type UInt8,
            max_fee_per_gas Nullable(UInt64),
            max_priority_fee_per_gas Nullable(UInt64),
            transaction_timestamp DateTime
        ) ENGINE = MergeTree()
        ORDER BY (block_number, transaction_index)
        """

@dataclass
class AddressStats:
    """地址统计数据模型"""
    address: str
    total_transactions: int
    total_received: Decimal
    total_sent: Decimal
    first_seen: datetime
    last_seen: datetime
    is_contract: bool

    @classmethod
    def create_table_sql(cls) -> str:
        return """
        CREATE TABLE IF NOT EXISTS address_stats (
            address String,
            total_transactions UInt64,
            total_received Decimal128(0),
            total_sent Decimal128(0),
            first_seen DateTime,
            last_seen DateTime,
            is_contract Boolean
        ) ENGINE = MergeTree()
        ORDER BY (address)
        """ 