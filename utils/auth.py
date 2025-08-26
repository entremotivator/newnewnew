import streamlit as st
import requests
from datetime import datetime, timezone
from typing import Dict, Optional
from supabase import create_client, Client
import datetime

# ------------------------
# Init Supabase
# ------------------------
@st.cache_resource
def init_supabase():
    """Initialize Supabase client with caching"""
    try:
        SUPABASE_URL = st.secrets["supabase"]["url"]
        SUPABASE_KEY = st.secrets["supabase"]["key"]
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        st.error(f"Failed to initialize Supabase: {e}")
        return None

# ------------------------
# WordPress Login
# ------------------------
def wp_login(username: str, password: str) -> Optional[Dict]:
    """WordPress JWT authentication with user ID fetch"""
    from utils.config import get_config
    config = get_config()
    
    if not config:
        return None

    url = f"{config['wp_url']}/wp-json/jwt-auth/v1/token"

    try:
        with st.spinner("Authenticating..."):
            resp = requests.post(
                url,
                data={"username": username, "password": password},
                timeout=10
            )

        if resp.status_code == 200:
            token_data = resp.json()

            # Fetch user details (to get WordPress user ID)
            me_url = f"{config['wp_url']}/wp-json/wp/v2/users/me"
            me_resp = requests.get(
                me_url,
                headers={"Authorization": f"Bearer {token_data['token']}"},
                timeout=10
            )

            if me_resp.status_code == 200:
                user_info = me_resp.json()
                token_data["user_id"] = user_info.get("id")
                token_data["user_email"] = user_info.get("email")
                token_data["username"] = user_info.get("username", token_data.get("user_nicename"))
            else:
                st.warning(f"⚠️ Could not fetch user info: {me_resp.text}")

            # Cache user session in Supabase
            cache_user_data(token_data)
            return token_data

        else:
            error_msg = resp.json().get('message', resp.text) if resp.text else 'Unknown error'
            st.error(f"🚫 Login failed: {error_msg}")
            return None

    except requests.exceptions.RequestException as e:
        st.error(f"🌐 Connection error: {e}")
        return None

# ------------------------
# Cache User Data
# ------------------------
def cache_user_data(user_data: Dict):
    """Cache user data for session management"""
    supabase = init_supabase()
    if supabase and "user_id" in user_data:
        try:
            supabase.table("user_sessions").upsert({
                "user_id": user_data["user_id"],
                "last_login": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "user_data": user_data
            }).execute()
        except Exception as e:
            st.warning(f"Failed to cache user data: {e}")

