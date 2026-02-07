import pandas as pd
from sqlalchemy import create_engine, text
import streamlit as st

#==================Database connection function==================

engine = create_engine("postgresql+psycopg2://postgres:2829@localhost:5432/phonepe",
                       isolation_level="AUTOCOMMIT")
#To execute INSERT, DROP, DELETE and CREATE commands
def execute_query(sql : str):
    with engine.connect() as conn:
        conn.execute(text(sql))
        
#Execute and retrieve the query result
def run_query(sql: str):
    with engine.connect() as conn:
        return pd.read_sql(text(sql), conn)
    

#==============CREATING TABLES AND INSERTING ROWS INTO TABLES=======================

#===========AGG TRANSACTION TABLE==================

execute_query("DROP TABLE IF EXISTS agg_transaction")

execute_query("""
CREATE TABLE agg_transaction(
                 state TEXT,
                 year INT,
                 quarter INT,
                 transaction_type TEXT,
                 transaction_count BIGINT,
                 transaction_amount DOUBLE PRECISION)
              """)


df = pd.read_csv("agg_transaction.csv")
df.columns = df.columns.str.lower()

df.to_sql(  
    "agg_transaction",
    engine,
    if_exists="append",
    index=False
)
print("\n 1. Succesfully inserted the csv data into agg_transaction table")
print(f"\n Total rows reflected :{len(df)} ")


#=============AGG INSURANCE====================

execute_query("DROP TABLE IF EXISTS agg_insurance")


execute_query("""

CREATE TABLE agg_insurance
              (state TEXT,
              year INT,
              quarter INT,
              insurance_type TEXT,
              insurance_count BIGINT,
              insurance_amount DOUBLE PRECISION)
              """)

df1 = pd.read_csv("agg_insurance.csv")
df1 = df1.rename(columns={"State" : "state", "Year" : "year", "Quarter" : "quarter", "name" : "insurance_type",
                          "Count" : "insurance_count","Amount" : "insurance_amount"})

df1.to_sql(
    "agg_insurance",
    engine,
    if_exists="append",
    index=False
)

print("\n 2. Successfully inserted data into agg_insurance table")
print(f"\n Total rows reflected :{len(df1)} ")

#========================AGG USERS=======================

execute_query("DROP TABLE IF EXISTS agg_users")

execute_query("""
CREATE TABLE agg_users(
              state TEXT,
              year INT,
              quarter INT,
              registered_users INT,
              brand TEXT,
              count INT,
              percentage DOUBLE PRECISION)
""")

df3 = pd.read_csv("agg_users.csv")
df3 = df3.rename(columns={"State" : "state", "Year" : "year", "Quarter" : "quarter",
                          "registeredUsers" : "registered_users", "Brand" : "brand",
                          "Count" : "count","Percentage" : "percentage"})

df3.to_sql(
    name = "agg_users",
    con = engine,
    if_exists="append",
    index=False
)

if not df.empty:
    print("\n 3. Successfully inserted data into agg_users table")
    print(f"\n Total rows reflected :{len(df3)} ")

else:
    print("No data to insert or data is empty.")


#===================Top TRANSACTION=====================

execute_query("DROP TABLE IF EXISTS top_transaction")

execute_query("""
CREATE TABLE top_transaction(
              state TEXT,
              year INT,
              quarter INT,
              level TEXT,
              entity_name TEXT,
              type TEXT,
              count BIGINT,
              amount DOUBLE PRECISION)
""")

df4 = pd.read_csv("top_transaction.csv")
df4 = df4.rename(columns={"State": "state","Year" : "year",
                          "Quarter" : "quarter", "Level": "level",
                          "EntityName": "entity_name","Type": "type",
                          "Count" : "count", "Amount": "amount"})
df4.to_sql(
    name="top_transaction",
    con=engine,
    if_exists="append",
    index=False
)

if not df4.empty:
    print("\n 4. Successfully loaded date into top_transaction table")
    print(f"\n Total rows reflected :{len(df4)} ")

else: 
    print("No data to insert or data is empty.")


#================TOP INSURANCE================

execute_query("DROP TABLE IF EXISTS top_insurance")

