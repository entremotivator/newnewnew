import streamlit as st

# ------------------------
# Config Loader
# ------------------------
@st.cache_data(ttl=3600)  # Increased TTL to 1 hour for config stability
def get_config():
    """Get configuration with error handling"""
    try:
        return {
            "wp_url": st.secrets["wordpress"]["base_url"],
            "wp_user": st.secrets["wordpress"]["username"],
            "wp_pass": st.secrets["wordpress"]["password"],
            "wc_key": st.secrets["woocommerce"]["consumer_key"],
            "wc_secret": st.secrets["woocommerce"]["consumer_secret"],
            "rentcast_key": st.secrets["rentcast"]["api_key"],
            "rentcast_url": "https://api.rentcast.io/v1"
        }
    except Exception as e:
        st.error(f"Configuration error: {e}")
        return None

