import re
import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Finance Dashboard", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_excel("normalized.xlsx")
    if list(df.columns)[:4] != ["Datum", "Částka", "Zpráva", "Kategorie"]:
        df = df.iloc[:, :4].copy()
        df.columns = ["Datum", "Částka", "Zpráva", "Kategorie"]
    df["Datum"] = pd.to_datetime(df["Datum"], dayfirst=True, errors="coerce")
    df["Částka"] = pd.to_numeric(df["Částka"].astype(str).str.replace(",", ".", regex=False), errors="coerce")
    df["Month"] = df["Datum"].dt.to_period("M").astype(str)
    df["Merchant"] = df["Zpráva"].astype(str).str.extract(r"^Msto\s+(.*?)(?:,|$)", expand=False).fillna(df["Zpráva"].astype(str))
    df["Merchant"] = df["Merchant"].str.replace(r"\s+", " ", regex=True).str.strip()
    return df.dropna(subset=["Datum", "Částka"])

def app():
    df = load_data()
    st.title("Finance dashboard")
    st.caption("Interactive web platform app with monthly reviews, category filtering, and merchant filtering.")

    min_date = df["Datum"].min().date()
    max_date = df["Datum"].max().date()
    c1, c2, c3 = st.columns(3)
    with c1:
        start, end = st.date_input("Date range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
    with c2:
        categories = sorted(df["Kategorie"].dropna().unique().tolist())
        selected_categories = st.multiselect("Categories", categories, default=categories)
    with c3:
        merchants = sorted(df["Merchant"].dropna().unique().tolist())
        merchant_query = st.text_input("Merchant search", "")

    filtered = df[(df["Datum"].dt.date >= start) & (df["Datum"].dt.date <= end)]
    if selected_categories:
        filtered = filtered[filtered["Kategorie"].isin(selected_categories)]
    if merchant_query:
        filtered = filtered[filtered["Merchant"].str.contains(merchant_query, case=False, na=False)]

    m1, m2, m3 = st.columns(3)
    m1.metric("Transactions", f"{len(filtered):,}")
    m2.metric("Total", f"{filtered['Částka'].sum():,.2f}")
    m3.metric("Average", f"{filtered['Částka'].mean():,.2f}")

    monthly = filtered.groupby("Month", as_index=False)["Částka"].sum()
    st.plotly_chart(px.line(monthly, x="Month", y="Částka", markers=True, title="Monthly totals"), use_container_width=True)

    left, right = st.columns(2)
    with left:
        by_cat = filtered.groupby("Kategorie", as_index=False)["Částka"].sum().sort_values("Částka", ascending=False)
        st.plotly_chart(px.bar(by_cat, x="Kategorie", y="Částka", title="By category"), use_container_width=True)
    with right:
        by_mer = filtered.groupby("Merchant", as_index=False)["Částka"].sum().sort_values("Částka", ascending=False).head(20)
        st.plotly_chart(px.bar(by_mer, x="Merchant", y="Částka", title="Top merchants"), use_container_width=True)

    st.subheader("Filtered transactions")
    st.dataframe(filtered.sort_values("Datum", ascending=False), use_container_width=True, height=500)

    csv = filtered.to_csv(index=False).encode("utf-8")
    st.download_button("Download filtered CSV", data=csv, file_name="filtered_transactions.csv", mime="text/csv")

if __name__ == "__main__":
    app()
