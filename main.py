import streamlit as st
import time
from datetime import datetime, timezone
from typing import Dict, Optional

# ------------------------
# Page Components
# ------------------------
from pages.property_search import display_property_search
from pages.portfolio import display_portfolio_page
from pages.orders import display_orders_page
from pages.market_analysis import market_analysis_page
from pages.settings import display_settings_page

# ------------------------
# Utilities
# ------------------------
from utils.auth import wp_login, init_supabase
from utils.config import get_config
from utils.usage import get_user_usage

# ------------------------
# Page Configuration
# ------------------------
st.set_page_config(
    page_title="Real Estate Intelligence Portal",
    page_icon="🏡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
.main-header {
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    padding: 2rem;
    border-radius: 10px;
    color: white;
    text-align: center;
    margin-bottom: 2rem;
}
.metric-card {
    background: white;
    padding: 1rem;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    border-left: 4px solid #667eea;
}
.property-card {
    background: #f8f9fa;
    padding: 1.5rem;
    border-radius: 12px;
    margin: 1rem 0;
    border: 1px solid #e9ecef;
}
.status-badge {
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
}
.success-badge { background: #d4edda; color: #155724; }
.warning-badge { background: #fff3cd; color: #856404; }
.danger-badge { background: #f8d7da; color: #721c24; }
</style>
""", unsafe_allow_html=True)

# ------------------------
# Global Initialization
# ------------------------
supabase = init_supabase()
config = get_config()

# ------------------------
# Main Application
# ------------------------
def main():
    """Main application function"""
    # Initialize session state
    if "wp_user" not in st.session_state:
        st.session_state.wp_user = None
    if "selected_property" not in st.session_state:
        st.session_state.selected_property = None

    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🏡 Real Estate Intelligence Portal</h1>
        <p>Comprehensive property analysis and investment management platform</p>
    </div>
    """, unsafe_allow_html=True)

    # Authentication check
    if st.session_state.wp_user is None:
        display_login_page()
    else:
        display_main_application()

# ------------------------
# Login Page
# ------------------------
def display_login_page():
    """Display WordPress login interface"""
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="background: white; padding: 2rem; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <h2 style="text-align: center; color: #333; margin-bottom: 2rem;">🔑 Account Access</h2>
        </div>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            username = st.text_input("📧 WordPress Username/Email", placeholder="Enter your username or email")
            password = st.text_input("🔐 Password", type="password", placeholder="Enter your password")
            login_submitted = st.form_submit_button("🚀 Login", use_container_width=True)

            if login_submitted and username and password:
                wp_user = wp_login(username, password)
                if wp_user:
                    st.session_state.wp_user = wp_user
                    st.success("✅ Login successful! Redirecting...")
                    time.sleep(1)
                    st.rerun()

        st.markdown("""
        <div style="text-align: center; margin-top: 2rem; color: #666;">
            <p>🔒 Secure login powered by WordPress JWT authentication</p>
            <p>Need help? Contact support or check your WordPress credentials</p>
        </div>
        """, unsafe_allow_html=True)

# ------------------------
# Main Application Interface
# ------------------------
def display_main_application():
    """Display main application interface"""
    wp_user = st.session_state.wp_user
    user_id = wp_user["user_id"]

    # Sidebar
    with st.sidebar:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 1rem; border-radius: 10px; color: white; margin-bottom: 1rem;">
            <h4 style="margin: 0;">👋 Welcome back!</h4>
            <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">{wp_user['user_email']}</p>
        </div>
        """ , unsafe_allow_html=True)

        # API Usage
        usage_data = get_user_usage(user_id)
        usage_pct = (usage_data['current_month'] / usage_data['limit']) * 100
        st.markdown("### 📊 API Usage This Month")
        st.progress(usage_pct / 100)
        st.write(f"{usage_data['current_month']}/{usage_data['limit']} calls ({usage_pct:.1f}%)")
        if usage_data.get('by_type'):
            st.write("**By Type:**")
            for query_type, count in usage_data['by_type'].items():
                st.write(f"• {query_type}: {count}")

        st.markdown("---")

        # Navigation
        page = st.selectbox(
            "🧭 Navigation",
            ["🏠 Property Search", "📊 Portfolio", "🛒 Orders", "📈 Market Analysis", "⚙️ Settings"]
        )
        st.markdown("---")

        if st.button("🔓 Logout", use_container_width=True):
            st.session_state.wp_user = None
            st.rerun()

    # Main content
    if page == "🏠 Property Search":
        display_property_search(user_id, usage_data)
    elif page == "📊 Portfolio":
        display_portfolio_page(user_id)
    elif page == "🛒 Orders":
        display_orders_page(user_id)
    elif page == "📈 Market Analysis":
        market_analysis_page()
    elif page == "⚙️ Settings":
        display_settings_page(user_id)

# ------------------------
# Run App
# ------------------------
if __name__ == "__main__":
    main()

