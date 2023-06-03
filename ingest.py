import pandas as pd
import logging
from collections import defaultdict
from pathlib import Path

DATA_FOLDER = Path('data')
MAX_ROWS_SCAN = 16
MAX_COLS_SUMMARY = 100

def find_header_row(file, max_rows_scan):
    """Returns the 'best' header row for a CSV file"""
    
    min_score = float('inf')
    best_header_row = None

    try:
        df = pd.read_csv(file)
    except FileNotFoundError:
        logging.error(f'Could not find {file}')
        return None

    n_rows_search = min(len(df)-1, max_rows_scan)

    for i in range(n_rows_search):
        df = pd.read_csv(file, header=i, nrows=n_rows_search+1)

        columns = df.columns.tolist()
        num_unnamed = sum('unnamed' in name.lower() for name in columns)
        num_unique = len(set(columns))
        type_consistency = sum(df[col].apply(type).nunique() == 1 for col in df.columns)

        total_score = num_unnamed - num_unique - type_consistency

        if total_score < min_score:
            min_score = total_score
            best_header_row = i

    return best_header_row

def summarize_csvs(data_folder, max_rows_scan, max_cols_summary):

    files = [file for file in data_folder.glob('*') if file.is_file() and file.name.endswith('.csv')]

    summary = defaultdict(dict)
    for file in files:
        summary[file]['header row'] = find_header_row(file, max_rows_scan)

        if summary[file]['header row'] is not None:
            try:
                df = pd.read_csv(file, header=summary[file]['header row'])
                columns = df.columns.to_list()
                del df

                summary[file]['columns'] = columns[:max_cols_summary] if len(columns) > max_cols_summary else columns

            except pd.errors.ParserError as e:
                logging.error(f'Error parsing {file}: {e}')
                
    return summary

def get_summary():
    logging.basicConfig(filename='csv_summary.log', level=logging.INFO)
    _summary = summarize_csvs(DATA_FOLDER, MAX_ROWS_SCAN, MAX_COLS_SUMMARY)
    # TODO add parsing/summarization for other filetypes
    summary = ''
    for key, val in dict(_summary).items():
        summary += str(key) + ': ' + str(val) + ', '
    summary = '{' + summary + '}'
    return summary