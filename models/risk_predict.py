import os
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier

MODEL_DIR = "models"
MODEL_PATH = os.path.join(MODEL_DIR, "risk_model.pkl")

def train_risk_model(df, score_threshold=65, attendance_threshold=75):
    """
    Trains a RandomForest model to predict if a student is at risk.
    Saves the trained model to a file.
    """
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)

    X = df[["Math", "Science", "English", "Attendance"]]
    # Define 'at-risk' condition
    y = ((X[["Math", "Science", "English"]].mean(axis=1) < score_threshold) | 
         (X["Attendance"] < attendance_threshold)).astype(int)
    
    clf = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
    clf.fit(X, y)
    
    joblib.dump(clf, MODEL_PATH)
    print(f"Risk model trained with thresholds (Score<{score_threshold}, Att<{attendance_threshold}) and saved.")
    return clf

def predict_risk(row, clf):
    """
    Predicts risk for a single student row using a loaded classifier.
    """
    X_pred = np.array([[row['Math'], row['Science'], row['English'], row['Attendance']]])
    return bool(clf.predict(X_pred)[0])

def load_risk_model(df_for_training=None):
    """
    Loads the risk model from file. If it doesn't exist, it trains a new one.
    """
    if os.path.exists(MODEL_PATH):
        print("Loading existing risk model.")
        return joblib.load(MODEL_PATH)
    elif df_for_training is not None:
        print("No risk model found. Training a new one with default thresholds.")
        return train_risk_model(df_for_training)
    else:
        return None