import streamlit as st
from typing import Dict, Optional
from datetime import datetime
import pandas as pd

# Custom modules (you must have these)
from utils.rentcast_api import fetch_property_data
from utils.property_analysis import analyze_property, display_property_analysis
from utils.property_management import save_property
from utils.usage import log_usage, get_user_usage

# ------------------------
# Main Application
# ------------------------
def main():
    st.set_page_config(page_title="Property Intelligence Portal", layout="wide")
    st.title("🏠 Real Estate Intelligence Portal")

    # Simulated user ID (replace with real user auth)
    user_id = 1

    # Display main property search interface
    display_property_search(user_id)

# ------------------------
# Property Search
# ------------------------
def display_property_search(user_id: int):
    """Display property search interface and handle logging."""
    
    st.header("🔍 Property Search & Analysis")

    # Fetch current usage for user
    usage_data = get_user_usage(user_id)

    # Quick search form
    with st.form("property_search", clear_on_submit=False):
        col1, col2 = st.columns([4, 1])
        with col1:
            full_address = st.text_input(
                "🏠 Full Property Address",
                value="",
                placeholder="5500 Grand Lake Dr, San Antonio, TX 78244"
            )
        with col2:
            search_submitted = st.form_submit_button("🔍 Search", use_container_width=True)

    # Advanced search
    with st.expander("🔧 Advanced Search Options"):
        advanced_property_search()

    if search_submitted:
        if not full_address:
            st.error("⚠️ Please enter a full address")
            log_usage(user_id, full_address, "failed_search", {"reason": "empty_address"})
            return

        parsed_address = parse_full_address(full_address.strip())
        if not parsed_address:
            st.error("⚠️ Please enter a complete address with city, state, and zip code")
            log_usage(user_id, full_address, "failed_search", {"reason": "invalid_address_format"})
            return

        # Check usage limits
        if usage_data['current_month'] >= usage_data['limit']:
            st.error("⚠️ Monthly API limit reached. Upgrade your plan or wait until next month.")
            log_usage(user_id, full_address, "limit_reached", {"current_usage": usage_data['current_month'], "limit": usage_data['limit']})
            return

        with st.spinner("🔍 Searching for property data..."):
            try:
                property_data = fetch_property_data(parsed_address['address'], parsed_address['city'], parsed_address['state'])
                
                if property_data:
                    log_usage(user_id, full_address, "property_search", {"full_address": full_address, "parsed": parsed_address})

                    st.session_state['last_property_data'] = property_data
                    st.session_state['last_search_params'] = parsed_address

                    display_property_cards(property_data)

                    try:
                        analysis = analyze_property(property_data)
                        st.session_state['last_analysis'] = analysis
                        display_property_analysis(analysis, property_data)
                    except Exception as e:
                        st.warning(f"Analysis temporarily unavailable: {str(e)}")

                    display_property_actions(user_id, property_data, full_address)

                else:
                    st.warning("🔍 No property data found. Please check the address and try again.")
                    display_search_tips()
                    log_usage(user_id, full_address, "failed_search", {"reason": "no_data_found"})

            except Exception as e:
                st.error(f"❌ Error fetching property data: {str(e)}")
                log_usage(user_id, full_address, "failed_search", {"reason": str(e)})

# ------------------------
# Helper Functions
# ------------------------
def parse_full_address(full_address: str) -> Optional[Dict[str, str]]:
    try:
        parts = [p.strip() for p in full_address.split(',')]
        if len(parts) < 3:
            return None
        address = parts[0]
        city = parts[1]
        state_zip = parts[-1].split()
        if len(state_zip) >= 2:
            state = state_zip[0].upper()
            zipcode = state_zip[-1]
        else:
            return None
        return {"address": address, "city": city.title(), "state": state, "zipcode": zipcode}
    except:
        return None

