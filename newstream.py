import streamlit as st
import pandas as pd
import plotly.express as px
import pyodbc

# ========================
# Page Config
# ========================
st.set_page_config(page_title="New Cairo Hospitals Dashboard", layout="wide")

st.title("🏥 New Cairo Hospitals Dashboard")
st.markdown("Interactive Data Visualization from SQL Server")

# ========================
# Database Connection
# ========================
def get_connection():
    return pyodbc.connect(
        "DRIVER={ODBC Driver 18 for SQL Server};"
        "SERVER=.;"
        "DATABASE=hospitals2;"
        "TrustServerCertificate=yes;"
        "Trusted_Connection=yes;"
    )

@st.cache_data
def load_data():
    conn = get_connection()
    df = pd.read_sql("SELECT TOP 40 * FROM hospitals2", conn)
    conn.close()
    return df

df = load_data()

# ========================
# Data Cleaning
# ========================
df["rating"] = pd.to_numeric(df["rating"], errors="coerce")

df[["lat","lon"]] = df["coordinates"].str.split(",", expand=True)
df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
df["lon"] = pd.to_numeric(df["lon"], errors="coerce")

# ========================
# KPIs
# ========================
col1, col2, col3 = st.columns(3)

col1.metric("Total Hospitals", len(df))
col2.metric("Average Rating", round(df["rating"].mean(),2))
col3.metric("Hospitals With Website", df["website"].notnull().sum())

st.divider()

# ========================
# Rating Distribution
# ========================
st.subheader("📊 Rating Distribution")

fig1 = px.histogram(df, x="rating", nbins=10)
st.plotly_chart(fig1, use_container_width=True)

# ========================
# Top 10 Hospitals
# ========================
st.subheader("🏆 Top 10 Hospitals")

top10 = df.sort_values(by="rating", ascending=False).head(10)

fig2 = px.bar(
    top10,
    x="rating",
    y="name",
    orientation="h"
)

st.plotly_chart(fig2, use_container_width=True)

# ========================
# Map Visualization
# ========================
st.subheader("🗺️ Hospitals Map")

map_df = df.dropna(subset=["lat","lon"])

fig3 = px.scatter_mapbox(
    map_df,
    lat="lat",
    lon="lon",
    hover_name="name",
    hover_data=["rating","address"],
    zoom=11,
    height=600
)

fig3.update_layout(mapbox_style="open-street-map")

st.plotly_chart(fig3, use_container_width=True)