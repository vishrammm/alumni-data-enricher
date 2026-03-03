
import requests
from config import PROXYCURL_API_KEY

def get_linkedin_profile_data(linkedin_url):
    """
    Uses Proxycurl API to fetch profile data.
    """
    api_endpoint = 'https://nubela.co/proxycurl/api/v2/linkedin'
    headers = {'Authorization': 'Bearer ' + PROXYCURL_API_KEY}
    params = {
        'url': linkedin_url,
        'fallback_to_cache': 'on-error',
        'use_cache': 'if-present',
        'skills': 'include',
        'inferred_salary': 'include',
        'personal_email': 'include',
        'personal_contact_number': 'include',
        'twitter_profile_id': 'include',
        'facebook_profile_id': 'include',
        'github_profile_id': 'include',
        'extra': 'include',
    }
    
    try:
        response = requests.get(api_endpoint, params=params, headers=headers)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            print(f"Profile not found: {linkedin_url}")
            return None
        else:
            print(f"Error fetching profile {linkedin_url}: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Exception fetching profile {linkedin_url}: {e}")
        return None
