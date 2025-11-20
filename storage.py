"""
Local storage for comparable company results.
"""

import json
import os
import hashlib
from datetime import datetime
from typing import Dict, Optional, List
import pandas as pd

STORAGE_DIR = "results_cache"
STORAGE_FILE = os.path.join(STORAGE_DIR, "results_history.json")


def ensure_storage_dir():
    """Create storage directory if it doesn't exist."""
    if not os.path.exists(STORAGE_DIR):
        os.makedirs(STORAGE_DIR)


def generate_cache_key(target_company: Dict) -> str:
    """Generate a unique cache key for a target company."""
    # Use name and business description to create unique key
    key_string = f"{target_company.get('name', '').lower().strip()}_{target_company.get('business_description', '').strip()}"
    return hashlib.md5(key_string.encode()).hexdigest()


def save_results(target_company: Dict, results_df: pd.DataFrame) -> str:
    """
    Save results to local storage.
    
    Args:
        target_company: Target company information
        results_df: DataFrame with comparable companies
        
    Returns:
        Cache key for the saved results
    """
    ensure_storage_dir()
    
    cache_key = generate_cache_key(target_company)
    
    # Load existing history
    history = load_history()
    
    # Convert DataFrame to dict for storage
    results_data = {
        "target_company": target_company,
        "results": results_df.to_dict('records'),
        "timestamp": datetime.now().isoformat(),
        "company_count": len(results_df),
        "cache_key": cache_key
    }
    
    # Add or update entry
    history[cache_key] = results_data
    
    # Save to file
    with open(STORAGE_FILE, 'w') as f:
        json.dump(history, f, indent=2)
    
    return cache_key


def load_results(cache_key: str) -> Optional[pd.DataFrame]:
    """
    Load results from cache.
    
    Args:
        cache_key: Cache key for the results
        
    Returns:
        DataFrame with results or None if not found
    """
    history = load_history()
    
    if cache_key in history:
        results_data = history[cache_key]
        results_list = results_data.get("results", [])
        if results_list:
            return pd.DataFrame(results_list)
    
    return None


def get_cached_results(target_company: Dict) -> Optional[pd.DataFrame]:
    """
    Check if results exist in cache for a target company.
    
    Args:
        target_company: Target company information
        
    Returns:
        DataFrame with cached results or None if not found
    """
    cache_key = generate_cache_key(target_company)
    return load_results(cache_key)


def load_history() -> Dict:
    """Load the entire results history."""
    ensure_storage_dir()
    
    if os.path.exists(STORAGE_FILE):
        try:
            with open(STORAGE_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    
    return {}


def get_history_list() -> List[Dict]:
    """
    Get a list of all cached searches.
    
    Returns:
        List of search metadata dictionaries
    """
    history = load_history()
    
    history_list = []
    for cache_key, data in history.items():
        history_list.append({
            "cache_key": cache_key,
            "company_name": data.get("target_company", {}).get("name", "Unknown"),
            "industry": data.get("target_company", {}).get("primary_industry_classification", "Unknown"),
            "timestamp": data.get("timestamp", ""),
            "company_count": data.get("company_count", 0),
            "url": data.get("target_company", {}).get("url", "")
        })
    
    # Sort by timestamp (newest first)
    history_list.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    
    return history_list


def delete_result(cache_key: str) -> bool:
    """
    Delete a cached result.
    
    Args:
        cache_key: Cache key to delete
        
    Returns:
        True if deleted, False if not found
    """
    history = load_history()
    
    if cache_key in history:
        del history[cache_key]
        
        # Save updated history
        with open(STORAGE_FILE, 'w') as f:
            json.dump(history, f, indent=2)
        
        return True
    
    return False


def clear_all_results() -> int:
    """
    Clear all cached results.
    
    Returns:
        Number of results deleted
    """
    history = load_history()
    count = len(history)
    
    # Clear history
    with open(STORAGE_FILE, 'w') as f:
        json.dump({}, f, indent=2)
    
    return count

