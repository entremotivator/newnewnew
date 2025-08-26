import streamlit as st
from typing import Dict
from utils.woocommerce import get_wc_orders, display_orders_analytics

def display_orders_page(user_id: int):
    """Display orders management page"""
    
    st.header("🛒 Order Management")
    
    # Fetch orders
    orders = get_wc_orders(user_id)
    
    if not orders:
        st.info("📦 No orders found for your account.")
        return
    
    # Display analytics
    display_orders_analytics(orders)
    
    # Order details
    st.subheader("📋 Order Details")
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.selectbox(
            "Filter by Status", 
            ["All"] + list(set([order['status'] for order in orders]))
        )
    with col2:
        date_range = st.selectbox(
            "Date Range",
            ["All Time", "Last 30 Days", "Last 90 Days", "This Year"]
        )
    with col3:
        sort_by = st.selectbox(
            "Sort by",
            ["Date (Newest)", "Date (Oldest)", "Amount (High)", "Amount (Low)"]
        )
    
    # Apply filters
    filtered_orders = orders.copy()
    
    if status_filter != "All":
        filtered_orders = [o for o in filtered_orders if o['status'] == status_filter]
    
    # Apply date filter
    if date_range != "All Time":
        from datetime import datetime, timedelta
        now = datetime.now()
        
        if date_range == "Last 30 Days":
            cutoff = now - timedelta(days=30)
        elif date_range == "Last 90 Days":
            cutoff = now - timedelta(days=90)
        elif date_range == "This Year":
            cutoff = datetime(now.year, 1, 1)
        
        filtered_orders = [
            o for o in filtered_orders 
            if o['date_created_parsed'] > cutoff
        ]
    
    # Apply sorting
    if sort_by == "Date (Newest)":
        filtered_orders.sort(key=lambda x: x['date_created_parsed'], reverse=True)
    elif sort_by == "Date (Oldest)":
        filtered_orders.sort(key=lambda x: x['date_created_parsed'])
    elif sort_by == "Amount (High)":
        filtered_orders.sort(key=lambda x: x['total_float'], reverse=True)
    elif sort_by == "Amount (Low)":
        filtered_orders.sort(key=lambda x: x['total_float'])
    
    # Display orders
    for order in filtered_orders:
        display_order_card(order)

def display_order_card(order: Dict):
    """Display individual order card"""
    
    # Status badge styling
    status_styles = {
        'completed': 'success-badge',
        'processing': 'warning-badge',
        'pending': 'warning-badge',
        'cancelled': 'danger-badge',
        'refunded': 'danger-badge',
        'failed': 'danger-badge'
    }
    
    status_class = status_styles.get(order['status'], 'warning-badge')
    
    with st.expander(f"Order #{order['number']} - ${order['total']} - {order['date_created'][:10]}"):
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.markdown(f"""
            **Order ID:** {order['id']}  
            **Date:** {order['date_created'][:10]}  
            **Customer:** {order.get('billing', {}).get('first_name', '')} {order.get('billing', {}).get('last_name', '')}  
            **Email:** {order.get('billing', {}).get('email', 'N/A')}
            """)
        
        with col2:
            st.markdown(f"""
            **Total:** ${order['total']}  
            **Currency:** {order['currency']}  
            **Payment Method:** {order.get('payment_method_title', 'N/A')}
            """)
        
        with col3:
            st.markdown(f"""
            <div class="status-badge {status_class}">
                {order['status'].upper()}
            </div>
            """, unsafe_allow_html=True)
        
        # Order items
        if order.get('line_items'):
            st.subheader("📦 Items")
            for item in order['line_items']:
                st.write(f"• {item['name']} (Qty: {item['quantity']}) - ${item['total']}")
        
        # Shipping info
        if order.get('shipping'):
            st.subheader("🚚 Shipping Address")
            shipping = order['shipping']
            st.write(f"{shipping.get('address_1', '')} {shipping.get('address_2', '')}")
            st.write(f"{shipping.get('city', '')}, {shipping.get('state', '')} {shipping.get('postcode', '')}")
            st.write(f"{shipping.get('country', '')}")
        
        # Order notes
        if order.get('customer_note'):
            st.subheader("📝 Customer Note")
            st.write(order['customer_note'])

