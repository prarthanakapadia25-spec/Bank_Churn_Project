import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt

def show_eda(df):

    st.write("### Churn Distribution")
    st.bar_chart(df["Exited"].value_counts())

    st.write("### Correlation Heatmap")
    fig, ax = plt.subplots()
    sns.heatmap(df.corr(), annot=True, cmap="coolwarm", ax=ax)
    st.pyplot(fig)

    st.write("### Age vs Churn")
    fig2, ax2 = plt.subplots()
    sns.boxplot(x="Exited", y="Age", data=df, ax=ax2)
    st.pyplot(fig2)

    st.write("### Balance vs Churn")
    fig3, ax3 = plt.subplots()
    sns.boxplot(x="Exited", y="Balance", data=df, ax=ax3)
    st.pyplot(fig3)