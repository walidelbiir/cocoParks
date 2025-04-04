# utils/data.py
import pandas as pd
import numpy as np

def clean_and_merge_csv_files(csv_files, output_path):
    """
    Clean and merge multiple CSV files into a single CSV file.
    
    Args:
        csv_files (list): List of paths to CSV files
        output_path (str): Path to save the merged and cleaned CSV file
    """
    all_dfs = []
    
    for file in csv_files:
        try:
            # Read the CSV file
            df = pd.read_csv(file)
            
            # Add source file information (optional)
            df['source_file'] = file
            
            # Basic data cleaning
            # 1. Handle missing values
            df.fillna('N/A', inplace=True)
            
            # 2. Convert timestamp columns to datetime
            for col in df.columns:
                if 'time' in col.lower() or 'date' in col.lower():
                    try:
                        df[col] = pd.to_datetime(df[col])
                    except:
                        pass
            
            # 3. Extract project from name if available
            if 'name' in df.columns:
                df['project'] = df['name'].apply(
                    lambda x: x.split('/')[1] if isinstance(x, str) and '/' in x else 'unknown'
                )
            
            # 4. Add additional metadata columns
            if 'labels' in df.columns:
                df['environment'] = df['labels'].apply(
                    lambda x: 'prod' if isinstance(x, str) and 'prod' in x else 
                             ('dev' if isinstance(x, str) and 'dev' in x else 'unknown')
                )
            
            # 5. Custom cleaning logic here...
            
            all_dfs.append(df)
            print(f"Processed file: {file}, shape: {df.shape}")
            
        except Exception as e:
            print(f"Error processing file {file}: {str(e)}")
    
    if not all_dfs:
        raise ValueError("No valid CSV files to merge")
    
    # Merge all dataframes
    merged_df = pd.concat(all_dfs, ignore_index=True)
    
    # Final cleaning and transformations on the merged dataset
    # 1. Remove duplicate entries
    merged_df.drop_duplicates(inplace=True)
    
    # 2. Standardize column names
    merged_df.columns = [col.lower().replace(' ', '_') for col in merged_df.columns]
    
    # 3. Add a last_updated column
    merged_df['last_updated'] = pd.Timestamp.now()
    
    # Save the cleaned and merged data
    merged_df.to_csv(output_path, index=False)
    
    print(f"Merged {len(all_dfs)} files into single CSV with {len(merged_df)} rows")
    return merged_df