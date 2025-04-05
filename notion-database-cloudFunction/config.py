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
]

# Notion API Configuration
NOTION_API_KEY = "ntn_o26376547504HL2EqsiTXqNbwiqG5viRcYMD6QJKr3IfBz"
NOTION_DATABASE_ID = "1c909d376ade80d3aedafb8e58f7c6af"