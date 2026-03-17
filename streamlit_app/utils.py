import os
import joblib

# Paths
BASE_DIR = os.path.dirname(__file__)
MODEL_DIR = os.path.join(BASE_DIR, "..", "models")

# Load ML models
def load_models():
    return {
        "Random Forest": joblib.load(os.path.join(MODEL_DIR, "rf_model.pkl")),
        "XGBoost": joblib.load(os.path.join(MODEL_DIR, "xgb_model.pkl")),
        "LightGBM": joblib.load(os.path.join(MODEL_DIR, "lgbm_model.pkl")),
    }

# Optional: retention strategy helper
def retention_strategy(prob):
    if prob > 0.7:
        return "🔥 High Risk: Offer premium benefits + personal call"
    elif prob > 0.5:
        return "⚠ Medium Risk: Give discounts & engagement offers"
    elif prob > 0.3:
        return "📊 Monitor customer behavior"
    else:
        return "✅ Customer stable"