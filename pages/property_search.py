import streamlit as st
from typing import Dict, Optional
from datetime import datetime
import json
from utils.rentcast_api import fetch_property_data
from utils.property_analysis import analyze_property, display_property_analysis
from utils.property_management import save_property
from utils.usage import log_usage

def display_property_search(user_id: int, usage_data: Dict):
    """Display property search interface"""
    
    st.header("🔍 Property Search & Analysis")
    
    # Quick search form - single line address with zip
    with st.form("property_search", clear_on_submit=False):
        col1, col2 = st.columns([4, 1])
        
        with col1:
            full_address = st.text_input(
                "🏠 Full Property Address", 
                value="", 
                placeholder="Enter full address with city, state, zip (e.g., 5500 Grand Lake Dr, San Antonio, TX 78244)"
            )
        with col2:
            search_submitted = st.form_submit_button("🔍 Search", use_container_width=True)
    
    # Advanced search toggle
    with st.expander("🔧 Advanced Search Options"):
        advanced_property_search()
    
    # Search execution
    if search_submitted:
        if not full_address:
            st.error("⚠️ Please enter a full address")
            return
        
        # Parse the full address
        parsed_address = parse_full_address(full_address.strip())
        if not parsed_address:
            st.error("⚠️ Please enter a complete address with city, state, and zip code")
            return
        
        # Check usage limits
        if usage_data['current_month'] >= usage_data['limit']:
            st.error("⚠️ Monthly API limit reached. Upgrade your plan or wait until next month.")
            return
        
        # Show loading spinner
        with st.spinner("🔍 Searching for property data..."):
            try:
                # Fetch property data
                property_data = fetch_property_data(
                    parsed_address['address'], 
                    parsed_address['city'], 
                    parsed_address['state']
                )
                
                if property_data:
                    # Log successful usage - simplified version
                    try:
                        # Use a simpler logging approach that matches your current schema
                        log_usage(user_id, full_address, {
                            "full_address": full_address,
                            "parsed": parsed_address,
                            "search_type": "property_search",
                            "timestamp": datetime.now().isoformat()
                        })
                    except Exception as log_error:
                        # Continue operation even if logging fails
                        st.warning(f"Usage logging failed: {str(log_error)}")
                        # You might want to log this to a file or alternative storage
                    
                    # Store results in session state
                    st.session_state['last_property_data'] = property_data
                    st.session_state['last_search_params'] = parsed_address
                    
                    # Display property information in organized cards
                    display_property_cards(property_data)
                    
                    # Display analysis if available
                    try:
                        analysis = analyze_property(property_data)
                        st.session_state['last_analysis'] = analysis
                        display_property_analysis(analysis, property_data)
                    except Exception as e:
                        st.warning(f"Analysis temporarily unavailable: {str(e)}")
                    
                    # Action buttons
                    display_property_actions(user_id, property_data, full_address)
                    
                else:
                    st.warning("🔍 No property data found. Please check the address and try again.")
                    display_search_tips()
                    
            except Exception as e:
                st.error(f"❌ Error fetching property data: {str(e)}")
                st.info("Please try again or contact support if the issue persists.")

def parse_full_address(full_address: str) -> Optional[Dict[str, str]]:
    """Parse full address into components"""
    try:
        # Split by commas and clean
        parts = [part.strip() for part in full_address.split(',')]
        
        if len(parts) < 3:
            return None
        
        # Extract components
        address = parts[0]
        city = parts[1]
        
        # Handle state and zip from last part
        state_zip = parts[-1].strip().split()
        if len(state_zip) >= 2:
            state = state_zip[0].upper()
            zipcode = state_zip[-1]
        else:
            return None
        
        return {
            'address': address,
            'city': city.title(),
            'state': state,
            'zipcode': zipcode
        }
    except:
        return None

