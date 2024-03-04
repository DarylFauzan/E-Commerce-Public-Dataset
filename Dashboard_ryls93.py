# Import packages
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# import data
df = pd.read_csv("E-Commerce Merge.csv")

# Mengubah kolom menjadi datetime
datetime_columns = ['order_approved_at']

# Turn data to datetime type
for column in datetime_columns:
    df[column] = pd.to_datetime(df[column])

# Create function to create a certain dataframe
def create_trend(df):
    # create trend dataframe
    trend = df[["order_approved_at", "price"]][(df["order_status"] != "canceled") & 
                                                   (df["order_status"] != "unavailable")].groupby("order_approved_at").sum().reset_index()
    
    # Create a year-month datetime
    trend["order_approved_at"] = trend["order_approved_at"].dt.date
    trend = trend.groupby("order_approved_at").sum().reset_index()
    
    #rename column
    trend.rename(columns = {"price": "Revenue",
                            "order_approved_at" : "date"}, inplace = True)
    
    return trend
    
def create_top_revenue_product(df):
    # create revenue per category dataframe
    revenue_per_category = df[(df["order_status"]!= "canceled") & 
                            (df["order_status"]!= "unavailable")]\
                            [["product_category_name_english", "price"]].groupby("product_category_name_english").sum().reset_index()
    
    # rename column
    revenue_per_category.rename(columns = {"price": "Revenue",
                                           "product_category_name_english": "Category"}, inplace = True)
    
    #sort the data
    revenue_per_category.sort_values(by = "Revenue", ascending = False, inplace = True)

    return revenue_per_category

def create_top_item_product(df):
    # create revenue per category dataframe
    item_per_category = df[(df["order_status"]!= "canceled") & 
                            (df["order_status"]!= "unavailable")]\
                            [["product_category_name_english", "order_id"]].groupby("product_category_name_english").count().reset_index()
    
    # rename column
    item_per_category.rename(columns = {"order_id": "Number of Order",
                                           "product_category_name_english": "Category"}, inplace = True)
    
    #sort the data
    item_per_category.sort_values(by = "Number of Order", ascending = False, inplace = True)
    
    return item_per_category

def create_top_buyer_city(df):
    # Create dataframe
    buyer_per_city = df[(df["order_status"]!= "canceled") & 
                        (df["order_status"]!= "unavailable")]\
                        [["customer_city", "order_id"]].groupby("customer_city").nunique().reset_index()
    
    # rename columns
    buyer_per_city.rename(columns = {"customer_city": "City", "order_id": "Number of Order"}, inplace = True)
    
    #sort values
    buyer_per_city.sort_values(by = "Number of Order", ascending = False, inplace = True)
    
    return buyer_per_city

def create_status(df):
    # Create dataframe and change values to "others", except "delivered"
    stat = df["order_status"].map({"delivered": "delivered", "invoiced" : "others",
                                   "shipped": "others", "processing": "others",
                                   "unavailable": "others", "canceled": "others",
                                   "created": "others", "approved": "others"}).value_counts()
    return stat

def create_pay_method(df):
    pay_method = df["payment_type"].value_counts()
    return pay_method

min_date = df["order_approved_at"].min()
max_date = df["order_approved_at"].max()

# Create sidebar
with st.sidebar:
    st.subheader("Muhammad Daryl Fauzan")
    st.subheader("M001D4KY2857")
    # Add Profile Picture
    st.image("foto linkedin deril.png")

    # Add date filter
    start_date, end_date = st.date_input(
    label='Rentang Waktu',min_value=min_date,
    max_value=max_date,
    value=[min_date, max_date])

    # Add city filter
    city = st.multiselect(
        label = "Select City",
        options = df["customer_city"].unique()
    )

    # Add product category filter
    category = st.multiselect(
        label = "Select Product",
        options = df["product_category_name_english"].unique()
    )

    # Create a main data frame that effected by filters
    main_df = df[(df["order_approved_at"].dt.date >= start_date) & 
                (df["order_approved_at"].dt.date <= end_date)]

    if city:
        main_df = main_df[main_df["customer_city"].isin(city)]

    if category:
        main_df = main_df[main_df["customer_city"].isin(category)]

# Create pivot table for charts
trend = create_trend(main_df)
revenue_per_category = create_top_revenue_product(main_df)
item_per_category = create_top_item_product(main_df)
buyer_per_city = create_top_buyer_city(main_df)
status = create_status(main_df)
pay_method = create_pay_method(main_df)

# Create Header
st.header("E-Commerce Analysis Dashboard")

# Create 2 columns for scorecard
col1, col2 = st.columns(2)

