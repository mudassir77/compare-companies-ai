# Caching & History Feature

## Overview

The Comparable Company Finder now includes local caching to:
- **Speed up repeated searches** - Instant results for previously searched companies
- **Save API costs** - Avoid unnecessary API calls for the same company
- **Preserve history** - View and reload previous searches anytime

## How It Works

### Automatic Caching

1. **Before Processing**: The system checks if results exist in cache for the target company
2. **Cache Key**: Generated from company name + business description (MD5 hash)
3. **If Found**: Results load instantly from local storage (no API calls)
4. **If Not Found**: Normal processing occurs, then results are automatically saved

### Storage Location

- **Directory**: `results_cache/`
- **File**: `results_cache/results_history.json`
- **Format**: JSON file containing all search history

## Features

### 1. Automatic Cache Check

When you submit a search:
- ✅ System checks cache first
- ✅ If found: Instant load (shows "Found cached results!")
- ✅ If not found: Normal processing, then auto-save

### 2. History Viewer

Access via sidebar button "👁️ View History":
- **Browse all previous searches**
- **Search by company name**
- **View metadata**: Company name, industry, date, count
- **Load previous results** with one click
- **Delete individual entries** or clear all

### 3. Cache Management

- **Load**: Click "📂 Load" to restore previous results
- **Delete**: Remove individual entries
- **Clear All**: Remove all cached results

## Cache Key Generation

The cache key is generated from:
```python
key = MD5(company_name + business_description)
```

This means:
- Same company + same description = Same cache key (instant load)
- Same company + different description = Different cache key (new search)
- Different company = Different cache key (new search)

## Benefits

### Performance
- **Instant results** for cached searches (no waiting)
- **No API calls** for repeated searches
- **Faster workflow** for testing and validation

### Cost Savings
- **Reduced API usage** - Only process new searches
- **Lower costs** - Cache hits don't use OpenAI API
- **Efficient** - Process once, use many times

### User Experience
- **History tracking** - See all previous searches
- **Easy reload** - One-click to restore results
- **No data loss** - Results persist between sessions

## Usage Examples

### Example 1: First Search
1. Enter company information
2. Click "Find Comparable Companies"
3. System processes (takes a few minutes)
4. Results displayed and **automatically saved**

### Example 2: Repeat Search
1. Enter **same** company information
2. Click "Find Comparable Companies"
3. System finds cache → **Instant load!**
4. Results displayed immediately

### Example 3: View History
1. Click "👁️ View History" in sidebar
2. Browse all previous searches
3. Click "📂 Load" on any entry
4. Results restored instantly

## Storage Structure

```json
{
  "cache_key_1": {
    "target_company": {
      "name": "Company Name",
      "url": "https://...",
      "business_description": "...",
      "primary_industry_classification": "..."
    },
    "results": [...],
    "timestamp": "2024-01-01T12:00:00",
    "company_count": 5,
    "cache_key": "cache_key_1"
  }
}
```

## Technical Details

### Files
- `storage.py` - Storage module with all caching functions
- `results_cache/results_history.json` - Cache storage file

### Functions
- `generate_cache_key()` - Creates unique cache key
- `save_results()` - Saves results to cache
- `get_cached_results()` - Checks and loads from cache
- `get_history_list()` - Gets list of all cached searches
- `load_results()` - Loads specific cached result
- `delete_result()` - Deletes specific cache entry
- `clear_all_results()` - Clears all cache

## Best Practices

1. **Keep cache** - Don't delete unless you need to free space
2. **Use history** - Check previous searches before creating new ones
3. **Cache key** - Understand that same company + same description = cache hit
4. **Storage** - Cache file grows over time; clear if needed

## Troubleshooting

### Cache not working?
- Check `results_cache/` directory exists
- Verify file permissions
- Check JSON file is valid

### Want to force new search?
- Slightly modify business description
- This creates new cache key
- Forces new API processing

### Clear cache?
- Use "Clear All History" button in UI
- Or delete `results_cache/results_history.json` file

