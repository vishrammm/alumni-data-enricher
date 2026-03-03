
import pandas as pd
import time
from config import *
from excel_handler import get_unprocessed_alumni, save_batch, initialize_output_file
from processor import process_alumni_row

def main():
    print("Starting Alumni Info Scraper...")
    
    # Ensure files are set up
    initialize_output_file()
    
    # Get unprocessed data
    unprocessed_df = get_unprocessed_alumni()
    total_to_process = len(unprocessed_df)
    print(f"Total alumni to process: {total_to_process}")
    
    if total_to_process == 0:
        print("No new alumni to process.")
        return

    processed_batch = []
    
    # Iterate through unprocessed rows
    # We use iterrows() which is slow but fine for 7000 records with API calls being the bottleneck
    for index, row in unprocessed_df.iterrows():
        print(f"Processing {index + 1}/{total_to_process}: {row[COL_NAME]}")
        
        try:
            enriched_data = process_alumni_row(row)
            
            # Combine original row data with enriched data
            # Convert row to dict first
            full_record = row.to_dict()
            full_record.update(enriched_data)
            
            processed_batch.append(full_record)
            
            # Check if batch size reached
            if len(processed_batch) >= BATCH_SIZE:
                save_batch(pd.DataFrame(processed_batch))
                processed_batch = [] # Reset batch
                print(f"Batch saved. Sleeping for 2 seconds...")
                time.sleep(2) # Respect API limits
                
        except Exception as e:
            print(f"Error processing row {index}: {e}")
            # Optionally continue or break
            continue
            
    # Save remaining records
    if processed_batch:
        save_batch(pd.DataFrame(processed_batch))
        print("Final batch saved.")
        
    print("Processing complete!")

if __name__ == "__main__":
    main()
