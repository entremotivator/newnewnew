# Real Estate Intelligence Portal - Refactored

A comprehensive property analysis and investment management platform built with Streamlit.

## Features

- **Property Search & Analysis**: Search properties using RentCast API with detailed financial analysis
- **Portfolio Management**: Track and analyze your property investments
- **Order Management**: View and manage WooCommerce orders
- **Market Analysis**: Understand market trends and comparable properties
- **User Authentication**: Secure WordPress JWT authentication
- **Usage Tracking**: Monitor API usage with Supabase integration

## Architecture

The application has been refactored into a modular structure:

```
real_estate_app/
├── main.py                 # Main application entry point
├── pages/                  # Page components
│   ├── property_search.py  # Property search and analysis
│   ├── portfolio.py        # Portfolio management
│   ├── orders.py          # Order management
│   ├── market_analysis.py # Market analysis tools
│   └── settings.py        # Settings and configuration
├── utils/                  # Utility modules
│   ├── auth.py            # Authentication utilities
│   ├── config.py          # Configuration management
│   ├── rentcast_api.py    # RentCast API integration (property lookup only)
│   ├── woocommerce.py     # WooCommerce integration
│   ├── usage.py           # Usage tracking
│   ├── property_management.py  # Property CRUD operations
│   └── property_analysis.py    # Property analysis and visualization
└── requirements.txt       # Python dependencies
```

## Key Changes

1. **Modular Structure**: Separated concerns into dedicated modules
2. **RentCast API**: Isolated to utils/rentcast_api.py with property lookup only (no rent estimates)
3. **Authentication**: Preserved exact WordPress JWT authentication mechanism
4. **Page Components**: Each page is now a separate module for better maintainability
5. **Utility Functions**: Common functionality extracted to reusable utilities

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure Streamlit secrets in `.streamlit/secrets.toml`:
```toml
[wordpress]
base_url = "your_wordpress_url"
username = "your_username"
password = "your_password"

[woocommerce]
consumer_key = "your_consumer_key"
consumer_secret = "your_consumer_secret"

[rentcast]
api_key = "your_rentcast_api_key"

[supabase]
url = "your_supabase_url"
key = "your_supabase_key"
```

## Usage

Run the application:
```bash
streamlit run main.py
```

## API Integration

### RentCast API
- **Endpoint**: Property lookup only
- **Features**: Property data fetching with retry logic and error handling
- **Caching**: 2-hour cache for property data stability

### WordPress/WooCommerce
- **Authentication**: JWT token-based authentication
- **Orders**: Fetch and display customer orders
- **User Management**: Session caching with Supabase

### Supabase
- **User Sessions**: Cache user authentication data
- **Properties**: Store and manage saved properties
- **Usage Tracking**: Monitor API usage and limits

## Security

- All authentication mechanisms preserved from original implementation
- API keys stored securely in Streamlit secrets
- User sessions managed with Supabase
- No sensitive data logged or exposed

