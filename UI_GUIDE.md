# Streamlit UI Guide

## Features

### 1. Input Form with Validation

The UI includes a comprehensive form with the following fields:

- **Company Name** (Required)
  - Minimum 3 characters
  - Validates that field is not empty

- **Website URL** (Required)
  - Validates proper URL format (http:// or https://)
  - Checks for valid domain structure

- **Business Description** (Required)
  - Minimum 50 characters (ensures sufficient context for AI)
  - Maximum 5000 characters
  - Validates that description is meaningful

- **Primary Industry Classification** (Required)
  - Minimum 3 characters
  - SIC industry classification name

### 2. Validation Features

All fields are validated before submission:
- **Real-time validation** on form submission
- **Clear error messages** for each validation failure
- **Prevents submission** until all validations pass
- **Visual feedback** with color-coded error messages

### 3. Results Display

Once comparables are found:
- **Summary metrics** showing:
  - Number of companies found
  - Target company name
  - Industry classification
- **Interactive data table** with all company information
- **Expandable detailed view** for each company

### 4. Download Options

Two download formats available:
- **CSV Download**: Standard comma-separated values file
- **Excel Download**: Formatted Excel file with:
  - Auto-adjusted column widths
  - Professional formatting
  - All company data included

### 5. User Experience

- **Sidebar instructions** for guidance
- **Progress indicators** during processing
- **Success/error messages** with clear feedback
- **Clear results** button to start new searches
- **Responsive design** that works on different screen sizes

## Running the App

```bash
# Activate virtual environment
source venv/bin/activate

# Run Streamlit app
streamlit run app.py
```

The app will open in your default browser at `http://localhost:8501`

## Validation Rules

### Company Name
- ✅ Required field
- ✅ Minimum 3 characters
- ✅ Cannot be empty or whitespace only

### Website URL
- ✅ Required field
- ✅ Must start with http:// or https://
- ✅ Must have valid domain structure
- ✅ Example: `https://www.example.com`

### Business Description
- ✅ Required field
- ✅ Minimum 50 characters (ensures AI has enough context)
- ✅ Maximum 5000 characters
- ✅ Cannot be empty or whitespace only

### Primary Industry Classification
- ✅ Required field
- ✅ Minimum 3 characters
- ✅ Cannot be empty or whitespace only

## Error Handling

The UI gracefully handles:
- **API errors**: Shows clear error messages
- **Validation errors**: Highlights specific field issues
- **Network issues**: Provides retry guidance
- **Empty results**: Shows appropriate messages

## Tips for Best Results

1. **Provide detailed business descriptions**: The more context you give, the better the AI can find true comparables
2. **Use accurate industry classifications**: This helps narrow down the search
3. **Include full company name**: Legal names work best for matching
4. **Verify website URL**: Ensure it's the official company website

