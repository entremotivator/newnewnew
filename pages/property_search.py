import streamlit as st
from typing import Dict
from utils.rentcast_api import fetch_property_data
from utils.property_analysis import analyze_property, display_property_analysis
from utils.property_management import save_property
from utils.usage import log_usage

def display_property_search(user_id: int, usage_data: Dict):
    """Display property search interface"""
    
    st.header("🔍 Property Search & Analysis")
    
    # Quick search form
    with st.form("property_search", clear_on_submit=False):
        col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
        
        with col1:
            address = st.text_input("🏠 Property Address", value="123 Main St", placeholder="Enter street address")
        with col2:
            city = st.text_input("🏙️ City", value="Los Angeles", placeholder="Enter city")
        with col3:
            state = st.text_input("🗺️ State", value="CA", placeholder="State")
        with col4:
            search_submitted = st.form_submit_button("🔍 Search", use_container_width=True)
    
    # Advanced search toggle
    with st.expander("🔧 Advanced Search Options"):
        advanced_property_search()
    
    # Search execution
    if search_submitted and address and city and state:
        if usage_data['current_month'] >= usage_data['limit']:
            st.error("⚠️ Monthly API limit reached. Upgrade your plan or wait until next month.")
        else:
            # Fetch property data
            property_data = fetch_property_data(address, city, state)
            
            if property_data:
                # Log usage
                log_usage(user_id, f"{address}, {city}, {state}", "property_search", {
                    "address": address, "city": city, "state": state
                })
                
                # Perform analysis
                analysis = analyze_property(property_data)
                
                # Display results
                display_property_analysis(analysis, property_data)
                
                # Save property option
                col1, col2, col3 = st.columns([1, 1, 2])
                with col1:
                    if st.button("💾 Save Property", use_container_width=True):
                        save_property(user_id, property_data, {
                            "address": address, "city": city, "state": state
                        })
                        st.rerun()
                
                with col2:
                    if st.button("📄 Generate Report", use_container_width=True):
                        report = generate_property_report(property_data, analysis)
                        st.download_button(
                            label="📥 Download Report",
                            data=report,
                            file_name=f"property_report_{address.replace(' ', '_')}_{city}.md",
                            mime="text/markdown"
                        )
            else:
                st.warning("🔍 No property data found. Please check the address and try again.")

def advanced_property_search():
    """Advanced property search with filters"""
    st.subheader("🔍 Advanced Property Search")
    
    with st.expander("Search Filters", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            min_price = st.number_input("Min Price ($)", value=0, step=10000)
            max_price = st.number_input("Max Price ($)", value=1000000, step=10000)
        
        with col2:
            min_bedrooms = st.selectbox("Min Bedrooms", [0, 1, 2, 3, 4, 5])
            max_bedrooms = st.selectbox("Max Bedrooms", [1, 2, 3, 4, 5, 10], index=5)
        
        with col3:
            property_types = st.multiselect(
                "Property Types", 
                ["Single Family", "Condo", "Townhouse", "Multi-Family"],
                default=["Single Family"]
            )
    
    # Saved searches
    if st.button("💾 Save Search Criteria"):
        # Implementation for saving search criteria
        st.success("Search criteria saved!")

def generate_property_report(property_data: Dict, analysis: Dict) -> str:
    """Generate comprehensive property report"""
    from datetime import datetime
    
    basic = analysis['basic_info']
    financial = analysis['financial_metrics']
    market = analysis['market_analysis']
    score = analysis['investment_score']
    
    report = f"""
# Property Investment Analysis Report

**Generated:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

---

## Property Overview

**Address:** {basic['address']}
**Location:** {basic['city']}, {basic['state']} {basic['zip_code']}
**Property Type:** {basic['property_type']}
**Year Built:** {basic['year_built']}

### Physical Characteristics
- **Bedrooms:** {basic['bedrooms']}
- **Bathrooms:** {basic['bathrooms']}
- **Square Footage:** {basic['square_feet']:,} sq ft
- **Lot Size:** {basic['lot_size']} sq ft

---

## Investment Analysis

### Overall Investment Score: {score['grade']} ({score['score']}/100)
**Recommendation:** {score['recommendation']}

### Financial Metrics
- **Property Price:** ${financial['price']:,}
- **Monthly Rent Estimate:** ${financial['monthly_rent']:,}
- **Annual Rent:** ${financial['annual_rent']:,}
- **Cap Rate:** {financial['cap_rate']}%
- **Estimated Monthly Cash Flow:** ${financial['estimated_cash_flow']:,}
- **Price-to-Rent Ratio:** {financial['price_to_rent_ratio']:.1f}
- **ROI Estimate:** {financial['roi_estimate']}%

### Market Analysis
- **Neighborhood:** {market['neighborhood']}
- **Price per Sq Ft:** ${market['price_per_sqft']:.0f}
- **Market Status:** {market['market_status']}
- **Appreciation Potential:** {market['appreciation_potential']}

### Positive Investment Factors
{chr(10).join(f'• {factor}' for factor in score['positive_factors'])}

---

## Important Disclaimers

1. This analysis is based on estimated data and should not be considered as professional financial advice.
2. Actual rental income, expenses, and property values may vary significantly.
3. Please consult with real estate professionals, accountants, and financial advisors before making investment decisions.
4. Market conditions can change rapidly and affect investment performance.

---

*Report generated by Real Estate Intelligence Portal*
"""
    
    return report

