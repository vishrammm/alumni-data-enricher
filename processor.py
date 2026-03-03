
from search import find_linkedin_profile, google_search
from linkedin import get_linkedin_profile_data
from scraper import scrape_generic_info
from config import *

def process_alumni_row(row):
    """
    Takes a row (Series) of alumni data and returns an enriched dictionary.
    """
    name = row[COL_NAME]
    company = row.get(COL_COMPANY, "")
    location = row.get(COL_LOCATION, "")
    
    # Initialize result fields
    result = {
        COL_LINKEDIN_URL: "",
        COL_LINKEDIN_STATUS: "Not Found",
        COL_DATA_SOURCE: "",
        COL_ENRICHED_ROLE: "",
        COL_ENRICHED_COMPANY: "",
        COL_ENRICHED_LOCATION: ""
    }
    
    # Step 1: Find LinkedIn Profile
    print(f"Searching for {name}...")
    linkedin_url = find_linkedin_profile(name, company, location)
    
    if linkedin_url:
        print(f"Found LinkedIn: {linkedin_url}")
        result[COL_LINKEDIN_URL] = linkedin_url
        result[COL_LINKEDIN_STATUS] = "Found"
        result[COL_DATA_SOURCE] = "LinkedIn"
        
        # Step 2: Get Profile Data
        profile_data = get_linkedin_profile_data(linkedin_url)
        if profile_data:
            # Extract relevant fields
            result[COL_ENRICHED_ROLE] = profile_data.get('occupation', '')
            result[COL_ENRICHED_LOCATION] = f"{profile_data.get('city', '')}, {profile_data.get('state', '')}, {profile_data.get('country_full_name', '')}".strip(', ')
            
            # Try to get current company from experiences
            experiences = profile_data.get('experiences', [])
            if experiences:
                current_job = experiences[0]
                if current_job.get('ends_at') is None: # Currently working there
                     result[COL_ENRICHED_COMPANY] = current_job.get('company', '')
                     if not result[COL_ENRICHED_ROLE]:
                        result[COL_ENRICHED_ROLE] = current_job.get('title', '')
            
            if not result[COL_ENRICHED_COMPANY]:
                 # Fallback to headline if specific company not found in experiences
                 pass
                 
    else:
        # Step 3: Fallback to General Web Search
        print(f"LinkedIn not found for {name}. Trying general search...")
        try:
            search_query = f"{name} {company} {location} current job"
            snippets = google_search(search_query) # This function was in search.py but named google_search inside it
            
            if snippets:
                result[COL_DATA_SOURCE] = "Web Search"
                result[COL_LINKEDIN_STATUS] = "Not Found"
                
                # Simple heuristic: Take the first result snippet as a summary
                # Or try to scrape the first result if it looks promising
                first_result = snippets[0]
                extracted_info = f"Source: {first_result['link']}\nSnippet: {first_result['snippet']}"
                
                # If we want to be more aggressive, we could scrape the link:
                # scraped_text = scrape_generic_info(first_result['link'])
                # if scraped_text:
                #     extracted_info += f"\n\nScraped: {scraped_text}"
                
                # Store this "messy" info in one of the fields or a notes field
                # For now, put it in Enriched Role to indicate what we found
                result[COL_ENRICHED_ROLE] = extracted_info[:500] # Limit length
        except Exception as e:
            print(f"Web search failed: {e}")

    return result
