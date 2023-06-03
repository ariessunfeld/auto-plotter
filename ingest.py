import pandas as pd
import sys
import os

DATA_FOLDER = 'data'
MAX_ROWS_TO_SCAN = 16

def find_header_row(file, max_rows_to_scan):
    """Returns the 'best' header row for a CSV file"""
    
    min_score = float('inf')  # Start with infinity so any score will be less
    best_header_row = None

    try:
        df = pd.read_csv(file)
    except FileNotFoundError:
        print(f'Could not find {file}')
        return None

    length = len(df)
    n_rows_to_search = min(length-1, max_rows_to_scan)

    # Loop over the first n rows
    for i in range(n_rows_to_search):
        # Try reading in the data with the current row as the header
        df = pd.read_csv(file, header=i, nrows=n_rows_to_search+1)

        # Convert the column names to a list
        columns = df.columns.tolist()

        # Score based on number of "unnamed" in the column names
        num_unnamed = sum('unnamed' in name.lower() for name in columns)

        # Score based on number of unique column names
        num_unique = len(set(columns))

        # Score based on consistency of data types in each column
        type_consistency = sum(df[col].apply(type).nunique() == 1 for col in df.columns)

        # Combine the scores into a total score
        # For this example, we'll simply add them, but you could consider other ways to combine the scores
        total_score = num_unnamed - num_unique - type_consistency

        # If this is the lowest score we've seen so far, update our best guess for the header row
        if total_score < min_score:
            min_score = total_score
            best_header_row = i

    return best_header_row

def summarize_csvs(data_folder, max_rows_to_scan, max_cols_in_summary):

    files = [os.path.join(data_folder, f) for f in os.listdir(data_folder)]

    summary = {}
    for file in files:
        if file.endswith('.csv'):
            summary[file] = {}
            summary[file]['header row'] = find_header_row(file, max_rows_to_scan)
            df = pd.read_csv(file, header=summary[file]['header row'])
            columns = df.columns.to_list()
            del df
            m = min(len(columns), max_cols_in_summary)
            if m == len(columns):
                summary[file]['columns'] = columns
            else:
                summary[file][f'first {max_cols_in_summary} columns'] = columns[:max_cols_in_summary]

    return summary
