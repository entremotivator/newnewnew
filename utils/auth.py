import streamlit as st
from supabase import create_client, Client
from typing import Optional

# ------------------------
# Supabase Client
# ------------------------
SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_ANON_KEY = st.secrets["supabase"]["anon_key"]

def init_supabase() -> Client:
    """Initialize and return Supabase client."""
    return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

supabase: Client = init_supabase()

# ------------------------
# Authentication State
# ------------------------
def initialize_auth_state():
    """Initialize authentication-related session state variables."""
    if "user" not in st.session_state:
        st.session_state.user = None
    if "access_token" not in st.session_state:
        st.session_state.access_token = None

def get_user_client() -> Optional[Client]:
    """Return Supabase client authorized with current user's access token."""
    if "access_token" not in st.session_state or st.session_state.access_token is None:
        return None
    client = init_supabase()
    client.auth.session = {"access_token": st.session_state.access_token}
    return client

# ------------------------
# Authentication Functions
# ------------------------
def login(email: str, password: str):
    """Handle user login."""
    try:
        auth = supabase.auth.sign_in_with_password({"email": email, "password": password})
        if auth and auth.session:
            st.session_state.access_token = auth.session.access_token
            st.session_state.user = auth.user
        return auth
    except Exception as e:
        st.error(f"Login failed: {e}")
        return None

def signup(email: str, password: str):
    """Handle user signup."""
    try:
        auth = supabase.auth.sign_up({"email": email, "password": password})
        if auth and auth.session:
            st.session_state.access_token = auth.session.access_token
            st.session_state.user = auth.user

            # Initialize usage tracking (optional)
            try:
                from utils.database import initialize_user_usage
                initialize_user_usage(str(auth.user.id), email)
            except ImportError:
                pass  # skip if database module not available

        return auth
    except Exception as e:
        st.error(f"Signup failed: {e}")
        return None

def logout():
    """Handle user logout."""
    st.session_state.user = None
    st.session_state.access_token = None
    st.success("Logged out successfully!")
    st.rerun()

# ------------------------
# Auth UI Page
# ------------------------
def show_auth_page():
    """Display authentication page with login/signup tabs."""
    st.subheader("🔐 Please sign in to continue")
    
    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            login_button = st.form_submit_button("Login")
            
            if login_button and email and password:
                user = login(email, password)
                if user:
                    st.success("Logged in successfully!")
                    st.rerun()

    with tab2:
        with st.form("signup_form"):
            email = st.text_input("Email", key="signup_email")
            password = st.text_input("Password", type="password", key="signup_password")
            confirm_password = st.text_input("Confirm Password", type="password")
            signup_button = st.form_submit_button("Sign Up")
            
            if signup_button and email and password:
                if password != confirm_password:
                    st.error("Passwords do not match!")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters long!")
                else:
                    user = signup(email, password)
                    if user:
                        st.success("Account created and logged in!")
                        st.rerun()
