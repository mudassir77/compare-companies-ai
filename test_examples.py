"""
Test script with example target companies for testing the comparable finder.
"""

from comparable_finder import find_comparables

# Example 1: Huron Consulting Group (from requirements)
huron = {
    "name": "Huron Consulting Group Inc.",
    "url": "http://www.huronconsultinggroup.com/",
    "business_description": """Huron Consulting Group Inc. provides consultancy and managed services in the United States and internationally. It operates through three segments: Healthcare, Education, and Commercial. The company offers financial and operational performance improvement consulting services; digital offerings; spanning technology and analytic-related services, including enterprise health record, enterprise resource planning, enterprise performance management, customer relationship management, data management, artificial intelligence and automation, technology managed services, and a portfolio of software products; organizational transformation; revenue cycle managed services and outsourcing; financial and capital advisory consulting; and strategy and innovation consulting. It also provides digital offerings; spanning technology and analytic-related services; technology managed services; research-focused consulting; managed services; and global philanthropy consulting services, as well as Huron Research product suite, a software suite designed to facilitate and enhance research administration service delivery and compliance. In addition, the company offers digital services, software products, financial capital advisory services, and Commercial consulting.""",
    "primary_industry_classification": "Research and Consulting Services"
}

# Example 2: A SaaS company (for testing different industry)
saas_company = {
    "name": "Example SaaS Corp",
    "url": "https://example-saas.com",
    "business_description": "Provides cloud-based project management and collaboration software for mid-market businesses. Serves primarily technology, professional services, and manufacturing industries.",
    "primary_industry_classification": "Software and Information Services"
}

# Example 3: A healthcare services company
healthcare_services = {
    "name": "Example Healthcare Services",
    "url": "https://example-healthcare.com",
    "business_description": "Provides revenue cycle management and patient engagement solutions to hospitals and health systems. Offers software and services for billing, collections, and patient communication.",
    "primary_industry_classification": "Healthcare Services"
}


def test_huron():
    """Test with Huron Consulting Group."""
    print("=" * 80)
    print("Testing with Huron Consulting Group Inc.")
    print("=" * 80)
    print()
    
    try:
        df = find_comparables(huron, output_file="huron_comparables.csv")
        print(f"\n✓ Successfully found {len(df)} comparable companies")
        print("\nResults:")
        print(df[['name', 'ticker', 'exchange', 'SIC_industry']].to_string(index=False))
        return True
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_custom_company(name, url, description, industry):
    """Test with a custom company."""
    target = {
        "name": name,
        "url": url,
        "business_description": description,
        "primary_industry_classification": industry
    }
    
    print("=" * 80)
    print(f"Testing with {name}")
    print("=" * 80)
    print()
    
    try:
        output_file = f"{name.lower().replace(' ', '_')}_comparables.csv"
        df = find_comparables(target, output_file=output_file)
        print(f"\n✓ Successfully found {len(df)} comparable companies")
        print("\nResults:")
        print(df[['name', 'ticker', 'exchange']].to_string(index=False))
        return True
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "huron":
            test_huron()
        elif sys.argv[1] == "saas":
            test_custom_company(**saas_company)
        elif sys.argv[1] == "healthcare":
            test_custom_company(**healthcare_services)
        else:
            print("Usage: python test_examples.py [huron|saas|healthcare]")
    else:
        # Default: test with Huron
        test_huron()

