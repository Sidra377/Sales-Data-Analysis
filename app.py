import streamlit as st
import pandas as pd
import plotly.express as px
from websockets import Data

st.set_page_config(page_title="Sales Dashboard", layout="wide")

st.title("Sales Data Analysis Dashboard")
st.write("Electronics Store Sales Data Analysis - 2019")

@st.cache_data
def load_data():
    data = pd.read_csv("Sales Data.csv", header=None, names=["Sr", "Order ID", "Product", "Quantity", "Price", "Order Date", "Purchase Address", "Month", "Sales", "City", "Extra" ])
    data.columns = data.columns.str.strip()
    return data

df = load_data()
st.write(df.head())

df = df.drop(columns="Unnamed: 0", errors="ignore")
st.write(df.columns)

st.write(df.isnull().sum())

df = df.dropna()
st.write(df.shape)

df["Order Date"] = pd.to_datetime(df["Order Date"])
st.write(df.dtypes)

st.write(df.duplicated().sum())

st.write(df[df.duplicated(keep=False)].sort_values("Order ID").head(6))

df = df.drop_duplicates()
st.write(df.shape)

st.write(df["Order Date"].min())
st.write(df["Order Date"].max())
st.write("Rows in 2019:", (df["Order Date"].dt.year == 2019).sum())
st.write("Rows in 2020:", (df["Order Date"].dt.year == 2020).sum())

df = df[df["Order Date"].dt.year == 2019]
st.write(df.shape)

fig = px.histogram(df, x="Quantity", title="Quantity ordered in one row")
st.plotly_chart(fig)

df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")
df["Price"] = pd.to_numeric(df["Price"], errors="coerce")
df = df.dropna(subset=["Quantity", "Price"])
st.write(df[df["Quantity"] >= 7]["Product"].value_counts())

df["Sales"] = df["Quantity"] * df["Price"]
fig = px.box(df, y="Sales", title="Sales per row")
st.plotly_chart(fig)


q1 = df["Sales"].quantile(0.25)
q3 = df["Sales"].quantile(0.75)
upper = q3 + 1.5 * (q3 - q1)

outliers = df[df["Sales"] > upper]
st.write("Upper limit:", upper, "| Outlier rows:", len(outliers))
st.write(outliers["Product"].value_counts())

df["Month"] = df["Order Date"].dt.month_name()
df["Hour"] = df["Order Date"].dt.hour

parts = df["Purchase Address"].str.split(",")
df["City"] = parts.str[1].str.strip() + " (" + parts.str[2].str.strip().str[:2] + ")"

months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
monthly = df.groupby("Month")["Sales"].sum().reindex(months).reset_index()

fig1 = px.bar(monthly, x="Month", y="Sales", title="Sales per month")
st.plotly_chart(fig1)
city_sales = df.groupby("City")["Sales"].sum().sort_values().reset_index()

fig2 = px.bar(city_sales, x="Sales", y="City", orientation="h", title="Sales per city")
st.plotly_chart(fig2)

hourly = df.groupby("Hour")["Sales"].sum().reset_index()

fig3 = px.line(hourly, x="Hour", y="Sales", markers=True, title="Sales by hour of the day")
st.plotly_chart(fig3)

product_sales = df.groupby("Product")["Sales"].sum().sort_values().reset_index()

fig4 = px.bar(product_sales, x="Sales", y="Product", orientation="h", height=550, title="Sales per product")
st.plotly_chart(fig4)

st.write(df.groupby("Product")["Quantity"].sum().sort_values(ascending=False).head(5))

orders = df.groupby("Order ID")["Sales"].sum().reset_index()

fig5 = px.histogram(orders, x="Sales", nbins=50, title="Total money in one order")
st.plotly_chart(fig5)

st.write("Typical order (median):", orders["Sales"].median())
st.write("Average order (mean):", round(orders["Sales"].mean(), 2))

