import streamlit as st

def show_kpis(df):

    total_customers = len(df)
    churn_rate = df["Exited"].mean() * 100
    active_users = df["IsActiveMember"].sum()
    avg_balance = df["Balance"].mean()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Customers", total_customers)
    col2.metric("Churn Rate (%)", f"{churn_rate:.2f}")
    col3.metric("Active Users", active_users)
    col4.metric("Avg Balance", f"{avg_balance:.2f}")

    # MPI
    st.write("### Market Penetration Index (MPI)")
    df["MPI"] = (df["NumOfProducts"] / total_customers) * 100
    st.bar_chart(df["MPI"].head(20))

    # SMPI
    st.write("### State-wise Market Penetration Index (SMPI)")
    smpi = df.groupby("Geography")["NumOfProducts"].mean()
    st.bar_chart(smpi)

    # UPSI
    st.write("### User Product Strength Index (UPSI)")
    df["UPSI"] = (df["NumOfProducts"] * df["IsActiveMember"]) / df["Age"]
    st.line_chart(df["UPSI"].head(50))