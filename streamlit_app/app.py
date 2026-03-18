import streamlit as st
import pandas as pd
import plotly.express as px
import os 

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Customer Churn Dashboard", layout="wide")

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    base_path = os.path.dirname(__file__)
    file_path = os.path.join(base_path, "..", "data", "bank_churn.csv")
    return pd.read_csv(file_path)

df = load_data()

# ---------------- COLOR THEMES ----------------
color_options = {
    "Default": px.colors.qualitative.Plotly,
    "Dark": px.colors.qualitative.Dark24,
    "Pastel": px.colors.qualitative.Pastel,
    "Bold": px.colors.qualitative.Bold,
    "Vivid": px.colors.qualitative.Vivid
}

selected_colors = st.sidebar.selectbox("🎨 Chart Theme", list(color_options.keys()))
colors = color_options[selected_colors]

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
body {background-color: #0e1117;}
h1, h2, h3 {color: #ffffff;}
.stMetric {
    background-color: lightblue;
    padding: 15px;
    border-radius: 10px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# ---------------- TITLE ----------------
st.title("🏦 Customer Churn Analysis Dashboard")

# ---------------- SIDEBAR FILTERS ----------------
st.sidebar.header("🔍 Advanced Filters")

filtered_df = df.copy()

country = st.sidebar.multiselect("🌍 Country", df["Geography"].unique())
if country:
    filtered_df = filtered_df[filtered_df["Geography"].isin(country)]

gender = st.sidebar.multiselect("👤 Gender", df["Gender"].unique())
if gender:
    filtered_df = filtered_df[filtered_df["Gender"].isin(gender)]

active = st.sidebar.selectbox("🟢 Active Member", ["All", "Yes", "No"])
if active == "Yes":
    filtered_df = filtered_df[filtered_df["IsActiveMember"] == 1]
elif active == "No":
    filtered_df = filtered_df[filtered_df["IsActiveMember"] == 0]

card = st.sidebar.selectbox("💳 Has Credit Card", ["All", "Yes", "No"])
if card == "Yes":
    filtered_df = filtered_df[filtered_df["HasCrCard"] == 1]
elif card == "No":
    filtered_df = filtered_df[filtered_df["HasCrCard"] == 0]

tenure = st.sidebar.slider("📅 Tenure (Years)", int(df["Tenure"].min()), int(df["Tenure"].max()), (0,10))
filtered_df = filtered_df[(filtered_df["Tenure"] >= tenure[0]) & (filtered_df["Tenure"] <= tenure[1])]

balance = st.sidebar.slider("💰 Balance", float(df["Balance"].min()), float(df["Balance"].max()), (0.0, float(df["Balance"].max())))
filtered_df = filtered_df[(filtered_df["Balance"] >= balance[0]) & (filtered_df["Balance"] <= balance[1])]

products = st.sidebar.multiselect("📦 Number of Products", df["NumOfProducts"].unique())
if products:
    filtered_df = filtered_df[filtered_df["NumOfProducts"].isin(products)]

churn = st.sidebar.selectbox("📉 Churn Status", ["All", "Churned", "Retained"])
if churn == "Churned":
    filtered_df = filtered_df[filtered_df["Exited"] == 1]
elif churn == "Retained":
    filtered_df = filtered_df[filtered_df["Exited"] == 0]

# ---------------- DOWNLOAD FULL ----------------
st.sidebar.markdown("## 📥 Download")
st.sidebar.download_button("📊 Download Full Dataset",
                           df.to_csv(index=False),
                           "full_dataset.csv")

# ---------------- KPI CARDS ----------------
st.markdown("## 📊 Key Metrics")

col1, col2, col3, col4 = st.columns(4)

col1.metric("👥 Total Customers", len(filtered_df))
col2.metric("📉 Churn Rate", f"{filtered_df['Exited'].mean()*100:.2f}%")
col3.metric("🟢 Active Members", filtered_df["IsActiveMember"].sum())
col4.metric("💳 Credit Card Users", filtered_df["HasCrCard"].sum())

# ---------------- RISK SEGMENTATION ----------------
def assign_risk(row):
    score = 0
    if row["IsActiveMember"] == 0: score += 2
    if row["NumOfProducts"] <= 1: score += 2
    if row["Balance"] > 100000: score += 1
    if row["Age"] > 50: score += 1
    if row["HasCrCard"] == 0: score += 1

    if score >= 5:
        return "High Risk"
    elif score >= 3:
        return "Medium Risk"
    else:
        return "Low Risk"

filtered_df["RiskLevel"] = filtered_df.apply(assign_risk, axis=1)

# ---------------- RISK CHART ----------------
st.markdown("## ⚠️ Customer Risk Distribution")

fig = px.pie(filtered_df, names="RiskLevel",
             color_discrete_sequence=colors)
st.plotly_chart(fig, use_container_width=True)

# ---------------- CHART SELECTOR ----------------
st.markdown("## 📊 Visual Analysis")

chart_option = st.selectbox(
    "Select Chart Type",
    ["Pie Chart", "Bar Chart", "Scatter Plot", "Animated Chart"]
)

if chart_option == "Pie Chart":
    fig = px.pie(filtered_df, names="Geography", hole=0.4,
                 color_discrete_sequence=colors)
    st.plotly_chart(fig, use_container_width=True)

elif chart_option == "Bar Chart":
    age_churn = filtered_df.groupby("Age")["Exited"].mean().reset_index()
    fig = px.bar(age_churn, x="Age", y="Exited",
                 color="Exited",
                 color_continuous_scale="Teal")
    st.plotly_chart(fig, use_container_width=True)

elif chart_option == "Scatter Plot":
    fig = px.scatter(filtered_df,
                     x="Balance",
                     y="EstimatedSalary",
                     color="RiskLevel",
                     size="Age",
                     color_discrete_sequence=colors)
    st.plotly_chart(fig, use_container_width=True)

elif chart_option == "Animated Chart":
    temp_df = filtered_df.copy()
    temp_df["TenureGroup"] = temp_df["Tenure"].astype(str)

    fig = px.bar(temp_df,
                 x="Geography",
                 color="RiskLevel",
                 animation_frame="TenureGroup",
                 color_discrete_sequence=colors)
    st.plotly_chart(fig, use_container_width=True)

# ---------------- INSIGHTS ----------------
st.markdown("## 🧠 Churn Risk Insights")

overall_churn = filtered_df["Exited"].mean() * 100

high_risk = filtered_df[filtered_df["RiskLevel"] == "High Risk"]

# ✅ Better logic
if overall_churn > 40:
    st.error(f"🔴 High churn risk overall ({overall_churn:.2f}%)")
elif overall_churn > 20:
    st.warning(f"🟡 Moderate churn risk ({overall_churn:.2f}%)")
else:
    st.success(f"🟢 Low churn risk overall ({overall_churn:.2f}%)")

# Show high-risk count
st.write(f"⚠️ High Risk Customers: {len(high_risk)}")

# Smart insights
if len(high_risk) > 0:
    if high_risk["IsActiveMember"].mean() < 0.5:
        st.write("🔴 Customers are mostly inactive")

    if high_risk["NumOfProducts"].mean() < 2:
        st.write("🔴 Low product usage")

    if high_risk["Balance"].mean() > 100000:
        st.write("🔴 High-value customers at risk")

# ---------------- BUSINESS SOLUTION ----------------
st.markdown("## 💡 Business Recommendations")

# Avoid error if no data
if len(filtered_df) > 0:

    country_risk = filtered_df.groupby("Geography")["Exited"].mean().sort_values(ascending=False)
    top_country = country_risk.index[0]

    st.write(f"🌍 Highest churn country (within selection): **{top_country}**")
    st.write(f"📊 Churn Rate: {country_risk.max()*100:.2f}%")

    # Dynamic recommendation
    if top_country == "Germany":
        st.write("👉 Improve engagement & retention campaigns")
    elif top_country == "France":
        st.write("👉 Offer loyalty rewards & credit benefits")
    elif top_country == "Spain":
        st.write("👉 Improve digital banking experience")

    st.write("""
    ### 📌 Suggested Actions:
    - Increase customer engagement  
    - Provide personalized offers  
    - Improve customer support  
    - Focus on high-risk customers  
    """)

else:
    st.warning("No data available for recommendations")
# ---------------- ADVANCED KPI ----------------
st.markdown("## 📌 Advanced KPIs")

temp_df = filtered_df.copy()
temp_df["MPI"] = temp_df["NumOfProducts"] / temp_df["NumOfProducts"].max()

st.dataframe(temp_df[["CustomerId", "MPI"]].head())

smpi = filtered_df.groupby("Geography")["Exited"].mean() * 100
st.bar_chart(smpi)

# ---------------- DOWNLOAD FILTERED ----------------
st.markdown("## 📄 Download Filtered Data")

st.download_button(
    "Download Filtered Data",
    filtered_df.to_csv(index=False),
    "filtered_data.csv"
)