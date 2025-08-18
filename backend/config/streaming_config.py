"""
Streaming Configuration for StableYield Index Production Pipeline
Defines Flink/Spark streaming jobs for real-time data processing
"""

import os
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class StreamingEngine(Enum):
    """Supported streaming engines"""
    FLINK = "flink"
    SPARK = "spark"

@dataclass
class StreamingJobConfig:
    """Configuration for a streaming job"""
    name: str
    engine: StreamingEngine
    input_topics: List[str]
    output_topics: List[str]
    parallelism: int
    memory_mb: int
    checkpoint_interval_ms: int
    description: str

# Streaming job configurations for production deployment
STREAMING_JOBS = {
    "peg_stability_processor": StreamingJobConfig(
        name="peg-stability-processor",
        engine=StreamingEngine.FLINK,
        input_topics=["cc.prices"],
        output_topics=["metrics.peg-stability"],
        parallelism=4,
        memory_mb=2048,
        checkpoint_interval_ms=30000,  # 30 seconds
        description="Real-time peg stability calculation"
    ),
    
    "liquidity_metrics_processor": StreamingJobConfig(
        name="liquidity-metrics-processor", 
        engine=StreamingEngine.FLINK,
        input_topics=["cc.orderbook"],
        output_topics=["metrics.liquidity"],
        parallelism=6,
        memory_mb=4096,
        checkpoint_interval_ms=15000,  # 15 seconds
        description="Order book depth and liquidity analysis"
    ),
    
    "ray_calculator": StreamingJobConfig(
        name="ray-calculator",
        engine=StreamingEngine.FLINK,
        input_topics=["dl.apy", "metrics.peg-stability", "metrics.liquidity"],
        output_topics=["ray.calculated"],
        parallelism=3,
        memory_mb=3072,
        checkpoint_interval_ms=60000,  # 1 minute
        description="Risk-Adjusted Yield calculation"
    ),
    
    "syi_index_calculator": StreamingJobConfig(
        name="syi-index-calculator",
        engine=StreamingEngine.FLINK,
        input_topics=["ray.calculated", "ex.mktcap"],
        output_topics=["syi.calculated"],
        parallelism=1,
        memory_mb=2048,
        checkpoint_interval_ms=60000,  # 1 minute
        description="StableYield Index calculation"
    ),
    
    "risk_premium_calculator": StreamingJobConfig(
        name="risk-premium-calculator",
        engine=StreamingEngine.SPARK,
        input_topics=["syi.calculated", "trad.tbill"],
        output_topics=["risk-premium.calculated"],
        parallelism=2,
        memory_mb=1536,
        checkpoint_interval_ms=300000,  # 5 minutes
        description="Risk premium calculation (SYI - T-Bill)"
    )
}

class FlinkConfig:
    """Apache Flink configuration"""
    
    def __init__(self):
        self.jobmanager_heap = os.getenv('FLINK_JOBMANAGER_HEAP', '1024m')
        self.taskmanager_heap = os.getenv('FLINK_TASKMANAGER_HEAP', '2048m')
        self.taskmanager_slots = int(os.getenv('FLINK_TASKMANAGER_SLOTS', '4'))
        self.parallelism_default = int(os.getenv('FLINK_PARALLELISM_DEFAULT', '2'))
        self.checkpoint_dir = os.getenv('FLINK_CHECKPOINT_DIR', 's3://stableyield-checkpoints/flink')
        self.savepoint_dir = os.getenv('FLINK_SAVEPOINT_DIR', 's3://stableyield-savepoints/flink')
    
    def get_flink_config(self) -> Dict:
        """Get Flink configuration properties"""
        return {
            # Job Manager
            'jobmanager.memory.process.size': self.jobmanager_heap,
            'jobmanager.rpc.address': 'localhost',
            'jobmanager.rpc.port': '6123',
            'jobmanager.bind-host': '0.0.0.0',
            
            # Task Manager
            'taskmanager.memory.process.size': self.taskmanager_heap,
            'taskmanager.numberOfTaskSlots': str(self.taskmanager_slots),
            'taskmanager.bind-host': '0.0.0.0',
            
            # Parallelism
            'parallelism.default': str(self.parallelism_default),
            
            # Checkpointing
            'state.backend': 'filesystem',
            'state.checkpoints.dir': self.checkpoint_dir,
            'state.savepoints.dir': self.savepoint_dir,
            'execution.checkpointing.interval': '60000',  # 1 minute
            'execution.checkpointing.mode': 'EXACTLY_ONCE',
            'execution.checkpointing.timeout': '300000',  # 5 minutes
            
            # Restart Strategy
            'restart-strategy': 'fixed-delay',
            'restart-strategy.fixed-delay.attempts': '5',
            'restart-strategy.fixed-delay.delay': '30s',
            
            # Kafka
            'connector.kafka.bootstrap.servers': os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092'),
            'connector.kafka.security.protocol': os.getenv('KAFKA_SECURITY_PROTOCOL', 'PLAINTEXT'),
            
            # High Availability
            'high-availability': 'zookeeper',
            'high-availability.zookeeper.quorum': os.getenv('ZOOKEEPER_QUORUM', 'localhost:2181'),
            'high-availability.storageDir': os.getenv('FLINK_HA_STORAGE_DIR', 's3://stableyield-ha/flink'),
            
            # Metrics
            'metrics.reporters': 'prometheus',
            'metrics.reporter.prometheus.class': 'org.apache.flink.metrics.prometheus.PrometheusReporter',
            'metrics.reporter.prometheus.port': '9250'
        }

