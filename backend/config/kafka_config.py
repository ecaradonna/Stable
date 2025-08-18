"""
Kafka Configuration for StableYield Index Production Pipeline
Handles topic creation, producer/consumer configs, and data schemas
"""

import os
from typing import Dict, List
from dataclasses import dataclass
from enum import Enum

class KafkaTopics(Enum):
    """Kafka topic definitions with naming convention"""
    CC_PRICES = "cc.prices"
    CC_ORDERBOOK = "cc.orderbook"
    DL_APY = "dl.apy"
    EX_MKTCAP = "ex.mktcap"
    TRAD_TBILL = "trad.tbill"
    SYI_CALCULATED = "syi.calculated"
    RAY_CALCULATED = "ray.calculated"

@dataclass
class TopicConfig:
    """Kafka topic configuration"""
    name: str
    partitions: int
    replication_factor: int
    retention_ms: int
    cleanup_policy: str
    key_schema: str
    value_schema: str

# Topic configurations for production deployment
TOPIC_CONFIGS = {
    KafkaTopics.CC_PRICES: TopicConfig(
        name="cc.prices",
        partitions=12,
        replication_factor=3,
        retention_ms=7 * 24 * 60 * 60 * 1000,  # 7 days
        cleanup_policy="compact",
        key_schema="{symbol}-{venue}",
        value_schema="price_data_v1"
    ),
    
    KafkaTopics.CC_ORDERBOOK: TopicConfig(
        name="cc.orderbook",
        partitions=12,
        replication_factor=3,
        retention_ms=24 * 60 * 60 * 1000,  # 24 hours
        cleanup_policy="delete",
        key_schema="{symbol}-{venue}",
        value_schema="orderbook_snapshot_v1"
    ),
    
    KafkaTopics.DL_APY: TopicConfig(
        name="dl.apy",
        partitions=6,
        replication_factor=3,
        retention_ms=30 * 24 * 60 * 60 * 1000,  # 30 days
        cleanup_policy="compact",
        key_schema="{protocol}-{symbol}",
        value_schema="apy_data_v1"
    ),
    
    KafkaTopics.EX_MKTCAP: TopicConfig(
        name="ex.mktcap",
        partitions=3,
        replication_factor=3,
        retention_ms=30 * 24 * 60 * 60 * 1000,  # 30 days
        cleanup_policy="compact",
        key_schema="{symbol}",
        value_schema="market_cap_data_v1"
    ),
    
    KafkaTopics.TRAD_TBILL: TopicConfig(
        name="trad.tbill",
        partitions=1,
        replication_factor=3,
        retention_ms=365 * 24 * 60 * 60 * 1000,  # 365 days
        cleanup_policy="compact",
        key_schema="yield-{maturity}",
        value_schema="tbill_rate_v1"
    ),
    
    KafkaTopics.SYI_CALCULATED: TopicConfig(
        name="syi.calculated",
        partitions=1,
        replication_factor=3,
        retention_ms=365 * 24 * 60 * 60 * 1000,  # 365 days
        cleanup_policy="compact",
        key_schema="SYI-{timestamp}",
        value_schema="index_value_v1"
    ),
    
    KafkaTopics.RAY_CALCULATED: TopicConfig(
        name="ray.calculated",
        partitions=6,
        replication_factor=3,
        retention_ms=90 * 24 * 60 * 60 * 1000,  # 90 days
        cleanup_policy="compact",
        key_schema="{symbol}-{timestamp}",
        value_schema="ray_observation_v1"
    )
}

class KafkaConfig:
    """Kafka cluster configuration"""
    
    def __init__(self):
        self.bootstrap_servers = os.getenv(
            'KAFKA_BOOTSTRAP_SERVERS', 
            'localhost:9092'
        )
        self.security_protocol = os.getenv('KAFKA_SECURITY_PROTOCOL', 'PLAINTEXT')
        self.sasl_mechanism = os.getenv('KAFKA_SASL_MECHANISM', 'PLAIN')
        self.sasl_username = os.getenv('KAFKA_SASL_USERNAME', '')
        self.sasl_password = os.getenv('KAFKA_SASL_PASSWORD', '')
        
    def get_producer_config(self) -> Dict:
        """Get Kafka producer configuration"""
        config = {
            'bootstrap_servers': self.bootstrap_servers,
            'security_protocol': self.security_protocol,
            'acks': 'all',  # Wait for all replicas
            'retries': 2147483647,  # Max retries
            'max_in_flight_requests_per_connection': 5,
            'enable_idempotence': True,
            'compression_type': 'snappy',
            'batch_size': 16384,
            'linger_ms': 10,  # Small batching delay
            'buffer_memory': 33554432,
            'key_serializer': 'org.apache.kafka.common.serialization.StringSerializer',
            'value_serializer': 'org.apache.kafka.common.serialization.StringSerializer'
        }
        
        if self.security_protocol != 'PLAINTEXT':
            config.update({
                'sasl_mechanism': self.sasl_mechanism,
                'sasl_username': self.sasl_username,
                'sasl_password': self.sasl_password
            })
        
        return config
    
    def get_consumer_config(self, group_id: str) -> Dict:
        """Get Kafka consumer configuration"""
        config = {
            'bootstrap_servers': self.bootstrap_servers,
            'security_protocol': self.security_protocol,
            'group_id': group_id,
            'auto_offset_reset': 'earliest',
            'enable_auto_commit': False,  # Manual commit for exactly-once
            'max_poll_records': 500,
            'session_timeout_ms': 30000,
            'heartbeat_interval_ms': 3000,
            'key_deserializer': 'org.apache.kafka.common.serialization.StringDeserializer',
            'value_deserializer': 'org.apache.kafka.common.serialization.StringDeserializer'
        }
        
        if self.security_protocol != 'PLAINTEXT':
            config.update({
                'sasl_mechanism': self.sasl_mechanism,
                'sasl_username': self.sasl_username,
                'sasl_password': self.sasl_password
            })
        
        return config

