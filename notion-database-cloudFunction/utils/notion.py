import requests
import json
import pandas as pd
import time

def update_notion_database(csv_file, notion_api_key, database_id):
    """
    Clear a Notion database and update it with data from a CSV file.
    
    Args:
        csv_file (str): Path to the CSV file
        notion_api_key (str): Notion API key
        database_id (str): ID of the Notion database to update
    """
    headers = {
        "Authorization": f"Bearer {notion_api_key}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    # Clear existing database entries
    clear_database(database_id, headers)
    
    # Fetch database schema
    response = requests.get(
        f"https://api.notion.com/v1/databases/{database_id}",
        headers=headers
    )
    
    if response.status_code != 200:
        raise Exception(f"Failed to fetch database schema: {response.text}")
    
    schema = response.json()
    properties = schema.get("properties", {})
    print(f"Retrieved database schema with {len(properties)} properties")
    
    # Load CSV data
    df = pd.read_csv(csv_file)
    print(f"Loaded CSV with {len(df)} rows and {len(df.columns)} columns")
    
    batch_size = 10
    total_records = len(df)
    
    for i in range(0, total_records, batch_size):
        batch = df.iloc[i:min(i+batch_size, total_records)]
        print(f"Processing batch {i//batch_size + 1} ({len(batch)} records)")
        
        for _, row in batch.iterrows():
            try:
                properties_payload = map_row_to_notion_properties(row, properties)
                
                create_url = "https://api.notion.com/v1/pages"
                payload = {
                    "parent": {"database_id": database_id},
                    "properties": properties_payload
                }
                
                response = requests.post(create_url, headers=headers, json=payload)
                
                if response.status_code not in [200, 201]:
                    print(f"Error creating page: {response.status_code}, {response.text}")
                    continue
                
            except Exception as e:
                print(f"Error processing row: {str(e)}")
        
        time.sleep(0.5)
    
    print(f"Successfully processed {total_records} records")

def map_row_to_notion_properties(row, schema_properties):
    """
    Map a CSV row to Notion properties based on the database schema.
    """
    notion_properties = {}
    
    for col_name, value in row.items():
        if pd.isna(value):
            continue
            
        matching_prop = None
        for prop_name, prop_schema in schema_properties.items():
            if prop_name.lower().replace(' ', '_') == col_name.lower().replace(' ', '_'):
                matching_prop = (prop_name, prop_schema)
                break
        
        if not matching_prop:
            continue
            
        prop_name, prop_schema = matching_prop
        prop_type = prop_schema.get('type')
        
        if prop_type == 'title':
            notion_properties[prop_name] = {"title": [{"text": {"content": str(value)}}]}
        elif prop_type == 'rich_text':
            notion_properties[prop_name] = {"rich_text": [{"text": {"content": str(value)}}]}
        elif prop_type == 'number':
            try:
                notion_properties[prop_name] = {"number": float(value)}
            except:
                pass
        elif prop_type == 'select':
            notion_properties[prop_name] = {"select": {"name": str(value)}}
        elif prop_type == 'multi_select':
            if isinstance(value, str):
                items = [item.strip() for item in value.split(',')]
                notion_properties[prop_name] = {"multi_select": [{"name": item} for item in items if item]}
        elif prop_type == 'date':
            try:
                notion_properties[prop_name] = {"date": {"start": str(value)}}
            except:
                pass
        elif prop_type == 'checkbox':
            notion_properties[prop_name] = {"checkbox": bool(value)}
        elif prop_type == 'url':
            notion_properties[prop_name] = {"url": str(value)}
        elif prop_type == 'email':
            notion_properties[prop_name] = {"email": str(value)}
        elif prop_type == 'phone_number':
            notion_properties[prop_name] = {"phone_number": str(value)}
    
    return notion_properties

def clear_database(database_id, headers):
    """
    Clear all entries from a Notion database.
    """
    print("WARNING: Clearing all existing database entries")
    
    has_more = True
    start_cursor = None
    deleted_count = 0
    
    while has_more:
        query_url = f"https://api.notion.com/v1/databases/{database_id}/query"
        payload = {}
        if start_cursor:
            payload["start_cursor"] = start_cursor
            
        response = requests.post(query_url, headers=headers, json=payload)
        
        if response.status_code != 200:
            print(f"Error querying database: {response.text}")
            return
        
        data = response.json()
        pages = data.get("results", [])
        
        for page in pages:
            page_id = page["id"]
            archive_url = f"https://api.notion.com/v1/pages/{page_id}"
            archive_payload = {"archived": True}
            
            delete_response = requests.patch(
                archive_url, 
                headers=headers, 
                json=archive_payload
            )
            
            if delete_response.status_code == 200:
                deleted_count += 1
            else:
                print(f"Failed to delete page {page_id}: {delete_response.text}")
            
            time.sleep(0.3)
        
        has_more = data.get("has_more", False)
        start_cursor = data.get("next_cursor")
    
    print(f"Successfully deleted {deleted_count} pages from the database")
