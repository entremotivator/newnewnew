import streamlit as st
import requests
from datetime import datetime, timezone
from typing import Dict, List
import pandas as pd
import plotly.express as px
from utils.config import get_config
import datetime

# ------------------------
# WooCommerce Integration
# ------------------------
@st.cache_data(ttl=600, show_spinner=False)  # Increased cache time to 10 minutes and disabled spinner
def get_wc_orders(user_id: int) -> List[Dict]:
    """Get WooCommerce orders for a customer"""
    config = get_config()
    if not config:
        return []

    url = f"{config['wp_url']}/wp-json/wc/v3/orders"
    params = {
        "customer": user_id,
        "per_page": 50,
        "orderby": "date",
        "order": "desc"
    }

    try:
        resp = requests.get(
            url,
            auth=(config['wc_key'], config['wc_secret']),
            params=params,
            timeout=15
        )

        if resp.status_code == 200:
            orders = resp.json()
            # Enrich order data
            for order in orders:
                order['total_float'] = float(order['total'])
                order['date_created_parsed'] = datetime.datetime.fromisoformat(
                    order['date_created'].replace('T', ' ').replace('Z', '')
                )
            return orders
        else:
            st.error(f"🛒 WooCommerce API error: {resp.text}")
            return []

    except requests.exceptions.RequestException as e:
        st.error(f"🌐 Failed to fetch orders: {e}")
        return []

def display_orders_analytics(orders: List[Dict]):
    """Display comprehensive order analytics"""
    if not orders:
        st.info("📦 No orders found")
        return
        
    # Convert to DataFrame for analysis
    df = pd.DataFrame(orders)
    df['month'] = pd.to_datetime(df['date_created']).dt.to_period('M')
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Orders", 
            len(orders),
            delta=f"+{len([o for o in orders if o['status'] == 'completed'])} completed"
        )
    
    with col2:
        total_value = sum(o['total_float'] for o in orders)
        st.metric("Total Value", f"${total_value:,.2f}")
    
    with col3:
        avg_order = total_value / len(orders) if orders else 0
        st.metric("Average Order", f"${avg_order:,.2f}")
    
    with col4:
        recent_orders = len([o for o in orders if 
            datetime.datetime.fromisoformat(o['date_created'].replace('T', ' ').replace('Z', '')) 
            > datetime.datetime.now() - datetime.timedelta(days=30)
        ])
        st.metric("Recent Orders (30d)", recent_orders)
    
    # Order trend chart
    if len(orders) > 1:
        monthly_data = df.groupby('month').agg({
            'id': 'count',
            'total_float': 'sum'
        }).reset_index()
        monthly_data['month_str'] = monthly_data['month'].astype(str)
        
        fig = px.line(
            monthly_data, 
            x='month_str', 
            y=['id', 'total_float'],
            title="📈 Order Trends Over Time",
            labels={'value': 'Count/Amount', 'month_str': 'Month'}
        )
        st.plotly_chart(fig, use_container_width=True)

