# model_supervised.py

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, precision_score, recall_score, f1_score
from xgboost import XGBClassifier
import streamlit as st

def train_supervised_model(df: pd.DataFrame, test_size: float = 0.3, label_col: str = "Pass/Fail", random_state: int = 42):
    """
    Trains an XGBoost classifier on labeled sensor data.

    Args:
        df (pd.DataFrame): Data with numeric features and a binary label column.
        test_size (float): Proportion of data to use for test split.
        label_col (str): Name of the label column ('Pass/Fail').
        random_state (int): Random seed for reproducibility.

    Returns:
        dict: Model, metrics, and test predictions.
    """
    st.write("➡️ Preprocessing data...")
    # Drop rows with missing label
    df = df.dropna(subset=[label_col])
    
    # Separate features and label
    y = df[label_col].astype(int).replace(-1, 0).values
    df_features = df.select_dtypes(include=["number"]).drop(columns=[label_col])

    # Rolling average to smooth out noise
    df_rolled = df_features.rolling(window=5, min_periods=1).mean()

    # Standardize features
    scaler = StandardScaler()
    X = scaler.fit_transform(df_rolled)

    # Split
    st.write("🧠 Splitting data into train and test sets...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)

    # Train model
    st.write("🚀 Fitting XGBoost model...")
    model = XGBClassifier(eval_metric='logloss', random_state=random_state)
    model.fit(X_train, y_train)
    st.write("✅ Model training completed.")
    y_pred = model.predict(X_test)

    # Compute metrics
    metrics = {
        "precision": precision_score(y_test, y_pred),
        "recall": recall_score(y_test, y_pred),
        "f1": f1_score(y_test, y_pred),
        "accuracy": np.mean(y_pred == y_test),
        "classification_report": classification_report(y_test, y_pred, output_dict=True),
        "confusion_matrix": pd.crosstab(y_test, y_pred, rownames=["Actual"], colnames=["Predicted"])
    }

    return {
        "model": model,
        "metrics": metrics,
        "X_test": X_test,
        "y_test": y_test,
        "y_pred": y_pred
    }
