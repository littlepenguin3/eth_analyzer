# 以太坊区块链分析器

这个项目是一个专门用于分析以太坊区块链数据的工具集。它基于从区块链导入器获取的数据，提供各种分析功能，包括地址分析、交易模式识别等。

## 数据模式

### 区块数据 (blocks)
```sql
CREATE TABLE blocks (
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
ORDER BY (number);
```

### 交易数据 (transactions)
```sql
CREATE TABLE transactions (
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
ORDER BY (block_number, transaction_index);
```

### 地址统计数据 (address_stats)
```sql
CREATE TABLE address_stats (
    address String,
    total_transactions UInt64,
    total_received Decimal128(0),
    total_sent Decimal128(0),
    first_seen DateTime,
    last_seen DateTime,
    is_contract Boolean
) ENGINE = MergeTree()
ORDER BY (address);
```

## 项目结构

```
eth_analyzer/
├── src/
│   ├── analyzers/
│   │   ├── __init__.py
│   │   ├── address_analyzer.py
│   │   ├── transaction_analyzer.py
│   │   └── pattern_analyzer.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── data_models.py
│   ├── utils/
│   │   ├── __init__.py
│   │   └── helpers.py
│   └── config/
│       ├── __init__.py
│       └── settings.py
├── tests/
│   └── __init__.py
├── notebooks/
│   └── analysis_examples.ipynb
├── requirements.txt
├── setup.py
└── README.md
```

## 配置说明

项目配置需要在 `config.yaml` 中设置以下参数：

```yaml
clickhouse:
  host: localhost
  port: 9000
  user: default
  password: 
  database: ethereum

analysis:
  cache_enabled: true
  cache_ttl: 3600
  batch_size: 1000
```

## 使用方法

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 运行分析：
```python
from eth_analyzer.analyzers import AddressAnalyzer

analyzer = AddressAnalyzer()
top_addresses = analyzer.get_top_addresses_by_value()
```

## AI 提示

以下是用于与AI工具交互的提示模板：

```
你是一个以太坊区块链数据分析助手。你可以访问以下数据表：

1. blocks表：包含区块基本信息
   - 主要字段：number(区块号)、timestamp(时间戳)、miner(矿工地址)
   - 用途：分析区块链基本指标和挖矿模式

2. transactions表：包含所有交易信息
   - 主要字段：hash(交易哈希)、from_address(发送方)、to_address(接收方)、value(交易值)
   - 用途：分析交易流向、金额分布等

3. address_stats表：地址统计信息
   - 主要字段：address(地址)、total_transactions(总交易数)、total_received/sent(总收发额)
   - 用途：分析地址行为特征

请基于这些数据结构，帮助用户进行以太坊数据分析。
``` 