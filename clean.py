import pandas as pd
import re

def clean_food_dataset(input_file, output_file):
    """
    Advanced cleaning for the food nutrition dataset with more robust parsing
    """
    # Read the raw file
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: File {input_file} not found.")
        return None
    
    # Process lines
    cleaned_lines = []
    
    # Process header
    if not lines:
        print("Error: Empty input file.")
        return None
    
    # Modify header handling to be more flexible
    header_line = lines[0].strip()
    header_parts = header_line.split()
    
    # Try to identify the correct header structure
    if len(header_parts) > 6:
        # Assume first few parts are food description
        description_parts = header_parts[:len(header_parts)-5]
        numeric_headers = header_parts[len(description_parts):]
        
        header = '_'.join(description_parts) + '\t' + '\t'.join(numeric_headers)
    else:
        header = '\t'.join(header_parts)
    
    cleaned_lines.append(header)
    
    # Process data lines with more flexible parsing
    for line in lines[1:]:
        line = line.strip()
        parts = line.split()
        
        # If line has fewer than 6 parts, skip
        if len(parts) < 6:
            continue
        
        # Try to separate description from numeric values more robustly
        # Look for the last 4 or 5 numeric-looking parts
        numeric_part_candidates = parts[-5:]
        
        # Validate numeric parts
        numeric_parts = []
        for part in numeric_part_candidates:
            try:
                # Attempt to convert to float
                float_val = float(part)
                numeric_parts.append(part)
            except ValueError:
                # If conversion fails, stop looking for numeric parts
                break
        
        # Ensure we have enough numeric parts
        if len(numeric_parts) < 4:
            print(f"Skipping line with insufficient numeric data: {line}")
            continue
        
        # The description is everything before the numeric parts
        description_parts = parts[:-len(numeric_parts)]
        description = '_'.join(description_parts)
        
        # Combine into a clean line
        cleaned_line = f"{description}\t" + "\t".join(numeric_parts)
        cleaned_lines.append(cleaned_line)
        
    # Write cleaned data
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(cleaned_lines))
    
    # Verify the cleaned file
    try:
        # Use more robust CSV reading
        df = pd.read_csv(output_file, sep='\t', dtype=str)
        
        # Convert numeric columns
        numeric_cols = ['Energy_(kcal)', 'Protein_(g)', 'Carbohydrate_(g)', 'Total_Fat_(g)']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        print("\nCleaned File Summary:")
        print(f"Total rows: {len(df)}")
        print("\nColumns:")
        print(df.columns)
        print("\nFirst few rows:")
        print(df.head())
        
        return df
    except Exception as e:
        print(f"Error reading the cleaned file: {e}")
        return None

def validate_dataset(df):
    if df is None or df.empty:
        print("Cannot validate an empty or None DataFrame")
        return
    
    print("\nDataset Validation:")
    
    # Use the predefined numeric columns
    numeric_cols = ['Energy_(kcal)', 'Protein_(g)', 'Carbohydrate_(g)', 'Total_Fat_(g)']
    
    # Validate numeric columns
    for col in numeric_cols:
        print(f"\nColumn: {col}")
        print(f"Total non-null values: {df[col].count()}")
        print(f"Numeric range: {df[col].min()} to {df[col].max()}")
        
        # Check for any non-numeric values
        non_numeric = df[pd.to_numeric(df[col], errors='coerce').isna()]
        if len(non_numeric) > 0:
            print(f"Warning: {len(non_numeric)} non-numeric values found")
            print(non_numeric[['description', col]])

# Paths
input_file = 'cleaned_fndds_nutrient_values.csv'
output_file = 'cleaned_fndds_nutrient_values_fixed.csv'

# Run the cleaning
cleaned_df = clean_food_dataset(input_file, output_file)

# Run validation if DataFrame is not empty
if cleaned_df is not None:
    validate_dataset(cleaned_df)