
import requests
from config import SERPAPI_KEY, COL_LOCATION, COL_COMPANY
import time

def find_linkedin_profile(name, company=None, location=None):
    """
    Uses SerpAPI to search for a LinkedIn profile.
    Returns the LinkedIn URL if found, else None.
    """
    query = f"site:linkedin.com/in/ {name}"
    if company:
        query += f" {company}"
    if location:
        query += f" {location}"
        
    params = {
        "engine": "google",
        "q": query,
        "api_key": SERPAPI_KEY,
        "num": 3  # We only need the top few results
    }
    
    try:
        response = requests.get("https://serpapi.com/search", params=params)
        response.raise_for_status()
        results = response.json()
        
        if "organic_results" in results:
            for result in results["organic_results"]:
                link = result.get("link")
                if link and "linkedin.com/in/" in link:
                    return link
    except Exception as e:
        print(f"Error searching for {name}: {e}")
        
    return None

def google_search(query):
    """
    General Google Search fallback.
    Returns list of top result snippets/links.
    """
    params = {
        "engine": "google",
        "q": query,
        "api_key": SERPAPI_KEY,
        "num": 5
    }
    
    try:
        response = requests.get("https://serpapi.com/search", params=params)
        response.raise_for_status()
        results = response.json()
        
        snippets = []
        if "organic_results" in results:
            for result in results["organic_results"]:
                title = result.get("title", "")
                snippet = result.get("snippet", "")
                link = result.get("link", "")
                snippets.append({"title": title, "snippet": snippet, "link": link})
        return snippets
    except Exception as e:
        print(f"Error in general search for {query}: {e}")
        return []
