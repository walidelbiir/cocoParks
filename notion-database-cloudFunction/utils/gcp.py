# utils/gcp.py
from google.cloud import asset_v1
from google import GoogleAPIError
import time
import uuid

def export_assets_from_projects(project_ids, gcs_bucket, asset_types):
    """
    Export GCP assets from multiple projects to CSV files in a GCS bucket.
    
    Args:
        project_ids (list): List of GCP project IDs
        gcs_bucket (str): GCS bucket name for storing CSV files
        asset_types (list): List of asset types to export
        
    Returns:
        list: List of GCS paths to exported CSV files
    """
    client = asset_v1.AssetService()
    csv_paths = []
    
    for project_id in project_ids:
        try:
            # Generate a unique filename for this export
            timestamp = int(time.time())
            unique_id = str(uuid.uuid4())[:8]
            output_file = f"{project_id}_assets_{timestamp}_{unique_id}.csv"
            gcs_uri = f"gs://{gcs_bucket}/{output_file}"
            
            # Set up the parent resource
            parent = f"projects/{project_id}"
            
            # Create the export request
            request = asset_v1.ExportAssetsRequest(
                parent=parent,
                read_time=None,  # Current time
                asset_types=asset_types,
                content_type=asset_v1.ContentType.RESOURCE,
                output_config=asset_v1.OutputConfig(
                    gcs_destination=asset_v1.GcsDestination(
                        uri=gcs_uri
                    )
                )
            )
            
            # Execute the export operation
            operation = client.ExportAssets(request=request)
            response = operation.result()  # Wait for operation to complete
            
            print(f"Successfully exported assets from {project_id} to {gcs_uri}")
            csv_paths.append(gcs_uri)
            
        except GoogleAPIError as e:
            print(f"Error exporting assets from project {project_id}: {str(e)}")
    
    return csv_paths