# anomaly_detection_app.py

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import precision_score
from sklearn.neural_network import MLPRegressor
import streamlit as st
from kafka import KafkaConsumer
import json
from collections import deque
from db_logger import init_db, log_anomalies, read_anomalies



# Streamlit UI
st.set_page_config(page_title="🔧 Industrial Anomaly Detection", layout="wide")
st.title("🔧 Industrial Sensor Anomaly Detection")
st.write("Real-time anomaly detection using Kafka + Isolation Forest + AutoEncoder")

# Parameters
buffer_size = 100
consumer = KafkaConsumer(
    "sensor_data",
    bootstrap_servers="localhost:9092",
    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    auto_offset_reset="latest",
    enable_auto_commit=True
)

# State buffers
if "raw_buffer" not in st.session_state:
    st.session_state.raw_buffer = deque(maxlen=buffer_size)

# Collect messages
st.subheader("Streaming from Kafka...")
new_messages = 0
for message in consumer.poll(timeout_ms=1000, max_records=buffer_size).values():
    for record in message:
        st.session_state.raw_buffer.append(record.value)
        new_messages += 1

st.write(f"Received {new_messages} new messages")

if len(st.session_state.raw_buffer) < 10:
    st.warning("Waiting for more data...")
    st.stop()

# Convert to DataFrame
df = pd.DataFrame(st.session_state.raw_buffer)
df = df.dropna(axis=1, thresh=0.9 * len(df))
df = df.fillna(method='ffill').fillna(method='bfill')

# Rolling statistics
df_rolled = df.rolling(window=5, min_periods=1).mean()

# Feature extraction
scaler = StandardScaler()
X_scaled = scaler.fit_transform(df_rolled)
pca = PCA(n_components=10)
X_pca = pca.fit_transform(X_scaled)

autoencoder = MLPRegressor(hidden_layer_sizes=(32, 16, 32), max_iter=100, random_state=42)
autoencoder.fit(X_pca, X_pca)
X_reconstructed = autoencoder.predict(X_pca)
reconstruction_error = np.mean((X_pca - X_reconstructed) ** 2, axis=1)

X_combined = np.hstack([X_pca, reconstruction_error.reshape(-1, 1)])
clf = IsolationForest(contamination=0.05, random_state=42)
y_pred = clf.fit_predict(X_combined)

# Anomaly visualization
anomaly_score = clf.decision_function(X_combined)
results = pd.DataFrame({
    "Anomaly Score": -anomaly_score,
    "Predicted Anomaly": (y_pred == -1).astype(int)
})

# After predicting anomalies
log_anomalies(anomaly_score, (y_pred == -1).astype(int))

# Optionally display history
st.subheader("📜 Recent Anomaly Log")
st.dataframe(read_anomalies())

st.metric("Anomaly Count", int((y_pred == -1).sum()))
st.line_chart(results["Anomaly Score"].rolling(10).mean())
st.dataframe(results.tail(20))