# Comparable Company Finder

A Python program that generates a list of comparable publicly traded companies for a target company using LLM APIs and web research.

## Overview

This tool identifies comparable companies based on:
- Similar products and services
- Similar customer/industry segments

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your OpenAI API key:
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

## Usage

### Streamlit Web UI (Recommended)

Launch the interactive web interface:

```bash
streamlit run app.py
```

The UI provides:
- Form validation for all input fields
- Real-time results display
- Download options (CSV and Excel)
- Detailed company information view

### Python API

```python
from comparable_finder import find_comparables

target_company = {
    "name": "Huron Consulting Group Inc.",
    "url": "http://www.huronconsultinggroup.com/",
    "business_description": "Huron Consulting Group Inc. provides consultancy and managed services...",
    "primary_industry_classification": "Research and Consulting Services"
}

comparables = find_comparables(target_company, output_file="comparables.csv")
```

### Command Line

```bash
python comparable_finder.py
```

## Output

The program generates a CSV or Parquet file containing:
- name: Company name
- url: Company website URL
- exchange: Stock exchange name
- ticker: Ticker symbol
- business_activity: Detailed description of products/services
- customer_segment: Major customer segments
- SIC_industry: SIC industry classification(s)

## Features

- Uses OpenAI API for intelligent company matching
- Validates comparables for product/service and customer segment similarity
- Handles LLM errors, rate limits, and missing data gracefully
- Supports both CSV and Parquet output formats
- Works for any target company (no hard-coding)

## Testing

The code includes a test case for Huron Consulting Group Inc. and can be tested with any company.

