import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import duckdb

# Load Raw Data
customer_df = pd.read_parquet("customer.parquet")
campaign_df = pd.read_parquet("campaign.parquet")
result_df = customer_df.merge(campaign_df, on="customer_id")
result_df['deposit'] = result_df['deposit'].map({'yes': 1, 'no': 0})

# Sidebar
st.sidebar.title("📊 Dashboard Navigation")
page = st.sidebar.radio("Go to", ["Exploratory Data Analysis", "SQL Query Interface"])


# EDA --> analyzing and visualizing data 
if page == "Exploratory Data Analysis":
    st.title("📊 Exploratory Data Analysis")

    # Filters
    selected_job = st.sidebar.multiselect("Filter by Job", customer_df['job'].unique(), default=customer_df['job'].unique())
    age_range = st.sidebar.slider("Age Range", min_value=int(customer_df['age'].min()), max_value=int(customer_df['age'].max()), value=(25, 60))

    st.subheader("1. Customers with Loan or Housing")
    fig1, ax1 = plt.subplots()
    customer_df['has_loan_or_housing'].value_counts().plot(kind='bar', color=['green', 'red'], ax=ax1)
    ax1.set_title("Customers with Loan or Housing")
    ax1.set_xlabel("Has Loan or Housing (0 = No, 1 = Yes)")
    ax1.set_ylabel("Number of Customers")
    ax1.set_xticks([0, 1])
    ax1.set_xticklabels(['No', 'Yes'], rotation=0)
    st.pyplot(fig1)

    st.subheader("2. Age vs Deposit")
    filtered_df = result_df[result_df['job'].isin(selected_job)]
    filtered_df = filtered_df[(filtered_df['age'] >= age_range[0]) & (filtered_df['age'] <= age_range[1])]
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    sns.histplot(data=filtered_df, x='age', hue='deposit', multiple='stack', palette='Set2', bins=20, ax=ax2)
    ax2.set_title("Age Distribution vs Deposit Outcome")
    ax2.set_xlabel("Age")
    ax2.set_ylabel("Count")
    st.pyplot(fig2)

    st.subheader("3. Call Duration by Deposit")
    fig3, ax3 = plt.subplots(figsize=(10, 6))
    sns.histplot(data=filtered_df, x='duration', hue='deposit', multiple='stack', bins=30, palette="Set2", ax=ax3)
    ax3.set_title("Call Duration Distribution by Deposit Outcome")
    ax3.set_xlabel("Duration")
    ax3.set_ylabel("Count")
    ax3.grid(axis='y', linestyle='--', alpha=0.7)
    st.pyplot(fig3)

    st.subheader("4. Job vs Deposit Outcome")
    job_group = filtered_df.groupby(['job', 'deposit']).size().reset_index(name='count')
    fig4, ax4 = plt.subplots(figsize=(12, 6))
    sns.barplot(data=job_group, x='job', y='count', hue='deposit', palette='Set2', ax=ax4)
    ax4.set_title("Job Distribution and Deposit Outcome")
    ax4.set_xlabel("Job")
    ax4.set_ylabel("Count")
    ax4.set_xticklabels(ax4.get_xticklabels(), rotation=45, ha='right')
    ax4.grid(axis='y', linestyle='--', alpha=0.5)
    st.pyplot(fig4)

# SQK Query
elif page == "SQL Query Interface":
    st.title("🧮 SQL Query Interface")

    # Init DuckDB con
    con = duckdb.connect()
    con.execute("INSTALL parquet; LOAD parquet;")
    con.execute("CREATE OR REPLACE VIEW customer AS SELECT * FROM read_parquet('customer.parquet');")
    con.execute("CREATE OR REPLACE VIEW campaign AS SELECT * FROM read_parquet('campaign.parquet');")

    query = st.text_area("Enter your SQL query", height=150, value="SELECT * FROM customer LIMIT 10")

    if st.button("Run Query"):
        try:
            result = con.execute(query).df()
            st.success("Query ran successfully!")
            st.dataframe(result)

            # # Download CSV
            # csv = result.to_csv(index=False).encode("utf-8")
            # st.download_button("Download as CSV", data=csv, file_name="query_result.csv", mime="text/csv")
        except Exception as e:
            st.error(f"An error occurred: {e}")
