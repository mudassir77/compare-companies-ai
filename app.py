"""
Streamlit UI for Comparable Company Finder
"""

import streamlit as st
import pandas as pd
from comparable_finder import find_comparables
import re
from io import BytesIO
from typing import Tuple

# Page configuration
st.set_page_config(
    page_title="Comparable Company Finder",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        font-weight: bold;
    }
    .error-message {
        color: #d32f2f;
        font-weight: bold;
        padding: 10px;
        background-color: #ffebee;
        border-radius: 5px;
        margin: 10px 0;
    }
    .success-message {
        color: #2e7d32;
        font-weight: bold;
        padding: 10px;
        background-color: #e8f5e9;
        border-radius: 5px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

def validate_url(url: str) -> Tuple[bool, str]:
    """Validate URL format."""
    if not url:
        return False, "URL is required"
    
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    if not url_pattern.match(url):
        return False, "Please enter a valid URL (e.g., http://example.com or https://example.com)"
    
    return True, ""

def validate_required_field(value: str, field_name: str, min_length: int = 3) -> Tuple[bool, str]:
    """Validate required text fields."""
    if not value or not value.strip():
        return False, f"{field_name} is required"
    
    if len(value.strip()) < min_length:
        return False, f"{field_name} must be at least {min_length} characters"
    
    return True, ""

def validate_business_description(description: str) -> Tuple[bool, str]:
    """Validate business description."""
    if not description or not description.strip():
        return False, "Business description is required"
    
    if len(description.strip()) < 50:
        return False, "Business description must be at least 50 characters to provide sufficient context"
    
    if len(description.strip()) > 5000:
        return False, "Business description is too long (maximum 5000 characters)"
    
    return True, ""

def to_excel(df: pd.DataFrame) -> BytesIO:
    """Convert DataFrame to Excel file in memory."""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Comparable Companies')
        # Auto-adjust column widths
        worksheet = writer.sheets['Comparable Companies']
        from openpyxl.utils import get_column_letter
        for idx, col in enumerate(df.columns, 1):
            max_length = max(
                df[col].astype(str).apply(len).max(),
                len(str(col))
            )
            column_letter = get_column_letter(idx)
            worksheet.column_dimensions[column_letter].width = min(max_length + 2, 50)
    output.seek(0)
    return output

def main():
    # Header
    st.markdown('<div class="main-header">🏢 Comparable Company Finder</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Find publicly traded companies comparable to your target company</div>', unsafe_allow_html=True)
    
    # Sidebar with instructions
    with st.sidebar:
        st.header("📋 Instructions")
        st.markdown("""
        **Fill in the form with:**
        1. **Company Name**: Full legal name of the target company
        2. **Website URL**: Official company website
        3. **Business Description**: Detailed description of products/services
        4. **Primary Industry**: SIC industry classification
        
        **The tool will:**
        - Find 3-10 comparable publicly traded companies
        - Validate comparability based on products/services and customer segments
        - Generate a detailed report with all company information
        """)
        
        st.header("ℹ️ About")
        st.markdown("""
        This tool uses AI to identify comparable companies based on:
        - Similar products and services
        - Similar customer/industry segments
        
        Results are validated to ensure true comparability.
        """)
    
    # Initialize session state
    if 'results_df' not in st.session_state:
        st.session_state.results_df = None
    if 'target_company' not in st.session_state:
        st.session_state.target_company = None
    
    # Main form
    with st.form("company_form", clear_on_submit=False):
        st.header("📝 Target Company Information")
        
        # Company Name
        company_name = st.text_input(
            "Company Name *",
            placeholder="e.g., Huron Consulting Group Inc.",
            help="Enter the full legal name of the target company"
        )
        
        # Website URL
        website_url = st.text_input(
            "Website URL *",
            placeholder="https://www.example.com",
            help="Enter the official company website URL"
        )
        
        # Business Description
        business_description = st.text_area(
            "Business Description *",
            placeholder="Provide a detailed description of the company's products, services, and operations...",
            height=200,
            help="Describe what the company does, its main products/services, and target customers (minimum 50 characters)"
        )
        
        # Primary Industry Classification
        primary_industry = st.text_input(
            "Primary Industry Classification (SIC) *",
            placeholder="e.g., Research and Consulting Services",
            help="Enter the primary SIC industry classification"
        )
        
        # Submit button
        submitted = st.form_submit_button("🔍 Find Comparable Companies", use_container_width=True)
        
        if submitted:
            # Validation
            errors = []
            
            # Validate company name
            is_valid, error_msg = validate_required_field(company_name, "Company name", min_length=3)
            if not is_valid:
                errors.append(error_msg)
            
            # Validate URL
            is_valid, error_msg = validate_url(website_url)
            if not is_valid:
                errors.append(error_msg)
            
            # Validate business description
            is_valid, error_msg = validate_business_description(business_description)
            if not is_valid:
                errors.append(error_msg)
            
            # Validate industry
            is_valid, error_msg = validate_required_field(primary_industry, "Primary industry classification", min_length=3)
            if not is_valid:
                errors.append(error_msg)
            
            # Display errors if any
            if errors:
                for error in errors:
                    st.markdown(f'<div class="error-message">❌ {error}</div>', unsafe_allow_html=True)
            else:
                # All validations passed
                target_company = {
                    "name": company_name.strip(),
                    "url": website_url.strip(),
                    "business_description": business_description.strip(),
                    "primary_industry_classification": primary_industry.strip()
                }
                
                st.session_state.target_company = target_company
                
                # Show progress
                with st.spinner("🔍 Finding comparable companies... This may take a few minutes."):
                    try:
                        # Find comparables
                        results_df = find_comparables(target_company, output_file=None)
                        st.session_state.results_df = results_df
                        
                        st.markdown(f'<div class="success-message">✅ Successfully found {len(results_df)} comparable companies!</div>', unsafe_allow_html=True)
                        st.rerun()
                    except Exception as e:
                        st.markdown(f'<div class="error-message">❌ Error: {str(e)}</div>', unsafe_allow_html=True)
                        st.error(f"Please check your OpenAI API key and try again. Error details: {str(e)}")
    
    # Display results if available
    if st.session_state.results_df is not None and not st.session_state.results_df.empty:
        st.header("📊 Results")
        
        # Display summary
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Companies Found", len(st.session_state.results_df))
        with col2:
            st.metric("Target Company", st.session_state.target_company['name'] if st.session_state.target_company else "N/A")
        with col3:
            st.metric("Industry", st.session_state.target_company['primary_industry_classification'] if st.session_state.target_company else "N/A")
        
        # Display dataframe
        st.subheader("Comparable Companies")
        st.dataframe(
            st.session_state.results_df,
            use_container_width=True,
            hide_index=True
        )
        
        # Download buttons
        st.subheader("📥 Download Results")
        col1, col2 = st.columns(2)
        
        with col1:
            # CSV download
            csv = st.session_state.results_df.to_csv(index=False)
            st.download_button(
                label="📄 Download as CSV",
                data=csv,
                file_name=f"comparables_{st.session_state.target_company['name'].replace(' ', '_').lower() if st.session_state.target_company else 'results'}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            # Excel download
            excel_file = to_excel(st.session_state.results_df)
            st.download_button(
                label="📊 Download as Excel",
                data=excel_file,
                file_name=f"comparables_{st.session_state.target_company['name'].replace(' ', '_').lower() if st.session_state.target_company else 'results'}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        
        # Detailed view
        with st.expander("🔍 View Detailed Information"):
            for idx, row in st.session_state.results_df.iterrows():
                st.markdown(f"### {row['name']}")
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Ticker:** {row['ticker']}")
                    st.write(f"**Exchange:** {row['exchange']}")
                    st.write(f"**Website:** [{row['url']}]({row['url']})")
                with col2:
                    st.write(f"**SIC Industry:** {row['SIC_industry']}")
                st.write(f"**Business Activity:** {row['business_activity']}")
                st.write(f"**Customer Segment:** {row['customer_segment']}")
                st.divider()
        
        # Clear results button
        if st.button("🔄 Clear Results and Start New Search", use_container_width=True):
            st.session_state.results_df = None
            st.session_state.target_company = None
            st.rerun()

if __name__ == "__main__":
    main()

