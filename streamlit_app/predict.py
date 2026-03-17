import os
import joblib

BASE_DIR = os.path.dirname(__file__)
MODEL_DIR = os.path.join(BASE_DIR, "..", "models")

def load_models():
    return {
        "Random Forest": joblib.load(os.path.join(MODEL_DIR, "rf_model.pkl")),
        "XGBoost": joblib.load(os.path.join(MODEL_DIR, "xgb_model.pkl")),
        "LightGBM": joblib.load(os.path.join(MODEL_DIR, "lgbm_model.pkl")),
    }

def predict_churn(model, data):
    prob = model.predict_proba(data)[:, 1]
    risk = []
    for p in prob:
        if p < 0.4: risk.append("Low Risk")
        elif p < 0.7: risk.append("Medium Risk")
        else: risk.append("High Risk")
    return prob, risk