def display_property_cards(property_data: Dict):
    """Display property information in organized cards using exact JSON structure"""
    
    st.subheader("🏠 Property Information")
    
    # Basic Property Info Card
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
    
    # Address Information Card
    with st.container():
        st.markdown("### 🏠 Address Details")
        st.write(f"**Full Address:** {property_data.get('formattedAddress', 'N/A')}")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write(f"**Zip Code:** {property_data.get('zipCode', 'N/A')}")
        with col2:
            st.write(f"**Zoning:** {property_data.get('zoning', 'N/A')}")
        with col3:
            st.write(f"**Assessor ID:** {property_data.get('assessorID', 'N/A')}")
        
        if property_data.get('legalDescription'):
            st.write(f"**Legal Description:** {property_data.get('legalDescription')}")
    
    st.divider()
    
    # Features Card
    features = property_data.get('features', {})
    if features:
        st.markdown("### 🏡 Property Features")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("**Structure:**")
            st.write(f"• Architecture: {features.get('architectureType', 'N/A')}")
            st.write(f"• Floors: {features.get('floorCount', 'N/A')}")
            st.write(f"• Rooms: {features.get('roomCount', 'N/A')}")
            st.write(f"• Foundation: {features.get('foundationType', 'N/A')}")
        
        with col2:
            st.write("**Climate & Utilities:**")
            cooling = "✅ Yes" if features.get('cooling') else "❌ No"
            st.write(f"• Cooling: {cooling} ({features.get('coolingType', '')})")
            heating = "✅ Yes" if features.get('heating') else "❌ No"
            st.write(f"• Heating: {heating} ({features.get('heatingType', '')})")
            
        with col3:
            st.write("**Amenities:**")
            garage = "✅ Yes" if features.get('garage') else "❌ No"
            st.write(f"• Garage: {garage} ({features.get('garageSpaces', 0)} spaces)")
            pool = "✅ Yes" if features.get('pool') else "❌ No"
            st.write(f"• Pool: {pool} ({features.get('poolType', '')})")
            fireplace = "✅ Yes" if features.get('fireplace') else "❌ No"
            st.write(f"• Fireplace: {fireplace}")
    
    st.divider()
    
    # Financial Information Cards
    col1, col2 = st.columns(2)
    
    # Sales History Card
    with col1:
        st.markdown("### 💰 Sales History")
        history = property_data.get('history', {})
        if history:
            for date, info in sorted(history.items(), reverse=True):
                sale_date = datetime.fromisoformat(info['date'].replace('Z', '+00:00')).strftime('%B %d, %Y')
                st.write(f"**{sale_date}:** ${info['price']:,}")
        
        # Last sale info
        if property_data.get('lastSaleDate') and property_data.get('lastSalePrice'):
            last_sale_date = datetime.fromisoformat(property_data['lastSaleDate'].replace('Z', '+00:00')).strftime('%B %d, %Y')
            st.metric("Last Sale", f"${property_data['lastSalePrice']:,}", f"on {last_sale_date}")
    
    # Tax Information Card
    with col2:
        st.markdown("### 🏛️ Tax Information")
        
        # Current tax assessment
        tax_assessments = property_data.get('taxAssessments', {})
        if tax_assessments:
            latest_year = max(tax_assessments.keys())
            latest_assessment = tax_assessments[latest_year]
            
            st.metric(f"Tax Assessment ({latest_year})", f"${latest_assessment['value']:,}")
            st.write(f"• Land Value: ${latest_assessment['land']:,}")
            st.write(f"• Improvements: ${latest_assessment['improvements']:,}")
        
        # Property taxes
        property_taxes = property_data.get('propertyTaxes', {})
        if property_taxes:
            latest_tax_year = max(property_taxes.keys())
            latest_tax = property_taxes[latest_tax_year]
            st.metric(f"Property Tax ({latest_tax_year})", f"${latest_tax['total']:,}")
        
        # HOA fees
        hoa = property_data.get('hoa', {})
        if hoa and hoa.get('fee'):
            st.metric("HOA Fee", f"${hoa['fee']:,}/month")
    
    st.divider()
    
    # Owner Information Card
    owner = property_data.get('owner', {})
    if owner:
        st.markdown("### 👤 Owner Information")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Owner:** {', '.join(owner.get('names', ['N/A']))}")
            st.write(f"**Owner Type:** {owner.get('type', 'N/A')}")
            owner_occupied = "Yes" if property_data.get('ownerOccupied') else "No"
            st.write(f"**Owner Occupied:** {owner_occupied}")
        
        with col2:
            mailing_address = owner.get('mailingAddress', {})
            if mailing_address:
                st.write("**Mailing Address:**")
                st.write(mailing_address.get('formattedAddress', 'N/A'))

