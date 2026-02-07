import pandas as pd
from sqlalchemy import create_engine, text
import streamlit as st
import plotly.graph_objects as go
import json
import matplotlib.pyplot as plt
import seaborn as sns

pd.options.display.float_format = '{:.2f}'.format
engine = create_engine("postgresql+psycopg2://postgres:2829@localhost:5432/phonepe",
                       isolation_level="AUTOCOMMIT")

def run_query(sql:str):
    with engine.connect() as conn:
        return pd.read_sql(text(sql), conn)

# Page configuration
st.set_page_config(page_title="PhonePe Pulse", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS for dark theme
st.markdown("""
<style>
    .stApp {
        background-color: #2D1B4E;
    }
    .main-title {
        color: #FFFFFF;
        font-size: 48px;
        font-weight: bold;
        margin-bottom: 30px;
    }
    .transactions-title {
        color: #00D9FF;
        font-size: 36px;
        font-weight: bold;
        margin-bottom: 20px;
    }
    .rank-item {
        color: #FFFFFF;
        font-size: 18px;
        padding: 8px 0;
        display: flex;
        justify-content: space-between;
    }
    .rank-number {
        color: #666;
        margin-right: 15px;
    }
    .rank-value {
        color: #00D9FF;
        font-weight: bold;
    }
    /* White text for Business Use Cases page */
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown {
        color: #FFFFFF !important;
    }
    .stExpander {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# Sidebar for navigation
page = st.sidebar.selectbox("Select Page", ["🗺️ Explore Data", "📊 Business Use Cases"])

if page == "🗺️ Explore Data":
    # Header with title
    st.markdown("""
    <h1 style="color: #FFFFFF; margin-bottom: 30px; font-size: 42px;">PhonePe Transaction Analysis</h1>
    """, unsafe_allow_html=True)
    
    # Top section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<p class="main-title">All India</p>', unsafe_allow_html=True)
        
        # Filters
        filter_col1, filter_col2 = st.columns(2)
        with filter_col1:
            st.markdown('<p style="color: white; font-size: 18px;">Transactions</p>', unsafe_allow_html=True)
        with filter_col2:
            # Get available years and quarters
            years_quarters = run_query("SELECT DISTINCT year, quarter FROM agg_transaction ORDER BY year DESC, quarter DESC")
            year_quarter_options = [f"Q{row['quarter']} {row['year']}" for _, row in years_quarters.iterrows()]
            selected_period = st.selectbox("", year_quarter_options, key="period")
            
            # Parse selected period
            selected_quarter = int(selected_period.split()[0][1])
            selected_year = int(selected_period.split()[1])
    
    # Main content area
    map_col, list_col = st.columns([2.5, 1])
    
    with map_col:
        # Get state-wise transaction data
        query = f"""
        SELECT 
            state,
            SUM(transaction_amount) AS total_amount,
            SUM(transaction_count) AS total_count
        FROM agg_transaction
        WHERE year = {selected_year} AND quarter = {selected_quarter}
        GROUP BY state
        ORDER BY total_amount DESC
        """
        
        df_state = run_query(query)
        
        # State name mapping
        state_mapping = {
            'andaman-&-nicobar-islands': 'Andaman & Nicobar',
            'andhra-pradesh': 'Andhra Pradesh',
            'arunachal-pradesh': 'Arunachal Pradesh',
            'assam': 'Assam',
            'bihar': 'Bihar',
            'chandigarh': 'Chandigarh',
            'chhattisgarh': 'Chhattisgarh',
            'dadra-&-nagar-haveli-&-daman-&-diu': 'Dadra and Nagar Haveli and Daman and Diu',
            'delhi': 'NCT of Delhi',
            'goa': 'Goa',
            'gujarat': 'Gujarat',
            'haryana': 'Haryana',
            'himachal-pradesh': 'Himachal Pradesh',
            'jammu-&-kashmir': 'Jammu & Kashmir',
            'jharkhand': 'Jharkhand',
            'karnataka': 'Karnataka',
            'kerala': 'Kerala',
            'ladakh': 'Ladakh',
            'lakshadweep': 'Lakshadweep',
            'madhya-pradesh': 'Madhya Pradesh',
            'maharashtra': 'Maharashtra',
            'manipur': 'Manipur',
            'meghalaya': 'Meghalaya',
            'mizoram': 'Mizoram',
            'nagaland': 'Nagaland',
            'odisha': 'Odisha',
            'puducherry': 'Puducherry',
            'punjab': 'Punjab',
            'rajasthan': 'Rajasthan',
            'sikkim': 'Sikkim',
            'tamil-nadu': 'Tamil Nadu',
            'telangana': 'Telangana',
            'tripura': 'Tripura',
            'uttar-pradesh': 'Uttar Pradesh',
            'uttarakhand': 'Uttarakhand',
            'west-bengal': 'West Bengal'
        }
        
        df_state['state_name'] = df_state['state'].map(state_mapping)
        
        # Create choropleth map
        fig = go.Figure(go.Choroplethmapbox(
            geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
            locations=df_state['state_name'],
            z=df_state['total_amount'],
            featureidkey='properties.ST_NM',
            colorscale=[[0, '#1a0033'], [0.5, '#ff6b35'], [1, '#f7931e']],
            marker_opacity=0.8,
            marker_line_width=0.5,
            marker_line_color='#00D9FF',
            showscale=False,
            hovertemplate='<b>%{location}</b><br>Amount: ₹%{z:,.0f}<extra></extra>'
        ))
        
        fig.update_layout(
            mapbox_style="carto-darkmatter",
            mapbox_zoom=3.5,
            mapbox_center={"lat": 22.5, "lon": 79},
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            height=700,
            paper_bgcolor='#2D1B4E',
            plot_bgcolor='#2D1B4E'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with list_col:
        st.markdown('<p class="transactions-title">Transactions</p>', unsafe_allow_html=True)
        
        # Get top 10 states for transactions
        query_top = f"""
        SELECT 
            state,
            SUM(transaction_amount) AS total_amount
        FROM agg_transaction
        WHERE year = {selected_year} AND quarter = {selected_quarter}
        GROUP BY state
        ORDER BY total_amount DESC
        LIMIT 10
        """
        
        df_top = run_query(query_top)
        
        # Display top 10 list
        for idx, row in df_top.iterrows():
            value_str = f"₹{row['total_amount']/10000000:.2f}Cr"
            state_display = row['state'].replace('-', ' ').title()
            
            st.markdown(f"""
            <div class="rank-item">
                <span><span class="rank-number">{idx+1}</span>{state_display}</span>
                <span class="rank-value">{value_str}</span>
            </div>
            """, unsafe_allow_html=True)

else:  # Business Use Cases page
    st.title("PhonePe Business Use Cases - SQL Queries")
    
    # Use Case 1
    with st.expander("Use Case 1: Decoding Transaction Dynamics on PhonePe"):
        st.subheader("Query 1.1 - Top 10 states with the highest total transaction amount")
        df = run_query("SELECT state, SUM(transaction_amount) AS total_amount FROM agg_transaction GROUP BY state ORDER BY total_amount DESC LIMIT 10")
        st.dataframe(df.style.format({'total_amount': '₹{:,.0f}'}))
        fig, ax = plt.subplots(figsize=(10, 6), facecolor='#2D1B4E')
        ax.set_facecolor('#2D1B4E')
        bars = ax.barh(df['state'], df['total_amount'], color='#00D9FF')
        ax.set_xlabel('Total Amount', color='white')
        ax.set_ylabel('State', color='white')
        ax.tick_params(colors='white')
        ax.invert_yaxis()
        for spine in ax.spines.values():
            spine.set_color('white')
        st.pyplot(fig)
        plt.close()

        st.subheader("Query 1.2 - Total transaction count and Amount for each transaction type")
        df = run_query("SELECT transaction_type, SUM(transaction_count) AS total_count, SUM(transaction_amount) AS total_amount FROM agg_transaction GROUP BY transaction_type ORDER BY total_amount DESC")
        st.dataframe(df.style.format({'total_amount': '₹{:,.0f}'}))
        fig, ax = plt.subplots(figsize=(10, 6), facecolor='#2D1B4E')
        ax.set_facecolor('#2D1B4E')
        ax.bar(df['transaction_type'], df['total_amount'], color='#00D9FF')
        ax.set_xlabel('Transaction Type', color='white')
        ax.set_ylabel('Total Amount', color='white')
        ax.tick_params(colors='white')
        plt.xticks(rotation=45, ha='right')
        for spine in ax.spines.values():
            spine.set_color('white')
        st.pyplot(fig)
        plt.close()

        st.subheader("Query 1.3 - Which year had the highest total transactions across all states")
        df = run_query("SELECT year, SUM(transaction_count) AS total_count, SUM(transaction_amount) AS total_amount FROM agg_transaction GROUP BY year ORDER BY total_amount DESC LIMIT 1")
        st.dataframe(df.style.format({'total_amount': '₹{:,.0f}'}))

        st.subheader("Query 1.4 - Top 5 districts with the most transaction volume")
        df = run_query("SELECT state, districts, SUM(amount) AS total_amount FROM map_transaction GROUP BY state, districts ORDER BY total_amount DESC LIMIT 5")
        st.dataframe(df.style.format({'total_amount': '₹{:,.0f}'}))
        fig, ax = plt.subplots(figsize=(10, 6), facecolor='#2D1B4E')
        ax.set_facecolor('#2D1B4E')
        ax.bar(df['districts'], df['total_amount'], color='#00D9FF')
        ax.set_xlabel('District', color='white')
        ax.set_ylabel('Total Amount', color='white')
        ax.tick_params(colors='white')
        plt.xticks(rotation=45, ha='right')
        for spine in ax.spines.values():
            spine.set_color('white')
        st.pyplot(fig)
        plt.close()

        st.subheader("Query 1.5 - Total transactions happened in each quarter across all years")
        df = run_query("SELECT year, quarter, SUM(transaction_count) AS total_count FROM agg_transaction GROUP BY year, quarter ORDER BY year, quarter")
        st.dataframe(df)
        df['year_quarter'] = df['year'].astype(str) + '-Q' + df['quarter'].astype(str)
        fig, ax = plt.subplots(figsize=(10, 6), facecolor='#2D1B4E')
        ax.set_facecolor('#2D1B4E')
        ax.plot(df['year_quarter'], df['total_count'], color='#00D9FF', marker='o', linewidth=2)
        ax.set_xlabel('Quarter', color='white')
        ax.set_ylabel('Total Count', color='white')
        ax.tick_params(colors='white')
        plt.xticks(rotation=45, ha='right')
        for spine in ax.spines.values():
            spine.set_color('white')
        st.pyplot(fig)
        plt.close()

        st.subheader("Query 1.6 - Quarterly transaction type analysis")
        df = run_query("SELECT transaction_type, year, quarter, SUM(transaction_amount) AS total_amount, SUM(transaction_count) AS total_transactions, CAST(AVG(transaction_amount) AS NUMERIC(20,2)) AS avg_transaction_value FROM agg_transaction GROUP BY transaction_type, year, quarter ORDER BY year DESC, quarter DESC, total_amount DESC LIMIT 20")
        st.dataframe(df.style.format({'total_amount': '₹{:,.0f}'}))

        st.subheader("Query 1.7 - State-wise Pincode Transaction Summary")
        df = run_query("SELECT state, level, SUM(count) AS total_count, SUM(amount) AS total_amount FROM top_transaction WHERE level = 'Pincode' GROUP BY state, level ORDER BY total_amount DESC LIMIT 10")
        st.dataframe(df.style.format({'total_amount': '₹{:,.0f}'}))
        fig, ax = plt.subplots(figsize=(10, 6), facecolor='#2D1B4E')
        ax.set_facecolor('#2D1B4E')
        ax.barh(df['state'], df['total_amount'], color='#00D9FF')
        ax.set_xlabel('Total Amount', color='white')
        ax.set_ylabel('State', color='white')
        ax.tick_params(colors='white')
        ax.invert_yaxis()
        for spine in ax.spines.values():
            spine.set_color('white')
        st.pyplot(fig)
        plt.close()

        st.subheader("Query 1.8 - Top Pincodes by Transaction Value")
        df = run_query("SELECT state, entity_name, SUM(count) AS total_count, SUM(amount) AS total_amount FROM top_transaction WHERE level = 'Pincode' GROUP BY state, entity_name ORDER BY total_amount DESC LIMIT 5")
        st.dataframe(df.style.format({'total_amount': '₹{:,.0f}'}))
        fig, ax = plt.subplots(figsize=(10, 6), facecolor='#2D1B4E')
        ax.set_facecolor('#2D1B4E')
        ax.bar(df['entity_name'], df['total_amount'], color='#00D9FF')
        ax.set_xlabel('Pincode', color='white')
        ax.set_ylabel('Total Amount', color='white')
        ax.tick_params(colors='white')
        plt.xticks(rotation=45, ha='right')
        for spine in ax.spines.values():
            spine.set_color('white')
        st.pyplot(fig)
        plt.close()

        st.subheader("Query 1.9 - Top 10 Pincodes by Transaction Count")
        df = run_query("SELECT state, entity_name, SUM(count) AS total_count FROM top_transaction WHERE level = 'Pincode' GROUP BY state, entity_name ORDER BY total_count DESC LIMIT 10")
        st.dataframe(df)
        fig, ax = plt.subplots(figsize=(10, 6), facecolor='#2D1B4E')
        ax.set_facecolor('#2D1B4E')
        ax.bar(df['entity_name'], df['total_count'], color='#00D9FF')
        ax.set_xlabel('Pincode', color='white')
        ax.set_ylabel('Total Count', color='white')
        ax.tick_params(colors='white')
        plt.xticks(rotation=45, ha='right')
        for spine in ax.spines.values():
            spine.set_color('white')
        st.pyplot(fig)
        plt.close()

        st.subheader("Query 1.10 - Top 10 Districts by Transaction Count")
        df = run_query("SELECT state, districts, SUM(count) AS total_count FROM map_transaction GROUP BY state, districts ORDER BY total_count DESC LIMIT 10")
        st.dataframe(df)
        fig, ax = plt.subplots(figsize=(10, 6), facecolor='#2D1B4E')
        ax.set_facecolor('#2D1B4E')
        ax.bar(df['districts'], df['total_count'], color='#00D9FF')
        ax.set_xlabel('District', color='white')
        ax.set_ylabel('Total Count', color='white')
        ax.tick_params(colors='white')
        plt.xticks(rotation=45, ha='right')
        for spine in ax.spines.values():
            spine.set_color('white')
        st.pyplot(fig)
        plt.close()

        st.subheader("Query 1.11 - Quarterly Transaction Summary")
        df = run_query("SELECT year, quarter, SUM(transaction_count) AS total_count, SUM(transaction_amount) AS total_amount FROM agg_transaction GROUP BY year, quarter ORDER BY year, quarter")
        st.dataframe(df.style.format({'total_amount': '₹{:,.0f}'}))
        df['year_quarter'] = df['year'].astype(str) + '-Q' + df['quarter'].astype(str)
        fig, ax = plt.subplots(figsize=(10, 6), facecolor='#2D1B4E')
        ax.set_facecolor('#2D1B4E')
        ax.plot(df['year_quarter'], df['total_amount'], color='#00D9FF', marker='o', linewidth=2)
        ax.set_xlabel('Quarter', color='white')
        ax.set_ylabel('Total Amount', color='white')
        ax.tick_params(colors='white')
        plt.xticks(rotation=45, ha='right')
        for spine in ax.spines.values():
            spine.set_color('white')
        st.pyplot(fig)
        plt.close()

    # Use Case 2
    with st.expander("Use Case 2: Device Dominance and User Engagement Analysis"):
        st.subheader("Query 2.1 - Top 10 mobile brands")
        df = run_query("SELECT brand, SUM(count) AS total_users FROM agg_users GROUP BY brand ORDER BY total_users DESC LIMIT 10")
        st.dataframe(df)
        fig, ax = plt.subplots(figsize=(10, 6), facecolor='#2D1B4E')
        ax.set_facecolor('#2D1B4E')
        ax.barh(df['brand'], df['total_users'], color='#00D9FF')
        ax.set_xlabel('Total Users', color='white')
        ax.set_ylabel('Brand', color='white')
        ax.tick_params(colors='white')
        ax.invert_yaxis()
        for spine in ax.spines.values():
            spine.set_color('white')
        st.pyplot(fig)
        plt.close()

        st.subheader("Query 2.2 - App engagement ratio")
        df = run_query("SELECT districts, SUM(registered_users) AS total_registered_users, SUM(app_opens) AS total_app_opens, ROUND(CAST(SUM(app_opens) AS NUMERIC) / NULLIF(SUM(registered_users), 0), 2) AS app_engagement_ratio FROM map_users GROUP BY districts ORDER BY app_engagement_ratio DESC LIMIT 20")
        st.dataframe(df)
        fig, ax = plt.subplots(figsize=(10, 6), facecolor='#2D1B4E')
        ax.set_facecolor('#2D1B4E')
        ax.bar(range(len(df)), df['app_engagement_ratio'], color='#00D9FF')
        ax.set_xlabel('District', color='white')
        ax.set_ylabel('Engagement Ratio', color='white')
        ax.tick_params(colors='white')
        plt.xticks(range(len(df)), df['districts'], rotation=90, ha='right')
        for spine in ax.spines.values():
            spine.set_color('white')
        st.pyplot(fig)
        plt.close()

        st.subheader("Query 2.3 - Top 10 Brands by State")
        df = run_query("SELECT state, brand, SUM(count) AS total_users FROM agg_users GROUP BY state, brand ORDER BY total_users DESC LIMIT 10")
        st.dataframe(df)
        fig, ax = plt.subplots(figsize=(10, 6), facecolor='#2D1B4E')
        ax.set_facecolor('#2D1B4E')
        ax.bar(df['brand'], df['total_users'], color='#00D9FF')
        ax.set_xlabel('Brand', color='white')
        ax.set_ylabel('Total Users', color='white')
        ax.tick_params(colors='white')
        plt.xticks(rotation=45, ha='right')
        for spine in ax.spines.values():
            spine.set_color('white')
        st.pyplot(fig)
        plt.close()

        st.subheader("Query 2.4 - Yearly Registered Users by State")
        df = run_query("SELECT state, year, SUM(registered_users) AS total_users FROM map_users GROUP BY state, year ORDER BY year, total_users DESC LIMIT 20")
        st.dataframe(df)

        st.subheader("Query 2.5 - Top 10 districts by registered users")
        df = run_query("SELECT state, districts, SUM(registered_users) AS total_registered_users, SUM(app_opens) AS total_app_opens FROM map_users GROUP BY state, districts ORDER BY total_registered_users DESC LIMIT 10")
        st.dataframe(df)
        fig, ax = plt.subplots(figsize=(10, 6), facecolor='#2D1B4E')
        ax.set_facecolor('#2D1B4E')
        ax.bar(df['districts'], df['total_registered_users'], color='#00D9FF')
        ax.set_xlabel('District', color='white')
        ax.set_ylabel('Registered Users', color='white')
        ax.tick_params(colors='white')
        plt.xticks(rotation=45, ha='right')
        for spine in ax.spines.values():
            spine.set_color('white')
        st.pyplot(fig)
        plt.close()

        st.subheader("Query 2.6 - Brand Usage by Year")
        df = run_query("SELECT brand, year, SUM(count) AS total_users FROM agg_users GROUP BY brand, year ORDER BY year DESC, total_users DESC LIMIT 20")
        st.dataframe(df)

        st.subheader("Query 2.7 - Quarter-wise app engagement")
        df = run_query("SELECT year, quarter, SUM(registered_users) AS total_registered_users, SUM(app_opens) AS total_app_opens, ROUND(CAST(SUM(app_opens) AS NUMERIC) / NULLIF(SUM(registered_users), 0), 2) AS avg_engagement_ratio FROM map_users GROUP BY year, quarter ORDER BY year, quarter")
        st.dataframe(df)
        df['year_quarter'] = df['year'].astype(str) + '-Q' + df['quarter'].astype(str)
        fig, ax = plt.subplots(figsize=(10, 6), facecolor='#2D1B4E')
        ax.set_facecolor('#2D1B4E')
        ax.plot(df['year_quarter'], df['avg_engagement_ratio'], color='#00D9FF', marker='o', linewidth=2)
        ax.set_xlabel('Quarter', color='white')
        ax.set_ylabel('Engagement Ratio', color='white')
        ax.tick_params(colors='white')
        plt.xticks(rotation=45, ha='right')
        for spine in ax.spines.values():
            spine.set_color('white')
        st.pyplot(fig)
        plt.close()

    # Use Case 3
    with st.expander("Use Case 3: Insurance Engagement Analysis"):
        st.subheader("Query 3.1 - Top 10 States by Insurance Policies")
        df = run_query("SELECT state, SUM(insurance_count) AS total_policies, SUM(insurance_amount) AS total_premium FROM agg_insurance GROUP BY state ORDER BY total_policies DESC LIMIT 10")
        st.dataframe(df.style.format({'total_premium': '₹{:,.0f}'}))
        fig, ax = plt.subplots(figsize=(10, 6), facecolor='#2D1B4E')
        ax.set_facecolor('#2D1B4E')
        ax.barh(df['state'], df['total_policies'], color='#00D9FF')
        ax.set_xlabel('Total Policies', color='white')
        ax.set_ylabel('State', color='white')
        ax.tick_params(colors='white')
        ax.invert_yaxis()
        for spine in ax.spines.values():
            spine.set_color('white')
        st.pyplot(fig)
        plt.close()

        st.subheader("Query 3.2 - Yearly Insurance Trends")
        df = run_query("SELECT year, SUM(insurance_count) AS total_policies, SUM(insurance_amount) AS total_premium FROM agg_insurance GROUP BY year ORDER BY year")
        st.dataframe(df.style.format({'total_premium': '₹{:,.0f}'}))
        fig, ax = plt.subplots(figsize=(10, 6), facecolor='#2D1B4E')
        ax.set_facecolor('#2D1B4E')
        ax.plot(df['year'], df['total_policies'], color='#00D9FF', marker='o', linewidth=2)
        ax.set_xlabel('Year', color='white')
        ax.set_ylabel('Total Policies', color='white')
        ax.tick_params(colors='white')
        for spine in ax.spines.values():
            spine.set_color('white')
        st.pyplot(fig)
        plt.close()

        st.subheader("Query 3.3 - Quarterly Insurance Summary")
        df = run_query("SELECT year, quarter, SUM(insurance_count) AS total_policies, SUM(insurance_amount) AS total_premium FROM agg_insurance GROUP BY year, quarter ORDER BY year, quarter")
        st.dataframe(df.style.format({'total_premium': '₹{:,.0f}'}))
        df['year_quarter'] = df['year'].astype(str) + '-Q' + df['quarter'].astype(str)
        fig, ax = plt.subplots(figsize=(10, 6), facecolor='#2D1B4E')
        ax.set_facecolor('#2D1B4E')
        ax.plot(df['year_quarter'], df['total_policies'], color='#00D9FF', marker='o', linewidth=2)
        ax.set_xlabel('Quarter', color='white')
        ax.set_ylabel('Total Policies', color='white')
        ax.tick_params(colors='white')
        plt.xticks(rotation=45, ha='right')
        for spine in ax.spines.values():
            spine.set_color('white')
        st.pyplot(fig)
        plt.close()

        st.subheader("Query 3.4 - Top 10 Insurance Districts")
        df = run_query("SELECT state, entity_name AS district, SUM(count) AS total_policies, SUM(amount) AS total_premium FROM top_insurance WHERE level = 'District' GROUP BY state, entity_name ORDER BY total_premium DESC LIMIT 10")
        st.dataframe(df.style.format({'total_premium': '₹{:,.0f}'}))
        fig, ax = plt.subplots(figsize=(10, 6), facecolor='#2D1B4E')
        ax.set_facecolor('#2D1B4E')
        ax.bar(df['district'], df['total_premium'], color='#00D9FF')
        ax.set_xlabel('District', color='white')
        ax.set_ylabel('Total Premium', color='white')
        ax.tick_params(colors='white')
        plt.xticks(rotation=45, ha='right')
        for spine in ax.spines.values():
            spine.set_color('white')
        st.pyplot(fig)
        plt.close()

        st.subheader("Query 3.5 - Insurance Count by State and Year")
        df = run_query("SELECT state, year, SUM(insurance_count) AS total_policies FROM agg_insurance GROUP BY state, year ORDER BY year DESC, total_policies DESC LIMIT 20")
        st.dataframe(df)

    # Use Case 4
    with st.expander("Use Case 4: User Registration Analysis"):
        st.subheader("Query 4.1 - Top 10 States by Registered Users")
        df = run_query("SELECT state, SUM(registered_users) AS total_registered_users FROM map_users GROUP BY state ORDER BY total_registered_users DESC LIMIT 10")
        st.dataframe(df)
        fig, ax = plt.subplots(figsize=(10, 6), facecolor='#2D1B4E')
        ax.set_facecolor('#2D1B4E')
        ax.barh(df['state'], df['total_registered_users'], color='#00D9FF')
        ax.set_xlabel('Registered Users', color='white')
        ax.set_ylabel('State', color='white')
        ax.tick_params(colors='white')
        ax.invert_yaxis()
        for spine in ax.spines.values():
            spine.set_color('white')
        st.pyplot(fig)
        plt.close()

        st.subheader("Query 4.2 - Top 10 Districts by Registered Users")
        df = run_query("SELECT state, district, SUM(registered_users) AS total_users FROM top_users WHERE level = 'District' GROUP BY state, district ORDER BY total_users DESC LIMIT 10")
        st.dataframe(df)
        fig, ax = plt.subplots(figsize=(10, 6), facecolor='#2D1B4E')
        ax.set_facecolor('#2D1B4E')
        ax.bar(df['district'], df['total_users'], color='#00D9FF')
        ax.set_xlabel('District', color='white')
        ax.set_ylabel('Total Users', color='white')
        ax.tick_params(colors='white')
        plt.xticks(rotation=45, ha='right')
        for spine in ax.spines.values():
            spine.set_color('white')
        st.pyplot(fig)
        plt.close()

        st.subheader("Query 4.3 - Top 10 Pincodes by Registered Users")
        df = run_query("SELECT state, district AS pincode, SUM(registered_users) AS total_users FROM top_users WHERE level = 'Pincode' GROUP BY state, district ORDER BY total_users DESC LIMIT 10")
        st.dataframe(df)
        fig, ax = plt.subplots(figsize=(10, 6), facecolor='#2D1B4E')
        ax.set_facecolor('#2D1B4E')
        ax.bar(df['pincode'], df['total_users'], color='#00D9FF')
        ax.set_xlabel('Pincode', color='white')
        ax.set_ylabel('Total Users', color='white')
        ax.tick_params(colors='white')
        plt.xticks(rotation=45, ha='right')
        for spine in ax.spines.values():
            spine.set_color('white')
        st.pyplot(fig)
        plt.close()

        st.subheader("Query 4.4 - Yearly User Registration Trends")
        df = run_query("SELECT year, SUM(registered_users) AS total_users FROM map_users GROUP BY year ORDER BY year")
        st.dataframe(df)
        fig, ax = plt.subplots(figsize=(10, 6), facecolor='#2D1B4E')
        ax.set_facecolor('#2D1B4E')
        ax.plot(df['year'], df['total_users'], color='#00D9FF', marker='o', linewidth=2)
        ax.set_xlabel('Year', color='white')
        ax.set_ylabel('Total Users', color='white')
        ax.tick_params(colors='white')
        for spine in ax.spines.values():
            spine.set_color('white')
        st.pyplot(fig)
        plt.close()

        st.subheader("Query 4.5 - Quarterly User Registration Summary")
        df = run_query("SELECT year, quarter, SUM(registered_users) AS total_users, SUM(app_opens) AS total_app_opens FROM map_users GROUP BY year, quarter ORDER BY year, quarter")
        st.dataframe(df)
        df['year_quarter'] = df['year'].astype(str) + '-Q' + df['quarter'].astype(str)
        fig, ax = plt.subplots(figsize=(10, 6), facecolor='#2D1B4E')
        ax.set_facecolor('#2D1B4E')
        ax.plot(df['year_quarter'], df['total_users'], color='#00D9FF', marker='o', linewidth=2)
        ax.set_xlabel('Quarter', color='white')
        ax.set_ylabel('Total Users', color='white')
        ax.tick_params(colors='white')
        plt.xticks(rotation=45, ha='right')
        for spine in ax.spines.values():
            spine.set_color('white')
        st.pyplot(fig)
        plt.close()

    # Use Case 5
    with st.expander("Use Case 5: Transaction Analysis Across States and Districts"):
        st.subheader("Query 5.1 - Transaction Summary by State and Quarter")
        df = run_query("SELECT state, year, quarter, SUM(transaction_amount) AS total_amount, SUM(transaction_count) AS total_count FROM agg_transaction GROUP BY state, year, quarter ORDER BY year DESC, quarter DESC, total_amount DESC LIMIT 20")
        st.dataframe(df.style.format({'total_amount': '₹{:,.0f}'}))

        st.subheader("Query 5.2 - Top 10 Districts by Transaction Amount")
        df = run_query("SELECT state, entity_name AS district, SUM(amount) AS total_amount, SUM(count) AS total_transactions FROM top_transaction WHERE level = 'District' GROUP BY state, entity_name ORDER BY total_amount DESC LIMIT 10")
        st.dataframe(df.style.format({'total_amount': '₹{:,.0f}'}))
        fig, ax = plt.subplots(figsize=(10, 6), facecolor='#2D1B4E')
        ax.set_facecolor('#2D1B4E')
        ax.bar(df['district'], df['total_amount'], color='#00D9FF')
        ax.set_xlabel('District', color='white')
        ax.set_ylabel('Total Amount', color='white')
        ax.tick_params(colors='white')
        plt.xticks(rotation=45, ha='right')
        for spine in ax.spines.values():
            spine.set_color('white')
        st.pyplot(fig)
        plt.close()

        st.subheader("Query 5.3 - Top 10 Pincodes by Transaction Amount")
        df = run_query("SELECT state, entity_name AS pincode, SUM(amount) AS total_amount, SUM(count) AS total_transactions FROM top_transaction WHERE level = 'Pincode' GROUP BY state, entity_name ORDER BY total_amount DESC LIMIT 10")
        st.dataframe(df.style.format({'total_amount': '₹{:,.0f}'}))
        fig, ax = plt.subplots(figsize=(10, 6), facecolor='#2D1B4E')
        ax.set_facecolor('#2D1B4E')
        ax.bar(df['pincode'], df['total_amount'], color='#00D9FF')
        ax.set_xlabel('Pincode', color='white')
        ax.set_ylabel('Total Amount', color='white')
        ax.tick_params(colors='white')
        plt.xticks(rotation=45, ha='right')
        for spine in ax.spines.values():
            spine.set_color('white')
        st.pyplot(fig)
        plt.close()

        st.subheader("Query 5.4 - District Transaction by Type")
        df = run_query("SELECT state, districts, type, SUM(amount) AS total_amount, SUM(count) AS total_count FROM map_transaction GROUP BY state, districts, type ORDER BY total_amount DESC LIMIT 20")
        st.dataframe(df.style.format({'total_amount': '₹{:,.0f}'}))

        st.subheader("Query 5.5 - District Transaction Summary by Year")
        df = run_query("SELECT state, districts, year, SUM(amount) AS total_amount, SUM(count) AS total_count FROM map_transaction GROUP BY state, districts, year ORDER BY year DESC, total_amount DESC LIMIT 20")
        st.dataframe(df.style.format({'total_amount': '₹{:,.0f}'}))
