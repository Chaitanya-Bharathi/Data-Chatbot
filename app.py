import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Excel Data Chatbot", layout="wide")
st.title("📊 Excel Data Chatbot (CSV/XLSX)")

uploaded_file = st.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx"])

df = None
if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    st.success("File loaded successfully!")
    st.dataframe(df, use_container_width=True)

if df is not None:
    st.subheader("📌 Summary Statistics & Cleaning")

    if st.checkbox("Show Summary Statistics"):
        st.write(df.describe())

    if st.checkbox("Show Missing Values"):
        st.write(df.isnull().sum())

    if st.checkbox("Remove Duplicates"):
        df = df.drop_duplicates()
        st.success("Duplicates removed!")
        st.dataframe(df, use_container_width=True)

    st.subheader("🔎 Filter Data by Column")
    column = st.selectbox("Choose Column to Filter", df.columns)
    unique_vals = df[column].dropna().unique()
    selected_val = st.selectbox("Choose Value", unique_vals)
    st.dataframe(df[df[column] == selected_val], use_container_width=True)

    st.subheader("📊 Group & Aggregate")
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

    st.subheader("❓ Ask a Question about the Data")
    question = st.text_input("Type your question")

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
        elif "number of rows" in q or "Number of rows" in q:
            return f"Number of rows: {len(df)}"
        elif "number of columns" in q or "column names" in q or "Number of columns" :
            return f"Columns: {list(df.columns)}"
        elif "describe" in q or "summary" in q:
            return df.describe()
        elif "show data where" in q.lower():
            q=q.strip().r.strip(".")
            pattern = r"show data where (.+?) is (.+)"
            match = re.search(pattern, q,re.IGNORECASE)
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
