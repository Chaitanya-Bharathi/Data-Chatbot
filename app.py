import streamlit as st
import pandas as pd
import mysql.connector
import re

st.set_page_config(page_title="Excel & MySQL Data Chatbot", layout="wide")
st.title("📊 Data Chatbot (Excel + MySQL)")

option = st.radio("Select Data Source:", ["Upload Excel", "Connect MySQL"])

df = None

if option == "Upload Excel":
    uploaded_file = st.file_uploader("Upload Excel file (.xlsx only)", type=["xlsx"])
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        st.success("Excel file loaded successfully!")
        st.dataframe(df, use_container_width=True)

elif option == "Connect MySQL":
    st.subheader("MySQL Connection Details")
    host = st.text_input("MySQL Host", value="localhost")
    user = st.text_input("MySQL User", value="root")
    password = st.text_input("MySQL Password", type="password")
    database = st.text_input("MySQL Database")

    if st.button("Connect to MySQL"):
        try:
            conn = mysql.connector.connect(
                host=host, user=user, password=password, database=database
            )
            cursor = conn.cursor()
            cursor.execute("SHOW TABLES;")
            tables = [table[0] for table in cursor.fetchall()]
            st.success("Connected successfully!")
            table = st.selectbox("Select a Table", tables)
            if st.button("Load Table"):
                df = pd.read_sql(f"SELECT * FROM {table}", conn)
                st.dataframe(df, use_container_width=True)
            conn.close()
        except Exception as e:
            st.error(f"MySQL Connection Failed: {e}")

if df is not None:
    st.subheader("📊 Dataset Summary & Exploration")

    if st.checkbox("Show Summary Statistics"):
        st.write(df.describe())

    st.subheader("🔎 Filter Data by Column")
    column = st.selectbox("Choose Column to Filter", df.columns)
    unique_vals = df[column].dropna().unique()
    selected_val = st.selectbox("Choose Value", unique_vals)
    st.dataframe(df[df[column] == selected_val], use_container_width=True)

    st.subheader("Group & Aggregate Data")
    group_col = st.selectbox("Group by Column", df.columns)
    agg_func = st.selectbox("Aggregation", ["count", "sum", "mean"])

    if st.button("Generate Aggregation"):
        if agg_func == "count":
            result = df.groupby(group_col).count()
        elif agg_func == "sum":
            result = df.groupby(group_col).sum(numeric_only=True)
        elif agg_func == "mean":
            result = df.groupby(group_col).mean(numeric_only=True)
        st.dataframe(result, use_container_width=True)

    st.subheader("Ask a Question about the Data")
    question = st.text_input("Type your question here")

    def get_column(q):
        for col in df.columns:
            if col.lower() in q.lower():
                return col
        return None

    def process_question(q):
        q = q.lower()
        col = get_column(q)
        if ("total" in q or "sum" in q) and col:
            return f"Total of {col}: {df[col].sum(numeric_only=True)}"
        elif ("average" in q or "mean" in q) and col:
            return f"Average of {col}: {df[col].mean(numeric_only=True)}"
        elif ("maximum" in q or "max" in q) and col:
            return f"Maximum of {col}: {df[col].max()}"
        elif ("minimum" in q or "min" in q) and col:
            return f"Minimum of {col}: {df[col].min()}"
        elif "unique" in q and col:
            return f"Unique values in {col}: {df[col].unique()}"
        elif "number of rows" in q:
            return f"Number of rows: {len(df)}"
        elif "columns" in q or "column names" in q:
            return f"Columns: {list(df.columns)}"
        elif "describe" in q or "summary" in q:
            return df.describe()
        elif "show data where" in q:
            pattern = r"show data where (.+?) is (.+)"
            match = re.search(pattern, q)
            if match:
                col_name = match.group(1).strip()
                value = match.group(2).strip()
                if col_name in df.columns:
                    return df[df[col_name] == value]
                else:
                    return f"Column '{col_name}' not found."
        elif "shape" in q:
            return f"Shape of dataset: {df.shape}"
        elif "first" in q and "rows" in q:
            return df.head()
        elif "last" in q and "rows" in q:
            return df.tail()
        else:
            return "❗ I don’t understand that yet. Try: total, average, unique, columns, show data where..."

    if question:
        result = process_question(question)
        if isinstance(result, pd.DataFrame):
            st.dataframe(result, use_container_width=True)
        else:
            st.write(result)

