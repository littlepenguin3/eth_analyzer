#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Neo4j数据模型 - 存储区块链关系数据
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict
from enum import Enum

class NodeLabel(Enum):
    """Neo4j节点标签"""
    BLOCK = "Block"
    TRANSACTION = "Transaction"
    ADDRESS = "Address"
    CONTRACT = "Contract"

class RelationType(Enum):
    """Neo4j关系类型"""
    MINED = "MINED"                 # Address -> Block
    INCLUDED_IN = "INCLUDED_IN"     # Transaction -> Block
    SENT = "SENT"                   # Address -> Transaction
    RECEIVED_BY = "RECEIVED_BY"     # Transaction -> Address
    TRANSFERS_TO = "TRANSFERS_TO"   # Address -> Address
    INTERACTS_WITH = "INTERACTS_WITH"  # Address -> Contract
    CREATED_CONTRACT = "CREATED_CONTRACT"  # Address -> Contract

@dataclass
class Neo4jNode:
    """Neo4j节点基类"""
    label: NodeLabel
    properties: Dict

    def to_cypher_create(self) -> str:
        """生成创建节点的Cypher语句"""
        props = ", ".join(f"{k}: ${k}" for k in self.properties.keys())
        return f"CREATE (n:{self.label.value} {{{props}}}) RETURN n"

@dataclass
class Neo4jRelationship:
    """Neo4j关系基类"""
    type: RelationType
    from_node: Neo4jNode
    to_node: Neo4jNode
    properties: Dict = None

    def to_cypher_create(self) -> str:
        """生成创建关系的Cypher语句"""
        props = ""
        if self.properties:
            props = " {" + ", ".join(f"{k}: ${k}" for k in self.properties.keys()) + "}"
        return f"""
        MATCH (from:{self.from_node.label.value} {{hash: $from_hash}})
        MATCH (to:{self.to_node.label.value} {{hash: $to_hash}})
        CREATE (from)-[r:{self.type.value}{props}]->(to)
        RETURN r
        """

@dataclass
class BlockNode(Neo4jNode):
    """区块节点"""
    def __init__(self, hash: str, number: int):
        super().__init__(
            label=NodeLabel.BLOCK,
            properties={
                "hash": hash,
                "number": number
            }
        )

@dataclass
class TransactionNode(Neo4jNode):
    """交易节点"""
    def __init__(self, hash: str):
        super().__init__(
            label=NodeLabel.TRANSACTION,
            properties={
                "hash": hash
            }
        )

@dataclass
class AddressNode(Neo4jNode):
    """地址节点"""
    def __init__(self, address: str, is_contract: bool = False):
        super().__init__(
            label=NodeLabel.ADDRESS if not is_contract else NodeLabel.CONTRACT,
            properties={
                "address": address,
                "is_contract": is_contract
            }
        )

class Neo4jSchema:
    """Neo4j数据库模式定义"""
    
    @staticmethod
    def get_constraints() -> List[str]:
        """获取所有约束的创建语句"""
        return [
            "CREATE CONSTRAINT address_unique IF NOT EXISTS FOR (a:Address) REQUIRE a.address IS UNIQUE",
            "CREATE CONSTRAINT tx_unique IF NOT EXISTS FOR (t:Transaction) REQUIRE t.hash IS UNIQUE",
            "CREATE CONSTRAINT block_unique IF NOT EXISTS FOR (b:Block) REQUIRE b.hash IS UNIQUE"
        ]
    
    @staticmethod
    def get_indexes() -> List[str]:
        """获取所有索引的创建语句"""
        return [
            "CREATE INDEX block_number_idx IF NOT EXISTS FOR (b:Block) ON (b.number)"
        ] 