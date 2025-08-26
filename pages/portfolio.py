import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List
from utils.property_management import get_user_properties, delete_property
from datetime import datetime

def display_portfolio_page(user_id: int):
    """Display portfolio management page"""
    
    st.header("📊 Investment Portfolio")
    
    # Get user properties
    properties = get_user_properties(user_id)
    
    if not properties:
        st.info("📊 No properties in your portfolio yet. Start by searching for properties!")
        return
    
    # Portfolio overview
    display_portfolio_overview(properties)
    
    # Property management
    st.subheader("🏠 Property Management")
    display_portfolio_table(properties, user_id)

def display_portfolio_overview(properties: List[Dict]):
    """Display comprehensive portfolio analytics"""
    
    # Calculate portfolio metrics
    portfolio_metrics = calculate_portfolio_metrics(properties)
    
    st.subheader("📈 Portfolio Overview")
    
    # Key metrics row
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "Total Properties", 
            portfolio_metrics['total_properties'],
            delta=f"+{portfolio_metrics.get('new_this_month', 0)} this month"
        )
    
    with col2:
        st.metric(
            "Portfolio Value", 
            f"${portfolio_metrics['total_value']:,.0f}",
            delta=f"{portfolio_metrics.get('value_change_pct', 0):+.1f}%"
        )
    
    with col3:
        st.metric(
            "Monthly Rent", 
            f"${portfolio_metrics['total_monthly_rent']:,.0f}",
            delta=f"${portfolio_metrics.get('rent_change', 0):+,.0f}"
        )
    
    with col4:
        st.metric(
            "Avg Cap Rate", 
            f"{portfolio_metrics['avg_cap_rate']:.2f}%",
            delta=f"{portfolio_metrics.get('cap_rate_trend', 0):+.2f}%"
        )
    
    with col5:
        st.metric(
            "Total Cash Flow", 
            f"${portfolio_metrics['total_cash_flow']:,.0f}",
            delta=portfolio_metrics.get('cash_flow_status', 'Positive' if portfolio_metrics['total_cash_flow'] > 0 else 'Negative')
        )
    
    # Portfolio composition charts
    create_portfolio_charts(properties, portfolio_metrics)

def calculate_portfolio_metrics(properties: List[Dict]) -> Dict:
    """Calculate comprehensive portfolio metrics"""
    total_value = 0
    total_rent = 0
    total_cash_flow = 0
    cap_rates = []
    
    for prop in properties:
        data = prop.get('data', {})
        
        # Extract financial data
        price = data.get('price', 0) or data.get('lastSalePrice', 0)
        rent = data.get('rentEstimate', {}).get('rent', 0) if isinstance(data.get('rentEstimate'), dict) else 0
        
        if price:
            total_value += price
            annual_rent = rent * 12
            total_rent += rent
            
            # Estimate cash flow (simplified)
            monthly_expenses = price * 0.004  # 4% monthly expense ratio
            cash_flow = rent - monthly_expenses
            total_cash_flow += cash_flow
            
            # Cap rate
            if annual_rent > 0:
                cap_rate = (annual_rent / price) * 100
                cap_rates.append(cap_rate)
    
    return {
        'total_properties': len(properties),
        'total_value': total_value,
        'total_monthly_rent': total_rent,
        'total_annual_rent': total_rent * 12,
        'total_cash_flow': total_cash_flow,
        'avg_cap_rate': sum(cap_rates) / len(cap_rates) if cap_rates else 0,
        'avg_property_value': total_value / len(properties) if properties else 0,
        'portfolio_yield': (total_rent * 12 / total_value * 100) if total_value > 0 else 0
    }

