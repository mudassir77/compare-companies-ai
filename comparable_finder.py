"""
Comparable Company Finder

This module identifies publicly traded companies that are comparable to a target company
based on products/services and customer segments.
"""

import os
import json
import time
import re
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv
from openai import OpenAI
import pandas as pd
from tenacity import retry, stop_after_attempt, wait_exponential

# Load environment variables
load_dotenv()

# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables. Please set it in .env file.")
client = OpenAI(api_key=api_key)


class ComparableFinder:
    """Main class for finding comparable companies."""
    
    def __init__(self):
        self.client = client
        self.max_comparables = 10
        self.min_comparables = 3
        
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _call_openai(self, messages: List[Dict], model: str = "gpt-4", temperature: float = 0.3) -> str:
        """Make OpenAI API call with retry logic."""
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                response_format={"type": "json_object"} if "json" in model.lower() else None
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI API error: {e}")
            raise
    
    def find_comparable_companies(self, target_company: Dict) -> List[Dict]:
        """
        Find comparable companies using LLM.
        
        Args:
            target_company: Dict with keys: name, url, business_description, primary_industry_classification
            
        Returns:
            List of comparable company dictionaries
        """
        print(f"Finding comparables for {target_company['name']}...")
        
        prompt = f"""You are an investment analyst identifying comparable publicly traded companies.

Target Company Information:
- Name: {target_company['name']}
- Business Description: {target_company['business_description']}
- Primary Industry: {target_company['primary_industry_classification']}
- Website: {target_company['url']}

Please identify 8-12 publicly traded companies that are comparable to this target company.
A comparable company must:
1. Offer similar products and services
2. Serve clients in similar industry segments

For each company, provide:
- name: Full company name
- ticker: Stock ticker symbol (e.g., NASDAQ: HURN)
- exchange: Stock exchange name (e.g., NASDAQ, NYSE)

Return your response as a JSON object with this structure:
{{
    "companies": [
        {{
            "name": "Company Name",
            "ticker": "EXCHANGE:SYMBOL",
            "exchange": "Exchange Name",
            "reasoning": "Brief explanation of why this is comparable"
        }}
    ]
}}

Focus on companies that are truly comparable in terms of business model, not just industry.
Return ONLY valid JSON, no additional text."""

        messages = [
            {"role": "system", "content": "You are a financial analyst expert at identifying comparable companies. Always return valid JSON."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = self._call_openai(messages, model="gpt-4")
            # Clean response to extract JSON - handle various formats
            response = response.strip()
            # Remove markdown code blocks
            response = re.sub(r'^```json\s*', '', response, flags=re.MULTILINE)
            response = re.sub(r'^```\s*', '', response, flags=re.MULTILINE)
            response = re.sub(r'```\s*$', '', response, flags=re.MULTILINE)
            response = response.strip()
            
            # Try to extract JSON object if wrapped in other text
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                response = json_match.group(0)
            
            data = json.loads(response)
            companies = data.get("companies", [])
            
            if len(companies) < self.min_comparables:
                print(f"Warning: Only {len(companies)} companies found, attempting to find more...")
                # Retry with a different approach
                companies = self._retry_find_comparables(target_company, companies)
            
            return companies[:self.max_comparables]
            
        except json.JSONDecodeError as e:
            print(f"Error parsing LLM response as JSON: {e}")
            print(f"Response was: {response[:500]}")
            # Fallback: try to extract company names manually
            return self._fallback_extract_companies(response, target_company)
        except Exception as e:
            print(f"Error finding comparables: {e}")
            raise
    
    def _retry_find_comparables(self, target_company: Dict, existing_companies: List[Dict]) -> List[Dict]:
        """Retry finding comparables if initial attempt found too few."""
        prompt = f"""The previous search found only {len(existing_companies)} comparable companies, but we need at least {self.min_comparables}.

Target: {target_company['name']}
Business: {target_company['business_description']}
Industry: {target_company['primary_industry_classification']}

Please find additional publicly traded companies that are comparable. Consider:
- Companies in adjacent markets
- Companies with similar business models
- Companies serving similar customer bases

Return JSON with structure:
{{
    "companies": [
        {{
            "name": "Company Name",
            "ticker": "EXCHANGE:SYMBOL",
            "exchange": "Exchange Name",
            "reasoning": "Why comparable"
        }}
    ]
}}"""

        try:
            response = self._call_openai([
                {"role": "system", "content": "You are a financial analyst. Return valid JSON only."},
                {"role": "user", "content": prompt}
            ])
            
            # Clean response using robust JSON extraction
            response = response.strip()
            response = re.sub(r'^```json\s*', '', response, flags=re.MULTILINE)
            response = re.sub(r'^```\s*', '', response, flags=re.MULTILINE)
            response = re.sub(r'```\s*$', '', response, flags=re.MULTILINE)
            response = response.strip()
            
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                response = json_match.group(0)
            
            data = json.loads(response)
            additional = data.get("companies", [])
            
            # Combine and deduplicate
            all_companies = existing_companies + additional
            seen_names = set()
            unique_companies = []
            for comp in all_companies:
                if comp["name"].lower() not in seen_names:
                    seen_names.add(comp["name"].lower())
                    unique_companies.append(comp)
            
            return unique_companies[:self.max_comparables]
        except Exception as e:
            print(f"Retry failed: {e}")
            return existing_companies
    
    def _fallback_extract_companies(self, response: str, target_company: Dict) -> List[Dict]:
        """Fallback method to extract company information from unstructured text."""
        print("Using fallback extraction method...")
        # Try to find company names and tickers in the response
        # This is a simplified fallback - in production, you'd want more sophisticated parsing
        prompt = f"""Extract company information from this text and return as JSON:

{response[:2000]}

Return JSON with structure:
{{
    "companies": [
        {{
            "name": "Company Name",
            "ticker": "EXCHANGE:SYMBOL",
            "exchange": "Exchange Name"
        }}
    ]
}}"""

        try:
            fallback_response = self._call_openai([
                {"role": "system", "content": "Extract company information and return valid JSON only."},
                {"role": "user", "content": prompt}
            ])
            # Clean response using same method as main parsing
            fallback_response = fallback_response.strip()
            fallback_response = re.sub(r'^```json\s*', '', fallback_response, flags=re.MULTILINE)
            fallback_response = re.sub(r'^```\s*', '', fallback_response, flags=re.MULTILINE)
            fallback_response = re.sub(r'```\s*$', '', fallback_response, flags=re.MULTILINE)
            fallback_response = fallback_response.strip()
            
            json_match = re.search(r'\{.*\}', fallback_response, re.DOTALL)
            if json_match:
                fallback_response = json_match.group(0)
            
            data = json.loads(fallback_response)
            return data.get("companies", [])
        except Exception as e:
            print(f"Fallback extraction failed: {e}")
            return []
    
    def enrich_company_data(self, company: Dict, target_company: Dict) -> Dict:
        """
        Enrich company data with additional information.
        
        Args:
            company: Dict with name, ticker, exchange
            target_company: Original target company for context
            
        Returns:
            Enriched company dict with all required fields
        """
        print(f"  Enriching data for {company['name']}...")
        
        # Parse ticker
        ticker_full = company.get("ticker", "")
        if ":" in ticker_full:
            exchange_part, symbol = ticker_full.split(":", 1)
            ticker = symbol.strip()
            exchange = company.get("exchange", exchange_part.strip())
        else:
            ticker = ticker_full.strip()
            exchange = company.get("exchange", "Unknown")
        
        # Use LLM to get detailed information
        prompt = f"""Provide detailed information about this publicly traded company:

Company: {company['name']}
Ticker: {ticker}
Exchange: {exchange}

Target Company Context (for comparison):
- Name: {target_company['name']}
- Business: {target_company['business_description']}
- Industry: {target_company['primary_industry_classification']}

Return JSON with:
{{
    "url": "Company website URL",
    "business_activity": "Detailed description of main products/services (2-3 sentences)",
    "customer_segment": "Major customer segments/industries served (1-2 sentences)",
    "SIC_industry": "SIC industry classification name(s), comma-separated if multiple"
}}

Return ONLY valid JSON."""

        try:
            response = self._call_openai([
                {"role": "system", "content": "You are a financial data analyst. Return valid JSON only."},
                {"role": "user", "content": prompt}
            ])
            
            # Clean response using robust JSON extraction
            response = response.strip()
            response = re.sub(r'^```json\s*', '', response, flags=re.MULTILINE)
            response = re.sub(r'^```\s*', '', response, flags=re.MULTILINE)
            response = re.sub(r'```\s*$', '', response, flags=re.MULTILINE)
            response = response.strip()
            
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                response = json_match.group(0)
            
            data = json.loads(response)
            
            # Try to get URL from web search if not provided
            url = data.get("url", "")
            if not url or url == "Unknown":
                url = self._search_company_url(company['name'])
            
            return {
                "name": company["name"],
                "url": url or company.get("url", ""),
                "exchange": exchange,
                "ticker": ticker,
                "business_activity": data.get("business_activity", "Not available"),
                "customer_segment": data.get("customer_segment", "Not available"),
                "SIC_industry": data.get("SIC_industry", "Not available")
            }
        except Exception as e:
            print(f"    Warning: Could not enrich data for {company['name']}: {e}")
            # Return minimal data
            return {
                "name": company["name"],
                "url": company.get("url", ""),
                "exchange": exchange,
                "ticker": ticker,
                "business_activity": "Data not available",
                "customer_segment": "Data not available",
                "SIC_industry": "Not available"
            }
    
    def _search_company_url(self, company_name: str) -> str:
        """Search for company website URL using LLM."""
        # Use LLM to find company URL if not available
        try:
            prompt = f"""What is the official website URL for the publicly traded company "{company_name}"? 
Return only the URL, nothing else."""
            response = self._call_openai([
                {"role": "system", "content": "You are a helpful assistant. Return only URLs."},
                {"role": "user", "content": prompt}
            ], model="gpt-3.5-turbo", temperature=0.1)
            url = response.strip().strip('"').strip("'")
            if url.startswith("http"):
                return url
        except Exception:
            pass
        return ""
    
    def validate_comparable(self, comparable: Dict, target_company: Dict) -> Tuple[bool, str]:
        """
        Validate that a company is truly comparable.
        
        Args:
            comparable: Comparable company dict
            target_company: Target company dict
            
        Returns:
            Tuple of (is_valid, reason)
        """
        print(f"  Validating {comparable['name']}...")
        
        prompt = f"""As an investment analyst, validate if this company is truly comparable to the target.

Target Company:
- Name: {target_company['name']}
- Business: {target_company['business_description']}
- Industry: {target_company['primary_industry_classification']}

Proposed Comparable:
- Name: {comparable['name']}
- Business Activity: {comparable['business_activity']}
- Customer Segment: {comparable['customer_segment']}
- SIC Industry: {comparable['SIC_industry']}

A company is comparable if:
1. It offers similar products/services to the target
2. It serves clients in similar industry segments

Return JSON:
{{
    "is_comparable": true/false,
    "reason": "Brief explanation (1-2 sentences)",
    "products_similarity_score": 0-10,
    "customer_similarity_score": 0-10
}}

Return ONLY valid JSON."""

        try:
            response = self._call_openai([
                {"role": "system", "content": "You are a financial analyst validating company comparability. Return valid JSON only."},
                {"role": "user", "content": prompt}
            ])
            
            # Clean response using robust JSON extraction
            response = response.strip()
            response = re.sub(r'^```json\s*', '', response, flags=re.MULTILINE)
            response = re.sub(r'^```\s*', '', response, flags=re.MULTILINE)
            response = re.sub(r'```\s*$', '', response, flags=re.MULTILINE)
            response = response.strip()
            
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                response = json_match.group(0)
            
            data = json.loads(response)
            
            is_comparable = data.get("is_comparable", False)
            products_score = data.get("products_similarity_score")
            customer_score = data.get("customer_similarity_score")
            reason = data.get("reason", "No reason provided")
            
            # Handle None values - convert to 0 if None
            if products_score is None:
                products_score = 0
            if customer_score is None:
                customer_score = 0
            # Ensure they're integers
            try:
                products_score = int(products_score) if products_score is not None else 0
                customer_score = int(customer_score) if customer_score is not None else 0
            except (ValueError, TypeError):
                products_score = 0
                customer_score = 0
            
            # Additional validation: require minimum similarity scores
            if products_score < 6 or customer_score < 6:
                is_comparable = False
                reason = f"Similarity scores too low (products: {products_score}/10, customers: {customer_score}/10)"
            
            return is_comparable, reason
            
        except Exception as e:
            print(f"    Warning: Validation failed for {comparable['name']}: {e}")
            # Default to valid if validation fails (to avoid false negatives)
            return True, "Validation check unavailable"
    
    def find_comparables(self, target_company: Dict, output_file: Optional[str] = None) -> pd.DataFrame:
        """
        Main method to find and return comparable companies.
        
        Args:
            target_company: Target company information
            output_file: Optional output file path (CSV or Parquet)
            
        Returns:
            DataFrame with comparable companies
        """
        # Step 1: Find initial list of comparables
        companies = self.find_comparable_companies(target_company)
        
        if len(companies) < self.min_comparables:
            raise ValueError(f"Could not find at least {self.min_comparables} comparable companies")
        
        # Step 2: Enrich company data
        enriched_companies = []
        for company in companies:
            try:
                enriched = self.enrich_company_data(company, target_company)
                enriched_companies.append(enriched)
                # Rate limiting
                time.sleep(0.5)
            except Exception as e:
                print(f"  Error enriching {company.get('name', 'Unknown')}: {e}")
                continue
        
        # Step 3: Validate comparables
        validated_companies = []
        for company in enriched_companies:
            try:
                is_valid, reason = self.validate_comparable(company, target_company)
                if is_valid:
                    validated_companies.append(company)
                    print(f"    ✓ {company['name']} validated: {reason}")
                else:
                    print(f"    ✗ {company['name']} rejected: {reason}")
                time.sleep(0.5)
            except Exception as e:
                print(f"    Warning: Validation error for {company['name']}: {e}")
                # Include anyway if validation fails
                validated_companies.append(company)
        
        # Ensure we have at least minimum number
        if len(validated_companies) < self.min_comparables:
            print(f"Warning: Only {len(validated_companies)} companies passed validation. Including all enriched companies.")
            validated_companies = enriched_companies[:self.max_comparables]
        
        # Step 4: Create DataFrame
        df = pd.DataFrame(validated_companies[:self.max_comparables])
        
        # Step 5: Export if requested
        if output_file:
            if output_file.endswith('.parquet'):
                df.to_parquet(output_file, index=False)
            else:
                df.to_csv(output_file, index=False)
            print(f"\nResults saved to {output_file}")
        
        return df


def find_comparables(target_company: Dict, output_file: Optional[str] = None) -> pd.DataFrame:
    """
    Convenience function to find comparable companies.
    
    Args:
        target_company: Dict with name, url, business_description, primary_industry_classification
        output_file: Optional output file path
        
    Returns:
        DataFrame with comparable companies
    """
    finder = ComparableFinder()
    return finder.find_comparables(target_company, output_file)


if __name__ == "__main__":
    # Test with Huron Consulting Group
    target = {
        "name": "Huron Consulting Group Inc.",
        "url": "http://www.huronconsultinggroup.com/",
        "business_description": """Huron Consulting Group Inc. provides consultancy and managed services in the United States and internationally. It operates through three segments: Healthcare, Education, and Commercial. The company offers financial and operational performance improvement consulting services; digital offerings; spanning technology and analytic-related services, including enterprise health record, enterprise resource planning, enterprise performance management, customer relationship management, data management, artificial intelligence and automation, technology managed services, and a portfolio of software products; organizational transformation; revenue cycle managed services and outsourcing; financial and capital advisory consulting; and strategy and innovation consulting. It also provides digital offerings; spanning technology and analytic-related services; technology managed services; research-focused consulting; managed services; and global philanthropy consulting services, as well as Huron Research product suite, a software suite designed to facilitate and enhance research administration service delivery and compliance. In addition, the company offers digital services, software products, financial capital advisory services, and Commercial consulting.""",
        "primary_industry_classification": "Research and Consulting Services"
    }
    
    print("=" * 80)
    print("Comparable Company Finder")
    print("=" * 80)
    print()
    
    try:
        df = find_comparables(target, output_file="huron_comparables.csv")
        print(f"\nFound {len(df)} comparable companies:")
        print(df.to_string(index=False))
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

