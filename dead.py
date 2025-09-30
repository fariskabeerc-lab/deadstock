import streamlit as st
import pandas as pd
import plotly.express as px

# --- Load Multiple Excel Files ---
files = ["dead_stock1.xlsx", "dead_stock2.xlsx", "dead_stock3.xlsx"]  # update file names
dfs = [pd.read_excel(f) for f in files]
df = pd.concat(dfs, ignore_index=True)

# --- Clean column names ---
df.columns = df.columns.str.strip()

# --- Ensure numeric fields ---
numeric_cols = ["Stock Value", "Stock", "Profit", "Margin%", "Total Sales", "Cost", "Selling", "LP Price"]
for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

# --- Handle negative stock for plotting ---
df["Stock_clean"] = df["Stock"].clip(lower=0)

# --- Dashboard Layout ---
st.set_page_config(page_title="Dead Stock Dashboard", layout="wide")
st.title("📊 Safa Oud Metha Dead Stock Dashboard (Zero Sales and LP before 2025)")

# --- Category Filter ---
if "Category" in df.columns:
    categories = ["All"] + sorted(df["Category"].dropna().unique().tolist())
    selected_category = st.sidebar.selectbox("Select Category", categories)
    if selected_category != "All":
        df_filtered = df[df["Category"] == selected_category]
    else:
        df_filtered = df.copy()
else:
    df_filtered = df.copy()

# --- KPIs at Top ---
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Dead Stock Items", f"{len(df_filtered):,}")
col2.metric("Total Stock Qty", f"{df_filtered['Stock'].sum():,.0f}")
col3.metric("Total Stock Value", f"{df_filtered['Stock Value'].sum():,.2f}")

# --- High Priority Items (Top 10 by Stock Value) ---
st.subheader("🚨 High Priority Items (Top 10 by Stock Value)")
high_priority = df_filtered.nlargest(10, "Stock Value")
priority_cols = [c for c in ["Item Bar Code","Item Name","Stock","Stock Value","Margin%","Profit",
                             "Cost","Selling","LP Price","LP Date","LP Supplier"] if c in df.columns]
st.table(high_priority[priority_cols])

# --- Top Items by Stock Value (Horizontal Bar Chart) ---
st.subheader("Top 20 Items by Stock Value")
top_items = df_filtered.nlargest(20, "Stock Value")
fig1 = px.bar(
    top_items, y="Item Name", x="Stock Value", orientation="h",
    text="Stock Value", color="Stock Value", color_continuous_scale="Reds",
    hover_data={col: True for col in priority_cols}
)
fig1.update_layout(yaxis={'categoryorder':'total ascending'}, height=600)
st.plotly_chart(fig1, use_container_width=True)

# --- Pie Chart: Category-wise Stock Value ---
st.subheader("Stock Value by Category")
if "Category" in df.columns:
    category_df = df_filtered.groupby("Category")["Stock Value"].sum().reset_index()
    fig2 = px.pie(
        category_df, values="Stock Value", names="Category",
        hover_data={"Stock Value": True},
        color_discrete_sequence=px.colors.sequential.Reds
    )
    fig2.update_traces(textinfo="percent+label")
    st.plotly_chart(fig2, use_container_width=True)

# --- Detailed Data Table (Full Details) ---
st.subheader("Detailed Dead Stock Items (Full Details)")
detailed_cols = [c for c in ["Item Bar Code","Item Name","Item No","Stock","Stock Value","Margin%","Profit",
                             "Cost","Selling","LP Price","LP Date","LP Supplier","CF","Unit","Category","Pre Return"] 
                 if c in df.columns]
st.dataframe(df_filtered[detailed_cols], height=400)

# --- Download Option ---
csv = df_filtered[detailed_cols].to_csv(index=False).encode('utf-8')
st.download_button("📥 Download Filtered Dead Stock Data", csv, "dead_stock_filtered.csv", "text/csv")
