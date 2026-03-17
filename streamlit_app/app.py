import streamlit as st
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from sklearn.cluster import KMeans

from utils import load_models, retention_strategy
from predict import predict_churn
from database import register_user, login_user

st.set_page_config(layout="wide", page_title="Bank Churn Dashboard")

# ---------------- SESSION ----------------
if "user" not in st.session_state:
    st.session_state.user = None
if "register" not in st.session_state:
    st.session_state.register = False

# ---------------- PROFESSIONAL LOGIN (FLEX CENTER) ----------------
if st.session_state.user is None:
    st.markdown("""
    <style>
    /* Full viewport background, remove Streamlit padding */
    body, .stApp, .main, .block-container {
        margin: 0;
        padding: 0;
        height: 100vh;
        width: 100vw;
        background: linear-gradient(to right, #e0f7fa, #80deea);
    }

    /* Flex container centers card perfectly */
    .login-container {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100%;
        width: 50%;
    }

    /* Card style */
    .login-card {
        background: white;
        width: 400px;
        max-width: 90%;
        padding: 50px 40px;
        border-radius: 15px;
        box-shadow: 0px 15px 40px rgba(0,0,0,0.2);
        text-align: center;
        transition: transform 0.3s;
    }
    .login-card:hover {transform: scale(1.02);}
    .login-header {
        font-size: 28px;
        font-weight: bold;
        color: #0277bd;
        margin-bottom: 30px;
    }
    .login-input {
        width: 100%;
        padding: 12px 15px;
        margin: 10px 0 20px 0;
        border: 1px solid #b0bec5;
        border-radius: 8px;
        font-size: 16px;
    }
    .login-input:focus {
        border-color: #0288d1;
        box-shadow: 0 0 8px rgba(2,136,209,0.3);
        outline: none;
    }
    .login-btn {
        width: 100%;
        padding: 12px 0;
        border: none;
        border-radius: 8px;
        background: linear-gradient(135deg, #0288d1, #26c6da);
        color: white;
        font-size: 18px;
        font-weight: bold;
        cursor: pointer;
        transition: 0.3s;
    }
    .login-btn:hover {
        background: linear-gradient(135deg, #26c6da, #0288d1);
        transform: scale(1.02);
    }
    .toggle-link {
        margin-top: 15px;
        font-size: 14px;
        color: #0288d1;
        cursor: pointer;
        text-decoration: underline;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<div class="login-card">', unsafe_allow_html=True)

    if not st.session_state.register:
        st.markdown('<div class="login-header">Login</div>', unsafe_allow_html=True)
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username", key="login_user")
            password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_pass")
            submit = st.form_submit_button("Login")
            if submit:
                if login_user(username, password):
                    st.session_state.user = username
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid credentials")
        st.markdown('<div class="toggle-link" onclick="window.location.reload()">Create Account</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="login-header">Register</div>', unsafe_allow_html=True)
        with st.form("register_form"):
            username = st.text_input("Username", placeholder="Choose a username", key="reg_user")
            password = st.text_input("Password", type="password", placeholder="Enter password", key="reg_pass")
            confirm = st.text_input("Confirm Password", type="password", placeholder="Confirm password", key="reg_confirm")
            submit = st.form_submit_button("Register")
            if submit:
                if password != confirm:
                    st.error("Passwords do not match")
                else:
                    register_user(username, password)
                    st.success("Account created! Please login.")
                    st.session_state.register = False
                    st.rerun()
        st.markdown('<div class="toggle-link" onclick="window.location.reload()">Back to Login</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()
# ---------------- LOAD DATA ----------------
BASE_DIR = os.path.dirname(__file__)
data_path = os.path.join(BASE_DIR, "..", "data", "bank_churn.csv")
df = pd.read_csv(data_path)
df_encoded = pd.get_dummies(df.drop(columns=["CustomerId","Surname"]), columns=["Geography","Gender"], drop_first=True)
models = load_models()

# ---------------- NAVBAR ----------------
st.markdown(f"""
<style>
.navbar {{
    display: flex; justify-content: space-between; align-items: center;
    background-color: #2E86C1; padding: 10px 30px; border-radius: 10px; color: white; font-size: 20px;}}
.profile-icon {{
    border-radius: 50%; background-color: #fff; color: #2E86C1; padding: 5px 10px; font-weight: bold;}}
.logout-btn {{
    background-color: #E74C3C; border: none; color: white; padding: 5px 10px; border-radius: 5px; cursor: pointer;}}
</style>
<div class="navbar">
    <div>🏦 Bank Churn Dashboard</div>
    <div>
        <span class="profile-icon">{st.session_state.user}</span>
        <button class="logout-btn" onclick="window.location.reload()">Logout</button>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR FILTERS ----------------
st.sidebar.title("Filters & Prediction Inputs")
with st.sidebar.expander("Model & Theme", expanded=True):
    model_name = st.selectbox("Model", list(models.keys()))
    model = models[model_name]
    theme = st.selectbox("Theme", ["Professional","Dark Elegant","Soft Pastel"])

# Risk colors
risk_colors = {"Low Risk":"#2E86C1","Medium Risk":"#F1C40F","High Risk":"#E74C3C"} if theme=="Professional" else \
              {"Low Risk":"#16A085","Medium Risk":"#F39C12","High Risk":"#C0392B"} if theme=="Dark Elegant" else \
              {"Low Risk":"#61CCC1","Medium Risk":"#7B5185","High Risk":"#ED8DC8"}

# ---------------- FILTER INPUTS ----------------
with st.sidebar.expander("Customer Attributes", expanded=True):
    # Manual input boxes for numeric filters
    age_min = int(st.text_input("Age Min", str(int(df.Age.min()))))
    age_max = int(st.text_input("Age Max", str(int(df.Age.max()))))
    
    balance_min = float(st.text_input("Balance Min", str(float(df.Balance.min()))))
    balance_max = float(st.text_input("Balance Max", str(float(df.Balance.max()))))
    
    credit_min = int(st.text_input("Credit Score Min", str(int(df.CreditScore.min()))))
    credit_max = int(st.text_input("Credit Score Max", str(int(df.CreditScore.max()))))
    
    tenure_min = int(st.text_input("Tenure Min", str(int(df.Tenure.min()))))
    tenure_max = int(st.text_input("Tenure Max", str(int(df.Tenure.max()))))
    
    products_min = int(st.text_input("NumOfProducts Min", str(int(df.NumOfProducts.min()))))
    products_max = int(st.text_input("NumOfProducts Max", str(int(df.NumOfProducts.max()))))
    
    geography = st.multiselect("Geography", df.Geography.unique(), default=list(df.Geography.unique()))
    gender = st.multiselect("Gender", df.Gender.unique(), default=list(df.Gender.unique()))
    
    has_card = st.selectbox("Has Credit Card", ["All", "Yes", "No"])
    is_active = st.selectbox("Is Active Member", ["All", "Yes", "No"])
    
    salary_min = float(st.text_input("Estimated Salary Min", str(float(df.EstimatedSalary.min()))))
    salary_max = float(st.text_input("Estimated Salary Max", str(float(df.EstimatedSalary.max()))))

# ---------------- APPLY FILTERS ----------------
f = df[
    (df.Age.between(age_min, age_max)) &
    (df.Balance.between(balance_min, balance_max)) &
    (df.CreditScore.between(credit_min, credit_max)) &
    (df.Tenure.between(tenure_min, tenure_max)) &
    (df.NumOfProducts.between(products_min, products_max)) &
    (df.Geography.isin(geography)) &
    (df.Gender.isin(gender)) &
    (df.EstimatedSalary.between(salary_min, salary_max))
].copy()

if has_card!="All":
    f = f[f.HasCrCard==(1 if has_card=="Yes" else 0)]
if is_active!="All":
    f = f[f.IsActiveMember==(1 if is_active=="Yes" else 0)]

# ---------------- ENCODE FOR MODEL (FIXED) ----------------
enc = pd.get_dummies(f.drop(columns=["CustomerId","Surname"]), columns=["Geography","Gender"], drop_first=True)
expected_cols = df_encoded.columns.drop("Exited")
for col in expected_cols:
    if col not in enc.columns: enc[col] = 0
enc = enc[expected_cols]

# ---------------- PREDICTION ----------------
prob, risk = predict_churn(model, enc)
f["Risk"] = risk

# ---------------- PREMIUM KPI CARDS ----------------
st.markdown("""
<style>
.kpi-card {background: linear-gradient(135deg, #71b7e6, #9b59b6); border-radius: 20px; padding: 20px;
            color: white; text-align: center; box-shadow: 0px 10px 20px rgba(0,0,0,0.2); transition: transform 0.3s;}
.kpi-card:hover {transform: scale(1.05);}
</style>
""", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
c1.markdown(f'<div class="kpi-card"><h3>Customers</h3><h1>{len(f)}</h1></div>', unsafe_allow_html=True)
c2.markdown(f'<div class="kpi-card"><h3>Avg Churn %</h3><h1>{prob.mean()*100:.2f}</h1></div>', unsafe_allow_html=True)
c3.markdown(f'<div class="kpi-card"><h3>High Risk</h3><h1>{risk.count("High Risk")}</h1></div>', unsafe_allow_html=True)
c4.markdown(f'<div class="kpi-card"><h3>Low Risk</h3><h1>{risk.count("Low Risk")}</h1></div>', unsafe_allow_html=True)

# ---------------- CHARTS ----------------
st.subheader("📊 Visualization")
chart_type = st.selectbox("Select Chart", ["Histogram","Bar","Line","Scatter","Box","Pie","Donut","Heatmap"])
rc = f["Risk"].value_counts()
color_map = risk_colors

if chart_type == "Histogram": fig = px.histogram(f, x="Age", color="Risk", color_discrete_map=color_map)
elif chart_type == "Bar": fig = px.bar(x=rc.index, y=rc.values, color=rc.index, color_discrete_map=color_map)
elif chart_type == "Line": fig = px.line(f, x="Age", y="Balance", color="Risk", color_discrete_map=color_map)
elif chart_type == "Scatter": fig = px.scatter(f, x="Age", y="Balance", color="Risk", color_discrete_map=color_map)
elif chart_type == "Box": fig = px.box(f, x="Risk", y="Balance", color="Risk", color_discrete_map=color_map)
elif chart_type == "Pie": fig = px.pie(values=rc.values, names=rc.index, color=rc.index, color_discrete_map=color_map)
elif chart_type == "Donut": fig = go.Figure(data=[go.Pie(labels=rc.index, values=rc.values, hole=0.5,
                                                      marker=dict(colors=[color_map[r] for r in rc.index]))])
elif chart_type == "Heatmap": fig = px.imshow(f.select_dtypes(include=np.number).corr(), text_auto=True, color_continuous_scale="Blues")
st.plotly_chart(fig, use_container_width=True)

# ---------------- AI INSIGHTS ----------------
st.subheader("🔍 Insights")
reasons, solutions = [], []
high = (f["Risk"]=="High Risk").sum()
total = len(f)
high_pct = (high/total)*100 if total>0 else 0
avg_credit = f["CreditScore"].mean()
avg_balance = f["Balance"].mean()
avg_age = f["Age"].mean()
active_ratio = f["IsActiveMember"].mean()

if high_pct > 60: reasons.append("Majority customers are high risk"); solutions.append("Immediate retention needed")
elif high_pct > 30: reasons.append("Moderate churn risk present"); solutions.append("Run targeted campaigns")
else: reasons.append("Low churn risk overall"); solutions.append("Maintain current strategy")

if avg_credit < 500: reasons.append("Low credit score users"); solutions.append("Offer credit improvement plans")
if avg_balance > 120000: reasons.append("High balance customers leaving"); solutions.append("Provide premium benefits")
if avg_age > 50: reasons.append("Older customers churn more"); solutions.append("Add loyalty programs")
if active_ratio < 0.5: reasons.append("Low engagement users"); solutions.append("Improve engagement strategies")

for r in reasons: st.write("•", r)
st.write("### 💡 Solutions")
for s in solutions: st.write("•", s)

# ---------------- CUSTOMER SEGMENTATION ----------------
st.subheader("🤖 Customer Segmentation")
features = ["Age","Balance","CreditScore","EstimatedSalary"]
X = f[features]
kmeans = KMeans(n_clusters=3, random_state=42)
f["Segment"] = kmeans.fit_predict(X)
seg_counts = f["Segment"].value_counts()
fig_seg = px.pie(values=seg_counts.values, names=[f"Segment {i}" for i in seg_counts.index])
st.plotly_chart(fig_seg, use_container_width=True)

# ---------------- DOWNLOAD ----------------
st.download_button("📥 Download Data", f.to_csv(index=False), "customers.csv")