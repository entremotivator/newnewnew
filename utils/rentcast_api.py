import streamlit as st
import requests
import time
from datetime import datetime, timezone
from typing import Dict, Optional
from utils.config import get_config
import datetime

# ------------------------
# RentCast API Integration - Property Lookup Only
# ------------------------
@st.cache_data(ttl=7200, show_spinner=False)  # Increased cache to 2 hours for property data stability
def fetch_property_data(address: str, city: str, state: str) -> Optional[Dict]:
    """Enhanced property data fetching with caching and error handling"""
    config = get_config()
    if not config:
        return None
        
    url = f"{config['rentcast_url']}/properties"
    headers = {
        "accept": "application/json", 
        "X-Api-Key": config['rentcast_key']
    }
    params = {
        "address": address,
        "city": city,
        "state": state,
        "propertyType": "Single Family"  # Can be made configurable
    }
    
    max_retries = 3
    retry_delay = 1
    
    for attempt in range(max_retries):
        try:
            with st.spinner(f"🔍 Fetching property data... (Attempt {attempt + 1}/{max_retries})"):
                resp = requests.get(url, headers=headers, params=params, timeout=30)  # Increased timeout to 30 seconds
                
            if resp.status_code == 200:
                data = resp.json()
                if data and len(data) > 0:
                    # Enrich the data
                    property_data = data[0] if isinstance(data, list) else data
                    property_data['fetch_timestamp'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
                    property_data['search_params'] = params
                    property_data['cache_key'] = f"{address}_{city}_{state}".lower().replace(" ", "_")  # Added cache key for better tracking
                    return property_data
                else:
                    st.warning("🔍 No property data found for this address")
                    return None
            elif resp.status_code == 401:
                st.error("🔑 API Authentication failed - check your RentCast API key")
                return None
            elif resp.status_code == 429:
                if attempt < max_retries - 1:  # Added retry logic for rate limiting
                    st.warning(f"🚦 Rate limit hit, retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                    continue
                else:
                    st.error("🚦 Rate limit exceeded - please wait before making another request")
                    return None
            elif resp.status_code >= 500:  # Added retry for server errors
                if attempt < max_retries - 1:
                    st.warning(f"🌐 Server error, retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                else:
                    st.error(f"🌐 Server Error {resp.status_code}: {resp.text}")
                    return None
            else:
                st.error(f"🌐 API Error {resp.status_code}: {resp.text}")
                return None
                
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                st.warning(f"⏱️ Request timeout, retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2
                continue
            else:
                st.error("⏱️ Request timed out after multiple attempts")
                return None
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                st.warning(f"🌐 Connection error, retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2
                continue
            else:
                st.error(f"🌐 Connection error: {e}")
                return None
    
    return None

def validate_rentcast_config() -> bool:
    """Validate RentCast API configuration"""
    config = get_config()
    if not config:
        st.error("❌ Configuration not available")
        return False
    
    if not config.get('rentcast_key'):
        st.error("❌ RentCast API key not configured")
        return False
    
    if not config.get('rentcast_url'):
        st.error("❌ RentCast API URL not configured")
        return False
    
    return True

def test_rentcast_connection() -> bool:
    """Test RentCast API connection"""
    if not validate_rentcast_config():
        return False
    
    config = get_config()
    url = f"{config['rentcast_url']}/properties"
    headers = {
        "accept": "application/json",
        "X-Api-Key": config['rentcast_key']
    }
    
    # Test with a simple query
    params = {
        "address": "123 Main St",
        "city": "Los Angeles",
        "state": "CA",
        "propertyType": "Single Family"
    }
    
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        if resp.status_code == 200:
            st.success("✅ RentCast API connection successful")
            return True
        elif resp.status_code == 401:
            st.error("❌ RentCast API authentication failed")
            return False
        else:
            st.warning(f"⚠️ RentCast API returned status {resp.status_code}")
            return False
    except Exception as e:
        st.error(f"❌ RentCast API connection failed: {e}")
        return False