execute_query("""
CREATE TABLE top_insurance(
              state TEXT,
              year INT,
              quarter INT,
              level TEXT,
              entity_name TEXT,
              type TEXT,
              count BIGINT,
              amount DOUBLE PRECISION)
""")

df5 = pd.read_csv("top_insurance.csv")
df5 = df5.rename(columns={"State": "state","Year" : "year",
                          "Quarter" : "quarter", "Level": "level",
                          "EntityName": "entity_name","Type": "type",
                          "Count" : "count", "Amount": "amount"})

df5.to_sql(
    name="top_insurance",
    con=engine,
    if_exists="append",
    index=False
)

if df5.empty:
    print("\n Error loading data")

else:
    print("\n 5. Successfully loaded data into top_insurance table")
    print(f"\n Total rows reflected : {len(df5)} ")


#================TOP USERS===================

execute_query("DROP TABLE IF EXISTS top_users")

execute_query("""
CREATE TABLE top_users(
              state TEXT,
              year INT,
              quarter INT,
              level TEXT,
              district TEXT,
              registered_users BIGINT)
""")

df6 = pd.read_csv("top_users.csv")
df6 = df6.rename(columns={"State": "state","Year" : "year",
                          "Quarter" : "quarter", "Level": "level",
                          "Name": "district", "RegisteredUsers": "registered_users"})

df6.to_sql(
    name="top_users",
    con=engine,
    if_exists="append",
    index=False
)

if df6.empty:
    print("\n Error loading data into tables")

else:
    print("\n 6. Successfully inserted data into top_users table")
    print(f"\n Total rows reflected : {len(df6)} ")


#===============MAP TRANSACTION==================

execute_query("DROP TABLE IF EXISTS map_transaction")

execute_query("""
CREATE TABLE map_transaction(
              state TEXT,
              year INT,
              quarter INT,
              districts TEXT,
              type TEXT,
              count BIGINT,
              amount DOUBLE PRECISION)
""")

df7 = pd.read_csv("map_transaction.csv")
df7 = df7.rename(columns={"State": "state","Year" : "year",
                          "Quarter" : "quarter", "Districts": "districts",
                          "Type": "type", "Count": "count", "Amount": "amount"})

df7.to_sql(
    name="map_transaction",
    con=engine,
    if_exists="append",
    index=False
)

if df7.empty:
    print("\n Error loading data into tables")

else:
    print("\n 7. Successfully loaded data into map_transaction table")
    print(f"\n Total rows reflected: {len(df7)}")

# ============ MAP INSURANCE ==============

execute_query("DROP TABLE IF EXISTS map_insurance")

execute_query("""
CREATE TABLE map_insurance(
              state TEXT,
              year INT,
              quarter INT,
              latitude TEXT,
              longitude TEXT,
              metric TEXT,
              districts TEXT)
""")

df8 = pd.read_csv("map_insurance.csv", dtype=str)
df8 = df8.rename(columns={"State": "state", "Year": "year",
                          "Quarter": "quarter", "Latitude": "latitude",
                          "Longitude": "longitude", "Metric": "metric",
                          "Districts": "districts"})
df8['year'] = df8['year'].astype(int)
df8['quarter'] = df8['quarter'].astype(int)

df8.to_sql(
    name="map_insurance",
    con=engine,
    if_exists="append",
    index=False
)

if df8.empty:
    print("\n Error loading data into table")
else:
    print("\n 8. Successfully loaded data into map_insurance table")
    print(f"\n Total rows reflected: {len(df8)}")

#===============MAP USERS==================

execute_query("DROP TABLE IF EXISTS map_users")

execute_query("""
CREATE TABLE map_users(
              state TEXT,
              year INT,
              quarter INT,
              districts TEXT,
              registered_users BIGINT,
              app_opens BIGINT)
""")

df9 = pd.read_csv("map_users.csv")
df9 = df9.rename(columns={"State": "state", "Year": "year",
                          "Quarter": "quarter","Districts": "districts", 
                          "RegisteredUsers": "registered_users", "appOpens": "app_opens"})

df9.to_sql(
    name="map_users",
    con=engine,
    if_exists="append",
    index=False
)

if df9.empty:
    print("\n Error loading data into table")
else:
    print("\n 9. Successfully loaded data into map_users table")
    print(f"\n Total rows reflected: {len(df9)}")


