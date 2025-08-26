import streamlit as st
from datetime import datetime, timezone
from typing import Dict
import plotly.express as px
import plotly.graph_objects as go
import datetime

# ------------------------
# Property Analysis & Visualization
# ------------------------
def analyze_property(property_data: Dict) -> Dict:
    """Comprehensive property analysis"""
    analysis = {
        'basic_info': extract_basic_info(property_data),
        'financial_metrics': calculate_financial_metrics(property_data),
        'market_analysis': perform_market_analysis(property_data),
        'investment_score': calculate_investment_score(property_data)
    }
    return analysis

def extract_basic_info(data: Dict) -> Dict:
    """Extract basic property information"""
    return {
        'address': data.get('address', 'N/A'),
        'city': data.get('city', 'N/A'),
        'state': data.get('state', 'N/A'),
        'zip_code': data.get('zipCode', 'N/A'),
        'property_type': data.get('propertyType', 'N/A'),
        'bedrooms': data.get('bedrooms', 0),
        'bathrooms': data.get('bathrooms', 0),
        'square_feet': data.get('squareFootage', 0),
        'lot_size': data.get('lotSize', 0),
        'year_built': data.get('yearBuilt', 'N/A')
    }

def calculate_financial_metrics(data: Dict) -> Dict:
    """Calculate financial metrics and investment potential"""
    price = data.get('price', 0) or data.get('lastSalePrice', 0)
    rent_estimate = data.get('rentEstimate', {}).get('rent', 0) if isinstance(data.get('rentEstimate'), dict) else 0
    
    if price and rent_estimate:
        monthly_rent = rent_estimate
        annual_rent = monthly_rent * 12
        
        # Calculate key metrics
        cap_rate = (annual_rent / price) * 100 if price > 0 else 0
        price_to_rent = price / annual_rent if annual_rent > 0 else 0
        cash_flow = monthly_rent - (price * 0.004)  # Rough estimate with 4% monthly expenses
        
        return {
            'price': price,
            'monthly_rent': monthly_rent,
            'annual_rent': annual_rent,
            'cap_rate': round(cap_rate, 2),
            'price_to_rent_ratio': round(price_to_rent, 2),
            'estimated_cash_flow': round(cash_flow, 2),
            'roi_estimate': round((cash_flow * 12 / (price * 0.2)) * 100, 2) if price > 0 else 0  # Assume 20% down
        }
    
    return {
        'price': price,
        'monthly_rent': rent_estimate,
        'annual_rent': rent_estimate * 12,
        'cap_rate': 0,
        'price_to_rent_ratio': 0,
        'estimated_cash_flow': 0,
        'roi_estimate': 0
    }

def perform_market_analysis(data: Dict) -> Dict:
    """Analyze market conditions and comparables"""
    # This would typically involve additional API calls to get comparable properties
    # For now, we'll use available data to provide basic market insights
    
    return {
        'neighborhood': data.get('neighborhood', 'N/A'),
        'price_per_sqft': round(data.get('price', 0) / data.get('squareFootage', 1), 2) if data.get('squareFootage') else 0,
        'market_status': determine_market_status(data),
        'appreciation_potential': analyze_appreciation_potential(data)
    }

def determine_market_status(data: Dict) -> str:
    """Determine market status based on available data"""
    # This is a simplified analysis - in reality, you'd want more market data
    price_per_sqft = data.get('price', 0) / data.get('squareFootage', 1) if data.get('squareFootage') else 0
    
    if price_per_sqft > 200:
        return "Hot Market"
    elif price_per_sqft > 100:
        return "Balanced Market"
    else:
        return "Buyer's Market"

def analyze_appreciation_potential(data: Dict) -> str:
    """Analyze appreciation potential"""
    year_built = data.get('yearBuilt', 2000)
    current_year = datetime.datetime.now().year
    property_age = current_year - year_built if isinstance(year_built, int) else 20
    
    if property_age < 10:
        return "High"
    elif property_age < 30:
        return "Moderate"
    else:
        return "Low"

def calculate_investment_score(data: Dict) -> Dict:
    """Calculate overall investment score"""
    metrics = calculate_financial_metrics(data)
    market = perform_market_analysis(data)
    
    # Simple scoring algorithm
    score = 0
    factors = []
    
    # Cap rate scoring
    cap_rate = metrics.get('cap_rate', 0)
    if cap_rate > 8:
        score += 25
        factors.append("Excellent cap rate")
    elif cap_rate > 6:
        score += 15
        factors.append("Good cap rate")
    elif cap_rate > 4:
        score += 10
        factors.append("Fair cap rate")
    
    # Cash flow scoring
    cash_flow = metrics.get('estimated_cash_flow', 0)
    if cash_flow > 300:
        score += 25
        factors.append("Strong cash flow")
    elif cash_flow > 100:
        score += 15
        factors.append("Positive cash flow")
    elif cash_flow > 0:
        score += 10
        factors.append("Break-even cash flow")
    
    # Market status scoring
    if market.get('market_status') == "Buyer's Market":
        score += 20
        factors.append("Favorable market conditions")
    elif market.get('market_status') == "Balanced Market":
        score += 15
        factors.append("Stable market conditions")
    
    # Appreciation potential
    if market.get('appreciation_potential') == "High":
        score += 15
        factors.append("High appreciation potential")
    elif market.get('appreciation_potential') == "Moderate":
        score += 10
        factors.append("Moderate appreciation potential")
    
    # Property condition (age-based)
    property_age = datetime.datetime.now().year - data.get('yearBuilt', 2000) if isinstance(data.get('yearBuilt'), int) else 20
    if property_age < 10:
        score += 15
        factors.append("New property")
    elif property_age < 30:
        score += 10
        factors.append("Well-maintained age")
    
    # Determine grade
    if score >= 80:
        grade = "A+"
        recommendation = "Excellent investment opportunity"
    elif score >= 70:
        grade = "A"
        recommendation = "Strong investment potential"
    elif score >= 60:
        grade = "B+"
        recommendation = "Good investment with some caution"
    elif score >= 50:
        grade = "B"
        recommendation = "Fair investment opportunity"
    elif score >= 40:
        grade = "C"
        recommendation = "Marginal investment - proceed carefully"
    else:
        grade = "D"
        recommendation = "Poor investment - not recommended"
    
    return {
        'score': score,
        'grade': grade,
        'recommendation': recommendation,
        'positive_factors': factors
    }