class SparkConfig:
    """Apache Spark Streaming configuration"""
    
    def __init__(self):
        self.app_name = "StableYield-Streaming"
        self.master = os.getenv('SPARK_MASTER', 'local[*]')
        self.driver_memory = os.getenv('SPARK_DRIVER_MEMORY', '2g')
        self.executor_memory = os.getenv('SPARK_EXECUTOR_MEMORY', '4g')
        self.executor_cores = int(os.getenv('SPARK_EXECUTOR_CORES', '2'))
        self.max_executors = int(os.getenv('SPARK_MAX_EXECUTORS', '10'))
    
    def get_spark_config(self) -> Dict:
        """Get Spark configuration properties"""
        return {
            # Application
            'spark.app.name': self.app_name,
            'spark.master': self.master,
            
            # Driver
            'spark.driver.memory': self.driver_memory,
            'spark.driver.cores': '2',
            'spark.driver.maxResultSize': '2g',
            
            # Executor
            'spark.executor.memory': self.executor_memory,
            'spark.executor.cores': str(self.executor_cores),
            'spark.executor.instances': '3',
            
            # Dynamic Allocation
            'spark.dynamicAllocation.enabled': 'true',
            'spark.dynamicAllocation.minExecutors': '1',
            'spark.dynamicAllocation.maxExecutors': str(self.max_executors),
            'spark.dynamicAllocation.initialExecutors': '2',
            
            # Streaming
            'spark.streaming.receiver.maxRate': '10000',
            'spark.streaming.kafka.maxRatePerPartition': '1000',
            'spark.streaming.backpressure.enabled': 'true',
            
            # Checkpointing
            'spark.sql.streaming.checkpointLocation': os.getenv('SPARK_CHECKPOINT_DIR', '/tmp/spark-checkpoint'),
            'spark.sql.streaming.stateStore.maintenanceInterval': '60s',
            
            # Kafka
            'spark.kafka.bootstrap.servers': os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092'),
            
            # Serialization
            'spark.serializer': 'org.apache.spark.serializer.KryoSerializer',
            'spark.sql.adaptive.enabled': 'true',
            'spark.sql.adaptive.coalescePartitions.enabled': 'true',
            
            # Monitoring
            'spark.eventLog.enabled': 'true',
            'spark.eventLog.dir': os.getenv('SPARK_EVENTLOG_DIR', '/tmp/spark-events'),
            'spark.history.fs.logDirectory': os.getenv('SPARK_EVENTLOG_DIR', '/tmp/spark-events'),
            
            # Metrics
            'spark.metrics.conf.driver.source.jvm.class': 'org.apache.spark.metrics.source.JvmSource',
            'spark.metrics.conf.executor.source.jvm.class': 'org.apache.spark.metrics.source.JvmSource'
        }

