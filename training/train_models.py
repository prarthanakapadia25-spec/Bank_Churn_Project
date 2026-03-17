import pandas as pd
import joblib
import os

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import xgboost as xgb
import lightgbm as lgb

BASE_DIR = os.path.dirname(__file__)

data_path = os.path.join(BASE_DIR, "..", "data", "bank_churn.csv")
model_path = os.path.join(BASE_DIR, "..", "models")

df = pd.read_csv(data_path)

# 🔴 STEP 1: REMOVE UNNECESSARY COLUMNS
drop_cols = ["RowNumber", "CustomerId", "Surname"]

for col in drop_cols:
    if col in df.columns:
        df = df.drop(col, axis=1)

# 🔴 STEP 2: HANDLE DIRTY VALUES
# Remove weird geography like "P'an"
df = df[df["Geography"].isin(["France", "Germany", "Spain"])]

# 🔴 STEP 3: ENCODE CATEGORICAL DATA
df = pd.get_dummies(df, columns=["Geography","Gender"], drop_first=True)

# 🔴 STEP 4: SPLIT DATA
X = df.drop("Exited", axis=1)
y = df["Exited"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 🔴 STEP 5: TRAIN MODELS
rf = RandomForestClassifier(n_estimators=200)
rf.fit(X_train, y_train)

xgb_model = xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss')
xgb_model.fit(X_train, y_train)

lgbm = lgb.LGBMClassifier()
lgbm.fit(X_train, y_train)

# 🔴 STEP 6.1: SAVE FEATURE LIST
feature_path = os.path.join(model_path, "features.pkl")
joblib.dump(X.columns.tolist(), feature_path)

# 🔴 STEP 6: SAVE MODELS
joblib.dump(rf, os.path.join(model_path,"rf_model.pkl"))
joblib.dump(xgb_model, os.path.join(model_path,"xgb_model.pkl"))
joblib.dump(lgbm, os.path.join(model_path,"lgbm_model.pkl"))
joblib.dump(X.columns.tolist(), os.path.join(model_path,"features.pkl"))
print("✅ Models trained successfully")