# Data schemas for validation and serialization
SCHEMAS = {
    "price_data_v1": {
        "type": "object",
        "properties": {
            "timestamp": {"type": "string", "format": "date-time"},
            "symbol": {"type": "string"},
            "venue": {"type": "string"},
            "price": {"type": "number"},
            "volume_24h": {"type": "number"},
            "change_24h": {"type": "number"},
            "market_cap": {"type": "number"}
        },
        "required": ["timestamp", "symbol", "venue", "price"]
    },
    
    "orderbook_snapshot_v1": {
        "type": "object",
        "properties": {
            "timestamp": {"type": "string", "format": "date-time"},
            "symbol": {"type": "string"},
            "venue": {"type": "string"},
            "bids": {
                "type": "array",
                "items": {
                    "type": "array",
                    "items": {"type": "number"},
                    "minItems": 2,
                    "maxItems": 2
                }
            },
            "asks": {
                "type": "array",
                "items": {
                    "type": "array",
                    "items": {"type": "number"},
                    "minItems": 2,
                    "maxItems": 2
                }
            }
        },
        "required": ["timestamp", "symbol", "venue", "bids", "asks"]
    },
    
    "apy_data_v1": {
        "type": "object",
        "properties": {
            "timestamp": {"type": "string", "format": "date-time"},
            "protocol": {"type": "string"},
            "symbol": {"type": "string"},
            "apy": {"type": "number"},
            "tvl": {"type": "number"},
            "pool_address": {"type": "string"},
            "risk_score": {"type": "number"}
        },
        "required": ["timestamp", "protocol", "symbol", "apy"]
    },
    
    "market_cap_data_v1": {
        "type": "object",
        "properties": {
            "timestamp": {"type": "string", "format": "date-time"},
            "symbol": {"type": "string"},
            "market_cap": {"type": "number"},
            "circulating_supply": {"type": "number"},
            "total_supply": {"type": "number"},
            "price": {"type": "number"}
        },
        "required": ["timestamp", "symbol", "market_cap"]
    },
    
    "tbill_rate_v1": {
        "type": "object",
        "properties": {
            "timestamp": {"type": "string", "format": "date-time"},
            "maturity": {"type": "string"},
            "rate": {"type": "number"},
            "source": {"type": "string"}
        },
        "required": ["timestamp", "maturity", "rate"]
    },
    
    "index_value_v1": {
        "type": "object",
        "properties": {
            "timestamp": {"type": "string", "format": "date-time"},
            "index_id": {"type": "string"},
            "value": {"type": "number"},
            "methodology_version": {"type": "string"},
            "constituents": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "symbol": {"type": "string"},
                        "weight": {"type": "number"},
                        "ray": {"type": "number"}
                    }
                }
            }
        },
        "required": ["timestamp", "index_id", "value", "constituents"]
    },
    
    "ray_observation_v1": {
        "type": "object",
        "properties": {
            "timestamp": {"type": "string", "format": "date-time"},
            "symbol": {"type": "string"},
            "raw_apy": {"type": "number"},
            "peg_score": {"type": "number"},
            "liquidity_score": {"type": "number"},
            "counterparty_score": {"type": "number"},
            "ray": {"type": "number"}
        },
        "required": ["timestamp", "symbol", "raw_apy", "ray"]
    }
}

# TODO: PRODUCTION DEPLOYMENT CHECKLIST
# 1. Deploy Kafka cluster with proper resource allocation
# 2. Create topics with these configurations
# 3. Set up monitoring for topic lag and throughput
# 4. Configure schema registry for evolution support
# 5. Implement proper security (SASL/SSL)
# 6. Set up backup and disaster recovery