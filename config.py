# config.py
import os

# API Keys — set these as environment variables on Render dashboard
SERPAPI_KEY = os.environ.get("SERPAPI_KEY", "")
PROXYCURL_API_KEY = os.environ.get("PROXYCURL_API_KEY", "")

# File Paths
INPUT_EXCEL_FILE = "alumni_data.ods"
OUTPUT_EXCEL_FILE = "enriched_alumni_new.xlsx"

# Processing Configuration
BATCH_SIZE = 50  # Process 50 alumni at a time before saving
USE_MOCK_DATA = False # Set to True for testing with mock data if needed

# Column Mapping (Adjust if input excel headers are different)
COL_NAME = "Name"
COL_EMAIL = "Email"
COL_COURSE = "Course Name"
COL_STREAM = "Stream Name"
COL_YEAR = "Passing Out Year"
COL_CONTACT = "Contact Info"
COL_LOCATION = "Current Location"
COL_COMPANY = "Company"
COL_DESIGNATION = "Designation"

# New Columns to Add
COL_LINKEDIN_URL = "LinkedIn URL"
COL_LINKEDIN_STATUS = "LinkedIn Status"
COL_WEB_SEARCH_URL = "Web Search URL"
