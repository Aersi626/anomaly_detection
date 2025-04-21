# 🔧 Real-Time Industrial Anomaly Detection

A production-ready anomaly detection system using **Kafka**, **Streamlit**, **Isolation Forest**, and **AutoEncoders**. Built for streaming industrial sensor data to detect equipment failure in real time.

---

## 🚀 Features
- Simulates real-time sensor data with Kafka
- Detects anomalies using Isolation Forest + AutoEncoder hybrid
- Uses rolling statistics and PCA for robust feature extraction
- Live visualizations in Streamlit dashboard
- Logs anomalies with timestamps to a SQLite database

---

## 📁 Project Structure

```
real_time_anomaly_detection/
├── app/
│   ├── anomaly_detection_app.py      # Streamlit dashboard
│   └── db_logger.py                  # SQLite anomaly logger
├── kafka/
│   ├── simulate_kafka_producer.py   # Streams sensor data to Kafka
│   └── docker-compose.yml           # Kafka + Zookeeper services
├── data/
│   └── uci-secom.csv                # Sensor dataset
├── requirements.txt                 # Python dependencies
└── README.md                        # Project overview
```

---

## 🛠 Installation

1. **Clone the repository**
```bash
git clone https://github.com/Aersi626/real_time_anomaly_detection.git
cd real_time_anomaly_detection
```

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

3. **Start Kafka services**
```bash
cd kafka
docker-compose up -d
```

4. **Simulate data streaming**
```bash
cd ..
python kafka/simulate_kafka_producer.py
```

5. **Run the Streamlit app**
```bash
streamlit run app/anomaly_detection_app.py
```

---

## 🧠 Model Overview
- Isolation Forest on PCA + AutoEncoder reconstruction error
- Rolling mean used to stabilize input features
- Anomaly scores visualized and logged to SQLite

---

## 📊 Database Logging
- Logs anomaly score + detection flag with timestamp
- SQLite DB: `anomalies.db`
- Viewable directly in the Streamlit dashboard

---

## 📌 Notes
- Requires Docker for Kafka
- You can expand with Slack/email alerts or batch retraining
- Dataset based on UCI SECOM (semiconductor manufacturing)

---

## 📜 License
MIT

---