with col1:
    total_sold_items = item_per_category["Number of Order"].sum()
    st.metric("Total Sold Items", f"{total_sold_items}")

with col2:
    total_revenue = revenue_per_category["Revenue"].sum()
    st.metric("Total Revenue", f"${total_revenue/1000:.2f}")

# Create revenue trend
st.subheader("Revenue Trend")

# Create figure and axes
fig, ax = plt.subplots()

# Create lineplot
sns.lineplot(data = trend, x = "date", y = "Revenue")

# Create label
ax.set_ylabel("")
ax.set_xlabel("")

plt.xticks(rotation = 45)
sns.despine()

plt.show()
st.pyplot(fig)

# Create top and bottom product revenue
st.subheader("Revenue per Product Category")

# Create figure and axes
fig, ax = plt.subplots(ncols = 2)

# Create barplot for top product
sns.barplot(data = revenue_per_category.head(10), y = "Category", x = "Revenue", width = 0.5, ax = ax[0])
ax[0].set_title("Top 10 Products", fontweight = "bold", fontsize = 12)
ax[0].set_xlabel("")
sns.despine(ax = ax[0])

# Create barplot for top product
sns.barplot(data = revenue_per_category.tail(10), y = "Category", x = "Revenue", width = 0.5, ax = ax[1])
ax[1].set_title("Bottom 10 Products", fontweight = "bold", fontsize = 12)
ax[1].set_xlabel("")
sns.despine(ax = ax[1])

fig.tight_layout()

plt.show()
st.pyplot(fig)

# Create top and bottom product orders
st.subheader("Number of Order per Product Category")

# Create figure and axes
fig, ax = plt.subplots(ncols = 2)

# Create barplot for top product
sns.barplot(data = item_per_category.head(10), y = "Category", x = "Number of Order", width = 0.5, ax = ax[0])
ax[0].set_title("Top 10 Products", fontweight = "bold", fontsize = 12)
ax[0].set_xlabel("")
sns.despine(ax = ax[0])

# Create barplot for top product
sns.barplot(data = item_per_category.tail(10), y = "Category", x = "Number of Order", width = 0.5, ax = ax[1])
ax[1].set_title("Bottom 10 Products", fontweight = "bold", fontsize = 12)
ax[1].set_xlabel("")
sns.despine(ax = ax[1])

fig.tight_layout()

plt.show()
st.pyplot(fig)

# Create Number of Buyers per City
st.subheader("Number of Buyers per City")

# Create figure and axes
fig, ax = plt.subplots(ncols = 2)

# Create barplot for top product
sns.barplot(data = buyer_per_city.head(10), y = "City", x = "Number of Order", width = 0.5, ax = ax[0])
ax[0].set_title("Top 10 Cities", fontweight = "bold", fontsize = 12)
ax[0].set_xlabel("")
sns.despine(ax = ax[0])

# Create barplot for top product
sns.barplot(data = buyer_per_city.tail(10), y = "City", x = "Number of Order", width = 0.5, ax = ax[1])
ax[1].set_title("Bottom 10 Cities", fontweight = "bold", fontsize = 12)
ax[1].set_xlim((0,10))
ax[1].set_xlabel("")
sns.despine(ax = ax[1])

fig.tight_layout()

plt.show()
st.pyplot(fig)

# Create order status and payment method proportions
col3, col4 = st.columns(2)

with col3:
    st.subheader("% Delivered")
    # create figure and axes
    fig, ax = plt.subplots(figsize = (5,5))
    # create pie chart
    ax.pie(status, wedgeprops = {"width": 0.4}, startangle = 90)
    ax.set_title("% Delivered", fontweight = "bold", fontsize = 14)
    
    ax.legend(status.index)
    # Add text in the middle
    if "delivered" in status.index:
        delivered_percent = status["delivered"]/status.sum()
    else:
        delivered_percent = 0
    
    # Add text at the center
    plt.text(0, 0, f"{delivered_percent*100:.2f}%", fontsize=24, color='black', fontweight = "bold", ha='center', va='center')
    
    # Add text at the bottom
    plt.text(0, -1.2, 'Delivered', fontsize=20, ha='center')
    
    plt.show()
    st.pyplot(fig)

with col4:
    st.subheader("Payment Method")
    # create figure and axes
    fig, ax = plt.subplots(figsize = (5,5))
    
    # create pie chart
    ax.pie(pay_method, wedgeprops = {"width": 0.5}, startangle = 90,
          textprops = {"fontweight" : "bold"})
    
    ax.legend(pay_method.index)
    
    plt.show()
    st.pyplot(fig)

