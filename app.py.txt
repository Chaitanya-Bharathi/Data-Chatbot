import streamlit as st
import pandas as pd
import mysql.connector
import sys
import os

st.set_page_config(page_title="AI-Powered SQL & Excel Data Chatbot with MySQL")

st.title("🤖 AI-Powered SQL & Excel Data Chatbot with MySQL")
st.write("Upload your Excel/CSV file or connect to a MySQL database, then ask questions!")

uploaded_file = st.file_uploader("Upload Excel or CSV", type=['csv', 'xlsx'])

df = None
if uploaded_file:
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    st.success("Data loaded successfully!")
    st.write(df.head())


st.subheader("🔗 Connect to MySQL Database")
mysql_host = st.text_input("MySQL Host", value="localhost")
mysql_user = st.text_input("MySQL User", value="root")
mysql_password = st.text_input("MySQL Password", type="password")
mysql_database = st.text_input("MySQL Database Name")
connect_button = st.button("Connect to MySQL")

conn = None
cursor = None
if connect_button:
    try:
        conn = mysql.connector.connect(
            host=mysql_host,
            user=mysql_user,
            password=mysql_password,
            database=mysql_database
        )
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()
        st.success("Connected to MySQL successfully!")
        st.write("Tables available in DB:")
        st.write(tables)
    except Exception as e:
        st.error(f"Error connecting to MySQL: {e}")


if df is not None:
    st.subheader("🧹 Dataset Cleaning Options")

    if st.checkbox("Show Missing Values Count"):
        st.write(df.isnull().sum())

    if st.checkbox("Fill Missing Values"):
        fill_value = st.text_input("Value to replace missing values with:")
        if st.button("Fill Now"):
            df = df.fillna(fill_value)
            st.success("Missing values filled.")
            st.write(df.head())

    if st.checkbox("Remove Duplicates"):
        if st.button("Remove Duplicates Now"):
            df = df.drop_duplicates()
            st.success("Duplicates removed.")
            st.write(df.head())

    if st.checkbox("Show Summary Statistics"):
        st.write(df.describe())


user_question = st.text_input("❓ Ask your question about the data:")

def query_openai(question, context):
    prompt = f"""
You are a data analyst helping with data analysis.

Dataset preview/context: 
{context}

User Question: 
{question}

Provide SQL queries or Pandas code to answer the question based on context. Also, briefly explain.
"""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You help users analyze datasets with SQL or Pandas."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )
    return response['choices'][0]['message']['content']

if st.button("Get Answer") and user_question:
    if df is not None:
        context = df.head().to_string()
        result = query_openai(user_question, context)
        st.markdown("### 💬 Answer:")
        st.code(result)

    elif conn is not None and cursor is not None:
        cursor.execute("SHOW TABLES;")
        context = "Available tables:\n" + "\n".join([str(table[0]) for table in cursor.fetchall()])
        result = query_openai(user_question, context)
        st.markdown("### 💬 Answer:")
        st.code(result)

    else:
        st.warning("Please upload a file or connect to a database first.")