def create_portfolio_charts(properties: List[Dict], metrics: Dict):
    """Create portfolio visualization charts"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Portfolio value distribution
        prop_values = []
        prop_labels = []
        
        for i, prop in enumerate(properties):
            data = prop.get('data', {})
            price = data.get('price', 0) or data.get('lastSalePrice', 0)
            address = data.get('address', f'Property {i+1}')
            
            if price > 0:
                prop_values.append(price)
                prop_labels.append(f"{address[:20]}...")
        
        if prop_values:
            fig = px.pie(
                values=prop_values,
                names=prop_labels,
                title="💰 Portfolio Value Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Cash flow by property
        cash_flows = []
        property_names = []
        
        for i, prop in enumerate(properties):
            data = prop.get('data', {})
            price = data.get('price', 0) or data.get('lastSalePrice', 0)
            rent = data.get('rentEstimate', {}).get('rent', 0) if isinstance(data.get('rentEstimate'), dict) else 0
            address = data.get('address', f'Property {i+1}')
            
            if price > 0:
                cash_flow = rent - (price * 0.004)
                cash_flows.append(cash_flow)
                property_names.append(f"{address[:15]}...")
        
        if cash_flows:
            fig = go.Figure(data=[
                go.Bar(
                    x=property_names,
                    y=cash_flows,
                    marker_color=['green' if cf > 0 else 'red' for cf in cash_flows]
                )
            ])
            fig.update_layout(
                title="💸 Monthly Cash Flow by Property",
                xaxis_title="Property",
                yaxis_title="Cash Flow ($)"
            )
            st.plotly_chart(fig, use_container_width=True)

def display_portfolio_table(properties: List[Dict], user_id: int):
    """Display portfolio properties in a table format with management options"""
    
    table_data = []
    
    for i, prop in enumerate(properties):
        data = prop.get('data', {})
        
        price = data.get('price', 0) or data.get('lastSalePrice', 0)
        rent = data.get('rentEstimate', {}).get('rent', 0) if isinstance(data.get('rentEstimate'), dict) else 0
        
        # Calculate metrics
        annual_rent = rent * 12
        cap_rate = (annual_rent / price * 100) if price > 0 else 0
        cash_flow = rent - (price * 0.004) if price > 0 else 0
        
        table_data.append({
            'Property': data.get('address', f'Property {i+1}'),
            'City': data.get('city', 'N/A'),
            'State': data.get('state', 'N/A'),
            'Price': f"${price:,.0f}" if price else 'N/A',
            'Monthly Rent': f"${rent:,.0f}" if rent else 'N/A',
            'Cap Rate': f"{cap_rate:.2f}%" if cap_rate else 'N/A',
            'Cash Flow': f"${cash_flow:,.0f}" if cash_flow else 'N/A',
            'Bedrooms': data.get('bedrooms', 'N/A'),
            'Bathrooms': data.get('bathrooms', 'N/A'),
            'Sq Ft': f"{data.get('squareFootage', 0):,}" if data.get('squareFootage') else 'N/A',
            'Added': prop.get('created_at', '')[:10] if prop.get('created_at') else 'N/A',
            'ID': prop.get('id')  # For deletion
        })
    
    if table_data:
        df = pd.DataFrame(table_data)
        
        # Add filters
        col1, col2, col3 = st.columns(3)
        with col1:
            state_filter = st.selectbox("Filter by State", ['All'] + list(df['State'].unique()))
        with col2:
            min_cap_rate = st.slider("Min Cap Rate (%)", 0.0, 20.0, 0.0, 0.5)
        with col3:
            sort_by = st.selectbox("Sort by", ['Property', 'Price', 'Cap Rate', 'Cash Flow', 'Added'])
        
        # Apply filters
        filtered_df = df.copy()
        if state_filter != 'All':
            filtered_df = filtered_df[filtered_df['State'] == state_filter]
        
        # Convert cap rate for filtering (remove % and convert to float)
        cap_rates_numeric = []
        for cap_rate_str in filtered_df['Cap Rate']:
            if cap_rate_str != 'N/A':
                try:
                    cap_rates_numeric.append(float(cap_rate_str.replace('%', '')))
                except:
                    cap_rates_numeric.append(0)
            else:
                cap_rates_numeric.append(0)
        
        filtered_df['Cap Rate Numeric'] = cap_rates_numeric
        filtered_df = filtered_df[filtered_df['Cap Rate Numeric'] >= min_cap_rate]
        
        # Display table with delete buttons
        for idx, row in filtered_df.iterrows():
            with st.expander(f"🏠 {row['Property']} - {row['Price']}"):
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.write(f"**Location:** {row['City']}, {row['State']}")
                    st.write(f"**Bedrooms:** {row['Bedrooms']}")
                    st.write(f"**Bathrooms:** {row['Bathrooms']}")
                
                with col2:
                    st.write(f"**Price:** {row['Price']}")
                    st.write(f"**Monthly Rent:** {row['Monthly Rent']}")
                    st.write(f"**Square Feet:** {row['Sq Ft']}")
                
                with col3:
                    st.write(f"**Cap Rate:** {row['Cap Rate']}")
                    st.write(f"**Cash Flow:** {row['Cash Flow']}")
                    st.write(f"**Added:** {row['Added']}")
                
                with col4:
                    if st.button(f"🗑️ Delete", key=f"delete_{row['ID']}"):
                        if delete_property(user_id, row['ID']):
                            st.rerun()
        
        # Export option
        csv = filtered_df.drop(['ID'], axis=1).to_csv(index=False)
        st.download_button(
            label="📥 Download Portfolio Data (CSV)",
            data=csv,
            file_name=f"portfolio_data_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

