
import pandas as pd
import os
import openpyxl
from config import *

# Ensure necessary columns exist in the DataFrame
NEW_COLUMNS = [
    COL_LINKEDIN_URL,
    COL_LINKEDIN_STATUS,
    COL_DATA_SOURCE,
    COL_ENRICHED_ROLE,
    COL_ENRICHED_COMPANY,
    COL_ENRICHED_LOCATION
]

def initialize_output_file():
    """
    Checks if output file exists. If not, creates it by copying headers from input file
    and adding new columns.
    """
    if not os.path.exists(OUTPUT_EXCEL_FILE):
        if not os.path.exists(INPUT_EXCEL_FILE):
             # Create a dummy file for testing if input doesn't exist
            print(f"Warning: {INPUT_EXCEL_FILE} not found. Creating a dummy file.")
            create_dummy_input_file()
            
        df = pd.read_excel(INPUT_EXCEL_FILE)
        # Initialize new columns
        for col in NEW_COLUMNS:
            df[col] = ""
        
        # Save empty dataframe to output file to start
        # We will append to this file
        # Actually, for batch processing, we might just want to read from input 
        # and checking if a row is already processed in output.
        # A simpler way: Copy input to output initially if output doesn't exist.
        df.head(0).to_excel(OUTPUT_EXCEL_FILE, index=False)
        print(f"Created {OUTPUT_EXCEL_FILE} with headers.")

def create_dummy_input_file():
    """Creates a dummy Excel file for testing."""
    data = {
        COL_NAME: ["John Doe", "Jane Smith", "Alice Jones"],
        COL_EMAIL: ["john@example.com", "jane@example.com", "alice@example.com"],
        COL_COURSE: ["B.Tech", "MBA", "B.Sc"],
        COL_STREAM: ["CS", "Marketing", "Physics"],
        COL_YEAR: [2020, 2019, 2021],
        COL_CONTACT: ["1234567890", "9876543210", ""],
        COL_LOCATION: ["New York", "London", "San Francisco"],
        COL_COMPANY: ["Google", "Amazon", "Unemployed"],
        COL_DESIGNATION: ["Engineer", "Manager", "Student"],
    }
    df = pd.DataFrame(data)
    df.to_excel(INPUT_EXCEL_FILE, index=False)
    print(f"Created dummy input file: {INPUT_EXCEL_FILE}")

def get_unprocessed_alumni():
    """
    Reads the input file and identifies rows that haven't been processed yet 
    by checking the output file.
    Returns: DataFrame of unprocessed rows.
    """
    if not os.path.exists(OUTPUT_EXCEL_FILE):
        initialize_output_file()
    
    input_df = pd.read_excel(INPUT_EXCEL_FILE)
    
    # Check if we have an output file with data
    try:
        output_df = pd.read_excel(OUTPUT_EXCEL_FILE)
    except FileNotFoundError:
        output_df = pd.DataFrame()
    
    # Identify processed rows based on a unique key, e.g., Email or Name + Course
    # For now, let's assume the index matches or email is unique.
    # A safer way is to add a 'Processed' flag in input, but we want to leave input untouched.
    # We can check if 'Email' exists in output_df.
    
    if not output_df.empty and COL_EMAIL in output_df.columns:
        processed_emails = output_df[COL_EMAIL].tolist()
        unprocessed_df = input_df[~input_df[COL_EMAIL].isin(processed_emails)]
    else:
        unprocessed_df = input_df
        
    return unprocessed_df

def save_batch(batch_df):
    """
    Appends the processed batch to the output Excel file.
    """
    if not os.path.isfile(OUTPUT_EXCEL_FILE):
        batch_df.to_excel(OUTPUT_EXCEL_FILE, index=False)
    else:
        # Append mode is tricky with Excel. 
        # Better to read existing, concat, and write. 
        # For very large files, this is slow, but for 7000 rows it's manageable.
        existing_df = pd.read_excel(OUTPUT_EXCEL_FILE)
        updated_df = pd.concat([existing_df, batch_df], ignore_index=True)
        updated_df.to_excel(OUTPUT_EXCEL_FILE, index=False)
        print(f"Saved batch of {len(batch_df)} records.")
