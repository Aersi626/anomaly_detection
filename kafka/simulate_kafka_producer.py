# simulate_kafka_producer.py

import pandas as pd
import time
from kafka import KafkaProducer
import json

# Set up Kafka producer
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Load and prepare data
df = pd.read_csv("../data/uci-secom.csv")
df = df.fillna(method='ffill').fillna(method='bfill')

# Stream each row as a Kafka message
for i, row in df.iterrows():
    message = row.to_dict()
    producer.send("sensor_data", message)
    print(f"[Kafka] Sent row {i}")
    time.sleep(0.1)  # simulate streaming at ~10 rows/sec

producer.flush()