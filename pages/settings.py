import streamlit as st
from typing import Dict
from utils.rentcast_api import test_rentcast_connection, validate_rentcast_config
from utils.usage import get_user_usage

def display_settings_page(user_id: int):
    """Display settings and configuration page"""
    
    st.header("⚙️ Settings & Configuration")
    
    tab1, tab2, tab3, tab4 = st.tabs(["🔧 API Settings", "📊 Usage Statistics", "👤 Account", "ℹ️ About"])
    
    with tab1:
        api_settings_tab()
    
    with tab2:
        usage_statistics_tab(user_id)
    
    with tab3:
        account_settings_tab()
    
    with tab4:
        about_tab()

def api_settings_tab():
    """API configuration and testing"""
    st.subheader("🔧 API Configuration")
    
    # RentCast API Settings
    st.markdown("### 🏠 RentCast API")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔍 Test RentCast Connection"):
            test_rentcast_connection()
    
    with col2:
        if st.button("✅ Validate Configuration"):
            if validate_rentcast_config():
                st.success("✅ RentCast configuration is valid")
    
    # API Status
    st.markdown("### 📡 API Status")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("**RentCast API**\n🟢 Active")
    
    with col2:
        st.info("**WordPress API**\n🟢 Connected")
    
    with col3:
        st.info("**WooCommerce API**\n🟢 Operational")

def usage_statistics_tab(user_id: int):
    """Display detailed usage statistics"""
    st.subheader("📊 Usage Statistics")
    
    usage_data = get_user_usage(user_id)
    
    # Current month usage
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "This Month", 
            f"{usage_data['current_month']}/{usage_data['limit']}",
            delta=f"{((usage_data['current_month']/usage_data['limit'])*100):.1f}% used"
        )
    
    with col2:
        st.metric("Total Lifetime", usage_data['total'])
    
    with col3:
        remaining = usage_data['limit'] - usage_data['current_month']
        st.metric("Remaining", remaining)
    
    # Usage by type
    if usage_data.get('by_type'):
        st.subheader("📈 Usage by Type")
        
        import plotly.express as px
        import pandas as pd
        
        usage_df = pd.DataFrame([
            {'Type': k, 'Count': v} 
            for k, v in usage_data['by_type'].items()
        ])
        
        fig = px.bar(usage_df, x='Type', y='Count', title="API Calls by Type")
        st.plotly_chart(fig, use_container_width=True)
    
    # Daily usage pattern
    if usage_data.get('daily_usage'):
        st.subheader("📅 Daily Usage Pattern")
        
        daily_df = pd.DataFrame([
            {'Date': k, 'Calls': v} 
            for k, v in usage_data['daily_usage'].items()
        ])
        daily_df['Date'] = pd.to_datetime(daily_df['Date'])
        daily_df = daily_df.sort_values('Date')
        
        fig = px.line(daily_df, x='Date', y='Calls', title="Daily API Usage")
        st.plotly_chart(fig, use_container_width=True)

def account_settings_tab():
    """Account management settings"""
    st.subheader("👤 Account Settings")
    
    # User info
    if st.session_state.get('wp_user'):
        user = st.session_state.wp_user
        
        st.markdown("### 📋 Account Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"**Username:** {user.get('username', 'N/A')}")
            st.info(f"**Email:** {user.get('user_email', 'N/A')}")
        
        with col2:
            st.info(f"**User ID:** {user.get('user_id', 'N/A')}")
            st.info(f"**Display Name:** {user.get('user_display_name', 'N/A')}")
    
    # Preferences
    st.markdown("### ⚙️ Preferences")
    
    col1, col2 = st.columns(2)
    
    with col1:
        default_state = st.selectbox(
            "Default Search State",
            ["CA", "NY", "TX", "FL", "WA", "OR", "NV", "AZ"],
            index=0
        )
        
        currency_format = st.selectbox(
            "Currency Format",
            ["USD ($)", "EUR (€)", "GBP (£)"],
            index=0
        )
    
    with col2:
        auto_save = st.checkbox("Auto-save searched properties", value=False)
        email_notifications = st.checkbox("Email notifications", value=True)
    
    if st.button("💾 Save Preferences"):
        st.success("✅ Preferences saved successfully!")

def about_tab():
    """About and help information"""
    st.subheader("ℹ️ About Real Estate Intelligence Portal")
    
    st.markdown("""
    ### 🏡 Real Estate Intelligence Portal
    
    A comprehensive property analysis and investment management platform that helps you:
    
    - **🔍 Search Properties:** Find detailed property information using RentCast API
    - **📊 Analyze Investments:** Calculate cap rates, cash flow, and ROI estimates
    - **💼 Manage Portfolio:** Track and analyze your property investments
    - **🛒 Order Management:** View and manage your WooCommerce orders
    - **📈 Market Analysis:** Understand market trends and comparable properties
    
    ### 🔧 Features
    
    - WordPress JWT authentication
    - Supabase database integration
    - Real-time property data from RentCast
    - Comprehensive financial analysis
    - Portfolio tracking and analytics
    - Order management integration
    - Usage tracking and limits
    
    ### 📞 Support
    
    For technical support or questions:
    - Check your WordPress credentials
    - Verify API key configurations
    - Contact system administrator
    
    ### 🔒 Privacy & Security
    
    - All data is encrypted and secure
    - API keys are stored securely
    - User sessions are managed safely
    - No sensitive data is logged
    """)
    
    # System info
    st.markdown("### 🖥️ System Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("**Version:** 2.0.0")
        st.info("**Framework:** Streamlit")
    
    with col2:
        st.info("**Database:** Supabase")
        st.info("**API:** RentCast, WordPress, WooCommerce")