def display_property_actions(user_id: int, property_data: Dict, full_address: str):
    """Display action buttons for property results"""
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("💾 Save Property", use_container_width=True):
            try:
                save_property(user_id, property_data, {
                    "full_address": full_address,
                    "search_params": st.session_state.get('last_search_params', {})
                })
                st.success("✅ Property saved successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error saving property: {str(e)}")
    
    with col2:
        if st.button("📄 Generate Report", use_container_width=True):
            try:
                analysis = st.session_state.get('last_analysis', {})
                report = generate_property_report(property_data, analysis)
                
                # Create filename from address
                filename = property_data.get('formattedAddress', 'property_report').replace(' ', '_').replace(',', '')
                
                st.download_button(
                    label="📥 Download Report",
                    data=report,
                    file_name=f"{filename}_report.md",
                    mime="text/markdown",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"❌ Error generating report: {str(e)}")
    
    with col3:
        if st.button("🗺️ View on Map", use_container_width=True):
            lat = property_data.get('latitude')
            lon = property_data.get('longitude')
            if lat and lon:
                # Create a simple map
                import pandas as pd
                df = pd.DataFrame({'lat': [lat], 'lon': [lon]})
                st.map(df, zoom=15)
            else:
                st.warning("Location coordinates not available")

def advanced_property_search():
    """Advanced property search with filters"""
    st.subheader("🔍 Advanced Property Search")
    
    with st.expander("Search Filters", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("💰 Price Range")
            min_price = st.number_input("Min Price ($)", value=0, step=10000, format="%d")
            max_price = st.number_input("Max Price ($)", value=1000000, step=10000, format="%d")
        
        with col2:
            st.subheader("🏠 Property Details")
            min_bedrooms = st.selectbox("Min Bedrooms", [0, 1, 2, 3, 4, 5], index=0)
            max_bedrooms = st.selectbox("Max Bedrooms", [1, 2, 3, 4, 5, 10], index=5)
            min_sqft = st.number_input("Min Sq Ft", value=0, step=100)
        
        with col3:
            st.subheader("🏘️ Property Type")
            property_types = st.multiselect(
                "Property Types", 
                ["Single Family", "Condo", "Townhouse", "Multi-Family", "Apartment"],
                default=["Single Family"]
            )
    
    # Store advanced search criteria in session state
    st.session_state['advanced_search_filters'] = {
        'min_price': min_price,
        'max_price': max_price,
        'min_bedrooms': min_bedrooms,
        'max_bedrooms': max_bedrooms,
        'min_sqft': min_sqft,
        'property_types': property_types
    }

def display_search_tips():
    """Display search troubleshooting tips"""
    st.info("""
    💡 **Search Tips:**
    - Use complete address format: "Street Address, City, State ZipCode"
    - Example: "5500 Grand Lake Dr, San Antonio, TX 78244"
    - Ensure correct spelling of street names and city
    - Some rural or new properties may not be available
    - Try variations of the address if not found
    """)

def generate_property_report(property_data: Dict, analysis: Dict = None) -> str:
    """Generate comprehensive property report using exact JSON structure"""
    
    try:
        report = f"""# Property Report - {property_data.get('formattedAddress', 'N/A')}

**Generated:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

---

## Property Overview

**Full Address:** {property_data.get('formattedAddress', 'N/A')}
**Property ID:** {property_data.get('id', 'N/A')}
**Property Type:** {property_data.get('propertyType', 'N/A')}
**County:** {property_data.get('county', 'N/A')}

### Physical Characteristics
- **Bedrooms:** {property_data.get('bedrooms', 'N/A')}
- **Bathrooms:** {property_data.get('bathrooms', 'N/A')}
- **Square Footage:** {property_data.get('squareFootage', 0):,} sq ft
- **Lot Size:** {property_data.get('lotSize', 0):,} sq ft
- **Year Built:** {property_data.get('yearBuilt', 'N/A')}

### Property Features
"""
        
        # Add features
        features = property_data.get('features', {})
        if features:
            report += f"""
- **Architecture:** {features.get('architectureType', 'N/A')}
- **Floors:** {features.get('floorCount', 'N/A')}
- **Rooms:** {features.get('roomCount', 'N/A')}
- **Garage:** {'Yes' if features.get('garage') else 'No'} ({features.get('garageSpaces', 0)} spaces)
- **Pool:** {'Yes' if features.get('pool') else 'No'}
- **Fireplace:** {'Yes' if features.get('fireplace') else 'No'}
- **Heating:** {features.get('heatingType', 'N/A')}
- **Cooling:** {features.get('coolingType', 'N/A')}
"""
        
        # Add financial information
        report += """
---

## Financial Information

"""
        
        # Sales history
        history = property_data.get('history', {})
        if history:
            report += "### Sales History\n"
            for date, info in sorted(history.items(), reverse=True):
                sale_date = datetime.fromisoformat(info['date'].replace('Z', '+00:00')).strftime('%B %d, %Y')
                report += f"- **{sale_date}:** ${info['price']:,}\n"
        
        # Tax information
        tax_assessments = property_data.get('taxAssessments', {})
        if tax_assessments:
            latest_year = max(tax_assessments.keys())
            latest_assessment = tax_assessments[latest_year]
            report += f"""
### Tax Assessment ({latest_year})
- **Total Value:** ${latest_assessment['value']:,}
- **Land Value:** ${latest_assessment['land']:,}
- **Improvements:** ${latest_assessment['improvements']:,}
"""
        
        # Property taxes
        property_taxes = property_data.get('propertyTaxes', {})
        if property_taxes:
            latest_tax_year = max(property_taxes.keys())
            latest_tax = property_taxes[latest_tax_year]
            report += f"- **Property Tax ({latest_tax_year}):** ${latest_tax['total']:,}\n"
        
        # HOA
        hoa = property_data.get('hoa', {})
        if hoa and hoa.get('fee'):
            report += f"- **HOA Fee:** ${hoa['fee']:,}/month\n"
        
        # Owner information
        owner = property_data.get('owner', {})
        if owner:
            report += f"""
### Owner Information
- **Owner:** {', '.join(owner.get('names', ['N/A']))}
- **Owner Type:** {owner.get('type', 'N/A')}
- **Owner Occupied:** {'Yes' if property_data.get('ownerOccupied') else 'No'}
"""
        
        # Add analysis if available
        if analysis:
            report += """
---

## Investment Analysis

"""
            if analysis.get('investment_score'):
                score = analysis['investment_score']
                report += f"**Investment Score:** {score.get('grade', 'N/A')} ({score.get('score', 0)}/100)\n"
                report += f"**Recommendation:** {score.get('recommendation', 'N/A')}\n"
        
        report += """
---

## Disclaimers

1. This report is based on publicly available data and estimates.
2. All information should be verified independently.
3. Consult with real estate professionals before making investment decisions.
4. Market conditions and property values can change rapidly.

---

*Report generated by Real Estate Intelligence Portal using RentCast API data*
"""
        
        return report
        
    except Exception as e:
        return f"Error generating report: {str(e)}"

def test_rentcast_connection():
    """Test function to verify RentCast API connection"""
    st.subheader("🔧 API Connection Test")
    
    if st.button("Test RentCast API"):
        with st.spinner("Testing API connection..."):
            try:
                # Test with the example address
                test_data = fetch_property_data("5500 Grand Lake Dr", "San Antonio", "TX")
                if test_data:
                    st.success("✅ RentCast API connection successful!")
                    with st.expander("Raw API Response", expanded=False):
                        st.json(test_data)
                else:
                    st.warning("⚠️ API connected but no data returned")
            except Exception as e:
                st.error(f"❌ API connection failed: {str(e)}")
                st.info("Check your API key, network connection, and RentCast API status.")