# Streaming job templates (would be actual Flink/Spark job definitions in production)
FLINK_JOB_TEMPLATES = {
    "peg_stability_processor": """
    // Flink job for peg stability calculation
    StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
    env.enableCheckpointing(30000);
    
    DataStream<PriceData> priceStream = env
        .addSource(new FlinkKafkaConsumer<>("cc.prices", new PriceDataSchema(), kafkaProps));
    
    DataStream<PegStabilityMetrics> pegMetrics = priceStream
        .keyBy(PriceData::getSymbol)
        .window(TumblingEventTimeWindows.of(Time.minutes(1)))
        .aggregate(new PegStabilityAggregator())
        .map(new PegScoreCalculator());
    
    pegMetrics.addSink(new FlinkKafkaProducer<>("metrics.peg-stability", new PegMetricsSchema(), kafkaProps));
    """,
    
    "liquidity_metrics_processor": """
    // Flink job for liquidity metrics calculation
    StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
    
    DataStream<OrderBookSnapshot> orderbookStream = env
        .addSource(new FlinkKafkaConsumer<>("cc.orderbook", new OrderBookSchema(), kafkaProps));
    
    DataStream<LiquidityMetrics> liquidityMetrics = orderbookStream
        .keyBy(data -> data.getSymbol() + "-" + data.getVenue())
        .map(new LiquidityDepthCalculator())
        .map(new EffectiveSpreadCalculator())
        .map(new LiquidityScoreCalculator());
    
    liquidityMetrics.addSink(new FlinkKafkaProducer<>("metrics.liquidity", new LiquiditySchema(), kafkaProps));
    """,
    
    "syi_index_calculator": """
    // Flink job for StableYield Index calculation
    StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
    
    DataStream<RAYObservation> rayStream = env
        .addSource(new FlinkKafkaConsumer<>("ray.calculated", new RAYSchema(), kafkaProps));
    
    DataStream<MarketCapData> mktcapStream = env
        .addSource(new FlinkKafkaConsumer<>("ex.mktcap", new MarketCapSchema(), kafkaProps));
    
    DataStream<IndexValue> indexStream = rayStream
        .connect(mktcapStream)
        .keyBy(RAYObservation::getSymbol, MarketCapData::getSymbol)
        .window(TumblingEventTimeWindows.of(Time.minutes(1)))
        .apply(new StableYieldIndexCalculator());
    
    indexStream.addSink(new FlinkKafkaProducer<>("syi.calculated", new IndexValueSchema(), kafkaProps));
    """
}

SPARK_JOB_TEMPLATES = {
    "risk_premium_calculator": """
    // Spark Structured Streaming job for risk premium calculation
    SparkSession spark = SparkSession.builder()
        .appName("StableYield-RiskPremium")
        .getOrCreate();
    
    Dataset<Row> syiStream = spark
        .readStream()
        .format("kafka")
        .option("kafka.bootstrap.servers", kafkaServers)
        .option("subscribe", "syi.calculated")
        .load();
    
    Dataset<Row> tbillStream = spark
        .readStream()
        .format("kafka")
        .option("kafka.bootstrap.servers", kafkaServers) 
        .option("subscribe", "trad.tbill")
        .load();
    
    Dataset<Row> riskPremium = syiStream
        .join(tbillStream, "timestamp")
        .select(
            col("timestamp"),
            col("syi_value").minus(col("tbill_rate")).alias("risk_premium")
        );
    
    StreamingQuery query = riskPremium
        .writeStream()
        .format("kafka")
        .option("kafka.bootstrap.servers", kafkaServers)
        .option("topic", "risk-premium.calculated")
        .option("checkpointLocation", checkpointDir)
        .start();
    """
}

# Deployment configuration
DEPLOYMENT_CONFIG = {
    "flink": {
        "jobmanager": {
            "replicas": 1,
            "cpu": "1000m",
            "memory": "2Gi",
            "storage": "10Gi"
        },
        "taskmanager": {
            "replicas": 3,
            "cpu": "2000m", 
            "memory": "4Gi",
            "storage": "20Gi"
        }
    },
    "spark": {
        "driver": {
            "cpu": "1000m",
            "memory": "2Gi",
            "storage": "10Gi"
        },
        "executor": {
            "instances": 3,
            "cpu": "2000m",
            "memory": "4Gi",
            "storage": "20Gi"
        }
    },
    "monitoring": {
        "prometheus": True,
        "grafana": True,
        "jaeger": True,
        "elasticsearch": True
    }
}

# TODO: PRODUCTION DEPLOYMENT CHECKLIST
# 1. Set up Flink cluster with proper resource allocation
# 2. Deploy Spark cluster with dynamic allocation
# 3. Configure Kafka Connect for external data sources
# 4. Set up monitoring with Prometheus and Grafana
# 5. Implement proper error handling and dead letter queues
# 6. Configure backup and disaster recovery for checkpoints
# 7. Set up automated testing for streaming jobs
# 8. Implement CI/CD pipeline for job deployment
# 9. Configure alerting for job failures and performance issues
# 10. Set up proper logging and observability stack