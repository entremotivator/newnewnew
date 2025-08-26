import streamlit as st
from datetime import datetime, timezone
from typing import Dict, List
import hashlib
from utils.auth import init_supabase
import datetime

# ------------------------
# Property Management
# ------------------------
def save_property(user_id: int, data: Dict, search_params: Dict = None):
    """Enhanced property saving with search context"""
    supabase = init_supabase()
    if not supabase:
        return False
        
    try:
        # Generate a unique hash for deduplication
        property_hash = hashlib.md5(
            f"{data.get('address', '')}{data.get('city', '')}{data.get('state', '')}".encode()
        ).hexdigest()
        
        property_data = {
            "user_id": user_id,
            "property_hash": property_hash,
            "data": data,
            "search_params": search_params or {},
            "created_at": datetime.datetime.utcnow().isoformat(),
            "updated_at": datetime.datetime.utcnow().isoformat()
        }
        
        # Check if property already exists
        existing = supabase.table("properties").select("id").eq(
            "user_id", user_id
        ).eq("property_hash", property_hash).execute()
        
        if existing.data:
            # Update existing
            supabase.table("properties").update(property_data).eq(
                "id", existing.data[0]["id"]
            ).execute()
            st.success("🔄 Property updated successfully!")
        else:
            # Insert new
            supabase.table("properties").insert(property_data).execute()
            st.success("💾 Property saved successfully!")
        
        return True
        
    except Exception as e:
        st.error(f"Failed to save property: {e}")
        return False

@st.cache_data(ttl=300, show_spinner=False)  # Increased cache time to 5 minutes for better performance
def get_user_properties(user_id: int) -> List[Dict]:
    """Get user properties with caching"""
    supabase = init_supabase()
    if not supabase:
        return []
        
    try:
        result = supabase.table("properties").select("*").eq(
            "user_id", user_id
        ).order("updated_at", desc=True).execute()
        return result.data
    except Exception as e:
        st.error(f"Failed to fetch properties: {e}")
        return []

def delete_property(user_id: int, property_id: int):
    """Delete a saved property"""
    supabase = init_supabase()
    if not supabase:
        return False
        
    try:
        supabase.table("properties").delete().eq("id", property_id).eq("user_id", user_id).execute()
        st.success("🗑️ Property deleted successfully!")
        st.cache_data.clear()  # Clear cache
        return True
    except Exception as e:
        st.error(f"Failed to delete property: {e}")
        return False

