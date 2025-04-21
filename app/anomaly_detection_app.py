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

# # Add auto-refresh interval
# refresh_interval = st.sidebar.number_input("🔁 Auto-refresh (seconds)", min_value=2, max_value=300, value=60, step=1)
# st.query_params['refresh']=str(refresh_interval)
# st.markdown(f"_Auto-refreshing every {refresh_interval} seconds..._")
# st.rerun()

# Sidebar controls
with st.sidebar:
    st.header("⚙️ Model Components")
    use_pca = st.checkbox("Apply PCA", value=True)
    use_autoencoder = st.checkbox("Use AutoEncoder Reconstruction", value=True)
    pca_components = st.slider("PCA Components", min_value=5, max_value=50, value=10)
    contamination_rate = st.slider("Isolation Forest Contamination", 0.01, 0.20, 0.05, step=0.01)

# Parameters
buffer_size = 1000
consumer = KafkaConsumer(
    "sensor_data",
    bootstrap_servers="localhost:9092",
    group_id="anomaly-detector-v2",
    auto_offset_reset="earliest",
    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    enable_auto_commit=True
)

# State buffers
if "raw_buffer" not in st.session_state:
    st.session_state.raw_buffer = deque(maxlen=buffer_size)

# Collect messages
st.subheader("Streaming from Kafka...")
# Read messages from Kafka
new_messages = 0
messages = consumer.poll(timeout_ms=100000, max_records=buffer_size)
for topic_partition, records in messages.items():
    for record in records:
        st.session_state.raw_buffer.append(record.value)
        new_messages += 1

# Show user-friendly feedback
if new_messages == 0:
    st.info("⏳ Waiting for Kafka data... Please start the producer if it's not running.")
else:
    st.success(f"📥 Received {new_messages} new records")

if len(st.session_state.raw_buffer) < 10:
    st.warning("⚠️ Need at least 10 messages to start anomaly detection.")
    st.stop()

init_db()

# Convert to DataFrame
df = pd.DataFrame(st.session_state.raw_buffer)
df = df.dropna(axis=1, thresh=0.9 * len(df))
df = df.fillna(method='ffill').fillna(method='bfill')

# Rolling statistics
df_numeric = df.select_dtypes(include=["number"])
df_rolled = df_numeric.rolling(window=5, min_periods=1).mean()

# Feature extraction
scaler = StandardScaler()
X = scaler.fit_transform(df_rolled)
if use_pca:
    pca = PCA(n_components=pca_components)
    X = pca.fit_transform(X)

if use_autoencoder:
    ae = MLPRegressor(hidden_layer_sizes=(32, 16, 32), max_iter=1000, random_state=42)
    ae.fit(X, X)
    X_recon = ae.predict(X)
    recon_error = np.mean((X - X_recon) ** 2, axis=1)
    X = np.hstack([X, recon_error.reshape(-1, 1)])

clf = IsolationForest(contamination=0.05, random_state=42)
y_pred = clf.fit_predict(X)

# Anomaly visualization
anomaly_score = clf.decision_function(X)
results = pd.DataFrame({
    "Anomaly Score": -anomaly_score,
    "Predicted Anomaly": (y_pred == -1).astype(int)
})

st.metric("Anomaly Count", int((y_pred == -1).sum()))
st.line_chart(results["Anomaly Score"].rolling(10).mean())
st.dataframe(results.tail(100))

# After predicting anomalies
log_anomalies(anomaly_score, (y_pred == -1).astype(int))

# Optionally display history
st.subheader("📜 Recent Anomaly Log")
st.dataframe(read_anomalies())