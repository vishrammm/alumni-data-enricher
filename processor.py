
from search import find_linkedin_profile, google_search
from linkedin import get_linkedin_profile_data
from scraper import scrape_generic_info
from config import *
import pandas as pd

def process_alumni_row(row):
    """
    Takes a row (Series) of alumni data and returns an enriched dictionary.
    Returns: Name, LinkedIn Status, LinkedIn URL, Web Search URL
    """
    name = str(row[COL_NAME]).strip() if pd.notna(row[COL_NAME]) else ""
    company = str(row.get(COL_COMPANY, "")).strip() if pd.notna(row.get(COL_COMPANY, "")) else ""
    location = str(row.get(COL_LOCATION, "")).strip() if pd.notna(row.get(COL_LOCATION, "")) else ""
    
    # Initialize result fields
    result = {
        COL_NAME: name,
        COL_LINKEDIN_STATUS: "Not Found",
        COL_LINKEDIN_URL: "",
        COL_WEB_SEARCH_URL: ""
    }
    
    # Step 1: Find LinkedIn Profile
    print(f"Searching for {name}...")
    linkedin_url = find_linkedin_profile(name, company, location)
    
    if linkedin_url:
        print(f"Found LinkedIn: {linkedin_url}")
        result[COL_LINKEDIN_URL] = linkedin_url
        result[COL_LINKEDIN_STATUS] = "Found"
    else:
        # Step 2: Fallback to General Web Search
        print(f"LinkedIn not found for {name}. Trying general search...")
        try:
            search_query = f"{name} {company} {location} current job"
            snippets = google_search(search_query)
            
            if snippets:
                result[COL_WEB_SEARCH_URL] = snippets[0]['link']
        except Exception as e:
            print(f"Web search failed: {e}")

    return result