def display_property_analysis(analysis: Dict, property_data: Dict):
    """Display comprehensive property analysis"""
    
    # Header
    basic = analysis['basic_info']
    st.markdown(f"""
    <div class="property-card">
        <h3>🏠 {basic['address']}</h3>
        <p><strong>{basic['city']}, {basic['state']} {basic['zip_code']}</strong></p>
        <p>{basic['bedrooms']} bed • {basic['bathrooms']} bath • {basic['square_feet']} sq ft • Built {basic['year_built']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Investment Score
    score_data = analysis['investment_score']
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown(f"""
        <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    border-radius: 15px; color: white; margin: 1rem 0;">
            <h2 style="margin: 0; font-size: 3rem;">{score_data['grade']}</h2>
            <p style="margin: 0.5rem 0; font-size: 1.2rem;">Investment Score: {score_data['score']}/100</p>
            <p style="margin: 0; opacity: 0.9;">{score_data['recommendation']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Financial Metrics
    st.subheader("💰 Financial Analysis")
    financial = analysis['financial_metrics']
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Property Price", f"${financial['price']:,.0f}")
    with col2:
        st.metric("Monthly Rent", f"${financial['monthly_rent']:,.0f}")
    with col3:
        st.metric("Cap Rate", f"{financial['cap_rate']}%")
    with col4:
        st.metric("Cash Flow", f"${financial['estimated_cash_flow']:,.0f}")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Annual Rent", f"${financial['annual_rent']:,.0f}")
    with col2:
        st.metric("Price/Rent Ratio", f"{financial['price_to_rent_ratio']:.1f}")
    with col3:
        st.metric("ROI Estimate", f"{financial['roi_estimate']}%")
    with col4:
        st.metric("Price/Sq Ft", f"${analysis['market_analysis']['price_per_sqft']:.0f}")
    
    # Market Analysis
    st.subheader("📊 Market Analysis")
    market = analysis['market_analysis']
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info(f"**Neighborhood:** {market['neighborhood']}")
    with col2:
        status_color = {"Hot Market": "🔥", "Balanced Market": "⚖️", "Buyer's Market": "💰"}
        st.info(f"**Market Status:** {status_color.get(market['market_status'], '📈')} {market['market_status']}")
    with col3:
        potential_color = {"High": "🚀", "Moderate": "📈", "Low": "📉"}
        st.info(f"**Appreciation:** {potential_color.get(market['appreciation_potential'], '📊')} {market['appreciation_potential']}")
    
    # Positive Factors
    if score_data['positive_factors']:
        st.subheader("✅ Positive Investment Factors")
        factors_text = " • ".join(score_data['positive_factors'])
        st.success(factors_text)
    
    # Visualizations
    create_property_charts(financial, property_data)

def create_property_charts(financial_data: Dict, property_data: Dict):
    """Create visualizations for property analysis"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Cash Flow Breakdown
        if financial_data['monthly_rent'] > 0:
            estimated_expenses = financial_data['price'] * 0.004 if financial_data['price'] else 0
            
            fig = go.Figure(data=[
                go.Bar(
                    x=['Monthly Income', 'Estimated Expenses', 'Net Cash Flow'],
                    y=[financial_data['monthly_rent'], estimated_expenses, financial_data['estimated_cash_flow']],
                    marker_color=['green', 'red', 'blue']
                )
            ])
            fig.update_layout(title="💰 Monthly Cash Flow Breakdown", yaxis_title="Amount ($)")
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Investment Metrics Radar
        metrics = [
            financial_data['cap_rate'] * 10,  # Scale up for visibility
            min(financial_data['roi_estimate'], 100),
            max(0, min(100, (financial_data['estimated_cash_flow'] + 500) / 10)),  # Scale cash flow
            max(0, min(100, 100 - financial_data['price_to_rent_ratio'] * 2))  # Inverse price/rent ratio
        ]
        
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=metrics,
            theta=['Cap Rate', 'ROI', 'Cash Flow', 'Affordability'],
            fill='toself',
            name='Property Metrics'
        ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            title="📊 Investment Metrics Overview",
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)

