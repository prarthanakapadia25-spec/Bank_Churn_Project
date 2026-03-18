import streamlit as st
import plotly.express as px

def show_animations(df):

    st.write("### Animated Bar Chart")
    fig1 = px.bar(df,
                  x="Geography",
                  y="Balance",
                  color="Geography",
                  animation_frame="Tenure")
    st.plotly_chart(fig1)

    st.write("### Animated Scatter Plot")
    fig2 = px.scatter(df,
                      x="Age",
                      y="Balance",
                      color="Exited",
                      size="EstimatedSalary",
                      animation_frame="Tenure")
    st.plotly_chart(fig2)

    st.write("### Time Series (Churn over Tenure)")
    ts = df.groupby("Tenure")["Exited"].mean()
    st.line_chart(ts)