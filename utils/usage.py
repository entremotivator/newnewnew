import streamlit as st
from datetime import datetime, timezone
from typing import Dict, List
from utils.auth import init_supabase

# ------------------------
# API Usage Management
# ------------------------
def get_user_usage(user_id: int) -> Dict:
    """Enhanced usage tracking with detailed metrics"""
    supabase = init_supabase()
    if not supabase:
        return {"current_month": 0, "total": 0, "limit": 30}

    try:
        now = datetime.utcnow()
        start_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Current month usage
        current_month_res = (
            supabase.table("api_usage")
            .select("*")
            .eq("user_id", user_id)
            .gte("created_at", start_month.isoformat())
            .execute()
        )

        # Total usage
        total_res = (
            supabase.table("api_usage")
            .select("*")
            .eq("user_id", user_id)
            .execute()
        )

        # Usage by endpoint
        usage_by_type = {}
        for record in current_month_res.data:
            query_type = record.get("query_type", "property_search")
            usage_by_type[query_type] = usage_by_type.get(query_type, 0) + 1

        return {
            "current_month": len(current_month_res.data),
            "total": len(total_res.data),
            "limit": 30,
            "by_type": usage_by_type,
            "daily_usage": calculate_daily_usage(current_month_res.data),
        }

    except Exception as e:
        st.error(f"Failed to fetch usage data: {e}")
        return {"current_month": 0, "total": 0, "limit": 30}


def calculate_daily_usage(usage_data: List[Dict]) -> Dict:
    """Calculate daily usage pattern"""
    daily_counts = {}
    for record in usage_data:
        date_str = record["created_at"][:10]  # Extract date part
        daily_counts[date_str] = daily_counts.get(date_str, 0) + 1
    return daily_counts


def log_usage(
    user_id: int,
    query: str,
    query_type: str = "property_search",
    metadata: Dict = None,
):
    """Enhanced usage logging with metadata"""
    supabase = init_supabase()
    if not supabase:
        return

    try:
        log_data = {
            "user_id": user_id,
            "query": query,
            "query_type": query_type,
            "created_at": datetime.utcnow().isoformat(),
            "metadata": metadata or {},
        }
        supabase.table("api_usage").insert(log_data).execute()
    except Exception as e:
        st.warning(f"Failed to log usage: {e}")
