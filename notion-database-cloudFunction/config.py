# config.py

# GCP Configuration
GCP_PROJECT_IDS = [
    "database-cocoparks",
    "cv-database-dev",
]

# GCS bucket for temporary storage of CSV files
GCS_BUCKET = "notion-database-syncher-bucket"

# Asset types to export
ASSET_TYPES = [
    "compute.googleapis.com/Instance",
    "storage.googleapis.com/Bucket",
    "container.googleapis.com/Cluster",
    "sqladmin.googleapis.com/Instance",
    # Add more asset types as needed
]

# Notion API Configuration
NOTION_API_KEY = "your-notion-api-key"
NOTION_DATABASE_ID = "your-notion-database-id"