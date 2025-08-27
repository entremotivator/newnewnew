import streamlit as st
from supabase import create_client, Client

# Supabase configuration
SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_ANON_KEY = st.secrets["supabase"]["anon_key"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

def initialize_auth_state():
    """Initialize authentication-related session state variables."""
    if "user" not in st.session_state:
        st.session_state.user = None
    if "access_token" not in st.session_state:
        st.session_state.access_token = None

def get_user_client():
    """Return Supabase client authorized with current user's access token."""
    if "access_token" not in st.session_state:
        return None
    client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    client.postgrest.auth(st.session_state.access_token)
    return client

def login(email, password):
    """Handle user login."""
    try:
        user = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        if user and user.session:
            st.session_state.access_token = user.session.access_token
            st.session_state.user = user.user
        return user
    except Exception as e:
        st.error(f"Login failed: {e}")
        return None

def signup(email, password):
    """Handle user signup."""
    try:
        user = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        if user and user.session:
            st.session_state.access_token = user.session.access_token
            st.session_state.user = user.user

            # Initialize usage tracking
            from utils.database import initialize_user_usage
            initialize_user_usage(str(user.user.id), email)
        return user
    except Exception as e:
        st.error(f"Signup failed: {e}")
        return None

def logout():
    """Handle user logout."""
    st.session_state.user = None
    st.session_state.access_token = None
    st.success("Logged out successfully!")
    st.rerun()

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