def display_property_cards(property_data: Dict):
    st.subheader("🏠 Property Information")
    with st.container():
        st.markdown("### 📍 Property Overview")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Property Type", property_data.get('propertyType', 'N/A'))
            st.metric("Year Built", property_data.get('yearBuilt', 'N/A'))
            st.metric("Square Footage", f"{property_data.get('squareFootage', 0):,} sq ft")
            st.metric("Lot Size", f"{property_data.get('lotSize', 0):,} sq ft")
        with col2:
            st.metric("Bedrooms", property_data.get('bedrooms', 'N/A'))
            st.metric("Bathrooms", property_data.get('bathrooms', 'N/A'))
            st.metric("County", property_data.get('county', 'N/A'))
            if property_data.get('subdivision'):
                st.metric("Subdivision", property_data.get('subdivision', 'N/A'))
    st.divider()

def display_property_actions(user_id: int, property_data: Dict, full_address: str):
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("💾 Save Property", use_container_width=True):
            try:
                save_property(user_id, property_data, {"full_address": full_address, "search_params": st.session_state.get('last_search_params', {})})
                st.success("✅ Property saved successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error saving property: {str(e)}")
    with col2:
        if st.button("📄 Generate Report", use_container_width=True):
            try:
                analysis = st.session_state.get('last_analysis', {})
                report = generate_property_report(property_data, analysis)
                filename = property_data.get('formattedAddress', 'property_report').replace(' ', '_').replace(',', '')
                st.download_button("📥 Download Report", report, file_name=f"{filename}_report.md", mime="text/markdown")
                log_usage(user_id, full_address, "report_generated")
            except Exception as e:
                st.error(f"❌ Error generating report: {str(e)}")
    with col3:
        if st.button("🗺️ View on Map", use_container_width=True):
            lat = property_data.get('latitude')
            lon = property_data.get('longitude')
            if lat and lon:
                df = pd.DataFrame({'lat': [lat], 'lon': [lon]})
                st.map(df, zoom=15)
            else:
                st.warning("Location coordinates not available")

def advanced_property_search():
    st.subheader("🔍 Advanced Property Search")
    with st.expander("Search Filters", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.subheader("💰 Price Range")
            min_price = st.number_input("Min Price ($)", value=0, step=10000)
            max_price = st.number_input("Max Price ($)", value=1000000, step=10000)
        with col2:
            st.subheader("🏠 Property Details")
            min_bedrooms = st.selectbox("Min Bedrooms", [0,1,2,3,4,5])
            max_bedrooms = st.selectbox("Max Bedrooms", [1,2,3,4,5,10], index=5)
            min_sqft = st.number_input("Min Sq Ft", value=0, step=100)
        with col3:
            st.subheader("🏘️ Property Type")
            property_types = st.multiselect("Property Types", ["Single Family", "Condo", "Townhouse", "Multi-Family", "Apartment"], default=["Single Family"])
    st.session_state['advanced_search_filters'] = {
        'min_price': min_price,
        'max_price': max_price,
        'min_bedrooms': min_bedrooms,
        'max_bedrooms': max_bedrooms,
        'min_sqft': min_sqft,
        'property_types': property_types
    }

def display_search_tips():
    st.info("""
💡 **Search Tips:**
- Use complete address format: "Street Address, City, State ZipCode"
- Example: "5500 Grand Lake Dr, San Antonio, TX 78244"
- Ensure correct spelling
- Some rural/new properties may not be available
- Try variations if not found
""")

def generate_property_report(property_data: Dict, analysis: Dict = None) -> str:
    """Generate markdown report"""
    report = f"# Property Report - {property_data.get('formattedAddress', 'N/A')}\n\n"
    report += f"Generated: {datetime.now().strftime('%B %d, %Y %I:%M %p')}\n\n"
    report += f"Property Type: {property_data.get('propertyType', 'N/A')}\n"
    report += f"Bedrooms: {property_data.get('bedrooms', 'N/A')}, Bathrooms: {property_data.get('bathrooms', 'N/A')}\n"
    report += f"Square Footage: {property_data.get('squareFootage', 0):,} sq ft\n"
    report += f"Lot Size: {property_data.get('lotSize', 0):,} sq ft\n"
    if analysis and analysis.get('investment_score'):
        score = analysis['investment_score']
        report += f"Investment Score: {score.get('grade', 'N/A')} ({score.get('score', 0)}/100)\nRecommendation: {score.get('recommendation', 'N/A')}\n"
    return report

# ------------------------
# Run the app
# ------------------------
if __name__ == "__main__":
    main()
