# Solution Overview

## Architecture

The solution uses an **optimized single-call approach** to find and validate comparable companies:

1. **Comprehensive Company Discovery**: Uses OpenAI GPT-5.1 in a single API call to:
   - Identify 8-12 potential comparable companies
   - Enrich each with complete details (URL, business activity, customer segments, SIC industry)
   - Validate each company using similarity scoring (products/services and customer segments)
   - Return only validated companies (similarity scores ≥ 6/10)
2. **Optional Follow-up**: If needed, makes one additional call to find more companies
3. **Export**: Outputs results to CSV or Parquet format


## Key Features

### 1. LLM Integration
- Uses OpenAI GPT-5.1 for comprehensive company matching, enrichment, and validation
- Single comprehensive API call handles all steps (find, enrich, validate) simultaneously
- Implements retry logic with exponential backoff for API reliability

### 2. Validation Logic
The solution implements two validation checks that mirror how an investment analyst would manually validate comparables:

**Check 1: Products/Services Similarity**
- Uses LLM to score similarity (0-10) of products/services between target and comparable
- Requires minimum score of 6/10

**Check 2: Customer Segment Similarity**
- Uses LLM to score similarity (0-10) of customer segments/industries served
- Requires minimum score of 6/10

Both checks are combined with a final boolean validation decision and reasoning.

### 3. Error Handling

The solution handles several realistic failure scenarios:

**Scenario 1: LLM Returns Invalid JSON**
- **Problem**: LLM sometimes returns text with markdown formatting or extra text
- **Solution**: Robust JSON extraction using regex to find JSON objects, handles markdown code blocks, and falls back to a secondary LLM call to extract structured data

**Scenario 2: Insufficient Companies Found**
- **Problem**: Initial search returns fewer than 3 companies
- **Solution**: Automatic retry with expanded search criteria, considers adjacent markets and similar business models

**Scenario 3: API Rate Limits / Network Errors**
- **Problem**: OpenAI API rate limits or temporary network issues
- **Solution**: Uses `tenacity` library with exponential backoff (3 retries, 4-10 second delays)

**Scenario 4: Missing Company Data**
- **Problem**: Cannot enrich data for a company (missing URL, business details, etc.)
- **Solution**: Graceful degradation - includes company with "Not available" placeholders, continues processing other companies

**Scenario 5: Validation Failures**
- **Problem**: Validation API call fails or returns invalid response
- **Solution**: Defaults to including the company (to avoid false negatives), logs warning

### 4. Business Logic

- **Focus on Main Segment**: For multi-segment companies, focuses on primary segment (as per requirements)
- **No Hard-coding**: Works for any target company, no company-specific logic
- **Range Enforcement**: Ensures 3-10 companies in final output
- **Deduplication**: Removes duplicate companies by name

## Usage

### Basic Usage
```python
from comparable_finder import find_comparables

target = {
    "name": "Company Name",
    "url": "https://company.com",
    "business_description": "Company description...",
    "primary_industry_classification": "Industry Name"
}

df = find_comparables(target, output_file="comparables.csv")
```

### Command Line
```bash
python comparable_finder.py
```

### Testing
```bash
python test_examples.py huron
python test_examples.py saas
python test_examples.py healthcare
```

## Output Format

CSV/Parquet file with columns:
- `name`: Company name
- `url`: Company website URL
- `exchange`: Stock exchange (NASDAQ, NYSE, etc.)
- `ticker`: Ticker symbol
- `business_activity`: Detailed products/services description
- `customer_segment`: Major customer segments
- `SIC_industry`: SIC industry classification(s)

## Testing

The solution includes:
1. **Huron Consulting Group test case** (from requirements)
2. **Additional test examples** for different industries (SaaS, Healthcare)
3. **Error scenario testing** through retry and fallback mechanisms

## Design Decisions

1. **GPT-5.1 for Comprehensive Processing**: Uses GPT-5.1 for all operations in a single comprehensive call (finds, enriches, validates simultaneously)
2. **Single-Call Optimization**: Combines all steps into one API call to reduce cost and latency (1-2 calls vs 20+)
3. **Temperature Settings**: Low temperature (0.3) for consistency in matching and validation
4. **Rate Limiting**: With only 1-2 calls, rate limits are much less of a concern
5. **Validation Thresholds**: 6/10 minimum similarity scores (configurable) - validated during the same API call
6. **Graceful Degradation**: Continues processing even if some companies fail, ensures minimum output
7. **Model Flexibility**: Supports GPT-5, GPT-5.1, or other OpenAI models via configuration

## Performance Improvements

**Optimization Completed**:
- ✅ Reduced API calls from 20+ to 1-2 total
- ✅ Single comprehensive call handles find, enrich, and validate
- ✅ Upgraded to GPT-5.1 for better quality and efficiency
- ✅ Dramatically reduced execution time and cost

## Future Enhancements

Potential improvements (not implemented due to scope):
- Integration with financial data APIs (Yahoo Finance, Alpha Vantage) for automatic ticker/exchange lookup
- Web scraping for company websites to enrich data
- Parallel processing for multiple target companies
- More sophisticated validation using multiple criteria
- Integration with SEC EDGAR API for 10-K data

