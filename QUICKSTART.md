# Quick Start Guide

## Setup (5 minutes)

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up OpenAI API key:**
   Create a `.env` file in the project root:
   ```bash
   echo "OPENAI_API_KEY=your_key_here" > .env
   ```
   Or manually create `.env` and add:
   ```
   OPENAI_API_KEY=sk-your-openai-api-key
   ```

3. **Test the installation:**
   ```bash
   python comparable_finder.py
   ```
   This will run the test case with Huron Consulting Group.

## Basic Usage

### Python Script
```python
from comparable_finder import find_comparables

target = {
    "name": "Your Company Name",
    "url": "https://company.com",
    "business_description": "Detailed description of what the company does...",
    "primary_industry_classification": "Industry Name"
}

# Find comparables and save to CSV
df = find_comparables(target, output_file="my_comparables.csv")

# Or save to Parquet
df = find_comparables(target, output_file="my_comparables.parquet")

# Or just get the DataFrame
df = find_comparables(target)
print(df)
```

### Command Line
```bash
# Run with default test case (Huron)
python comparable_finder.py

# Run test examples
python test_examples.py huron
python test_examples.py saas
python test_examples.py healthcare
```

## Expected Output

The script will:
1. Find 8-12 potential comparable companies
2. Enrich each with detailed information
3. Validate each for true comparability
4. Return 3-10 validated companies
5. Save to CSV/Parquet file

Example output file (`huron_comparables.csv`):
```csv
name,url,exchange,ticker,business_activity,customer_segment,SIC_industry
Accenture plc,https://www.accenture.com,NYSE,ACN,"IT consulting and services...","Technology, healthcare, financial services...","Business Services"
Deloitte Consulting,https://www2.deloitte.com,Private,N/A,"Management consulting...","Various industries...","Business Services"
...
```

## Troubleshooting

### "OPENAI_API_KEY not found"
- Make sure you created a `.env` file
- Check that the file is in the project root directory
- Verify the key format: `OPENAI_API_KEY=sk-...`

### "Could not find at least 3 comparable companies"
- The target company might be in a niche industry
- Try providing more detailed business_description
- Check that primary_industry_classification is accurate

### API Rate Limits
- The script includes automatic retries with backoff
- If you hit rate limits, wait a few minutes and try again
- Consider using a higher-tier OpenAI plan for production use

### JSON Parsing Errors
- The script includes robust error handling for this
- If you see JSON errors, the script will attempt fallback methods
- Check the console output for detailed error messages

## Next Steps

- Review `SOLUTION.md` for architecture details
- Check `test_examples.py` for more usage examples
- Customize validation thresholds in `ComparableFinder.__init__()` if needed

