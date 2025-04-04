# main.py
import os
import tempfile
from google.cloud import storage
import pandas as pd
from utils.gcp import export_assets_from_projects
from utils.notion import update_notion_database
from utils.data import clean_and_merge_csv_files
import config

def gcp_to_notion_sync(request):
    """
    Cloud Function to sync GCP assets to a Notion database via HTTP trigger.
    
    Args:
        request (flask.Request): The request object
    Returns:
        flask.Response: The response object
    """
    print("Starting GCP to Notion sync process")
    
    # Create a temporary directory for working with files
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Step 1: Export assets from multiple projects to GCS
        csv_files_in_gcs = export_assets_from_projects(
            project_ids=config.GCP_PROJECT_IDS,
            gcs_bucket=config.GCS_BUCKET,
            asset_types=config.ASSET_TYPES
        )
        
        # Step 2: Download CSV files from GCS
        storage_client = storage.Client()
        bucket = storage_client.bucket(config.GCS_BUCKET)
        
        local_csv_paths = []
        for gcs_path in csv_files_in_gcs:
            blob_name = gcs_path.split(f"gs://{config.GCS_BUCKET}/")[1]
            local_path = os.path.join(temp_dir, os.path.basename(blob_name))
            
            blob = bucket.blob(blob_name)
            blob.download_to_filename(local_path)
            local_csv_paths.append(local_path)
            
            print(f"Downloaded {gcs_path} to {local_path}")
        
        # Step 3: Clean and merge the CSV files
        merged_csv_path = os.path.join(temp_dir, 'merged_assets.csv')
        clean_and_merge_csv_files(local_csv_paths, merged_csv_path)
        print(f"Merged and cleaned data saved to {merged_csv_path}")
        
        # Step 4: Update Notion database with merged data
        update_notion_database(
            csv_file=merged_csv_path,
            notion_api_key=config.NOTION_API_KEY,
            database_id=config.NOTION_DATABASE_ID
        )
        
        print("Successfully updated Notion database")
        
        # Cleanup: Delete the temporary GCS files
        for gcs_path in csv_files_in_gcs:
            blob_name = gcs_path.split(f"gs://{config.GCS_BUCKET}/")[1]
            bucket.blob(blob_name).delete()
            print(f"Deleted temporary file: {gcs_path}")
        
        return "Sync completed successfully", 200
        
    except Exception as e:
        print(f"Error in GCP to Notion sync process: {str(e)}")
        raise e
    
    finally:
        # Clean up temp files
        for file in os.listdir(temp_dir):
            os.remove(os.path.join(temp_dir, file))
        os.rmdir(temp_dir)