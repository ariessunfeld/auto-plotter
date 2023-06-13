import pandas as pd
import logging
from collections import defaultdict
from pathlib import Path

DATA_FOLDER = Path('data')
MAX_ROWS_SCAN = 16
MAX_COLS_SUMMARY = 100

def find_header_row_excel(file, max_rows_scan, sheet_name):
    """Returns the 'best' header row for an Excel file"""

    min_score = float('inf')
    best_header_row = None

    try:
        df = pd.read_excel(file, sheet_name)
    except FileNotFoundError:
        logging.error(f'Could not find {file}')
        return None

    n_rows_search = min(len(df)-1, max_rows_scan)

    for i in range(n_rows_search):
        df = pd.read_excel(file, sheet_name, header=i, nrows=n_rows_search+1)

        columns = df.columns.tolist()
        num_unnamed = sum('unnamed' in str(name).lower() for name in columns)
        num_unique = len(set(columns))
        type_consistency = sum(df[col].apply(type).nunique() == 1 for col in df.columns)

        total_score = num_unnamed - num_unique - type_consistency

        if total_score < min_score:
            min_score = total_score
            best_header_row = i

    return best_header_row

def summarize_excels(data_folder, max_rows_scan, max_cols_summary):
    """Summarize all Excel files in the data folder"""

    files = [file for file in data_folder.glob('*') if file.is_file() and file.name.endswith('.xlsx') and not file.name.startswith('~')]

    summary = defaultdict(dict)
    for file in files:

        xls = pd.ExcelFile(file)
        for sheet_name in xls.sheet_names:
            summary[file][sheet_name] = {}

            summary[file][sheet_name]['header row'] = find_header_row_excel(file, max_rows_scan, sheet_name)

            if summary[file][sheet_name]['header row'] is not None:
                try:
                    df = pd.read_excel(file, sheet_name, header=summary[file][sheet_name]['header row'])
                    columns = df.columns.to_list()
                    del df

                    summary[file][sheet_name]['columns'] = columns[:max_cols_summary] if len(columns) > max_cols_summary else columns

                except pd.errors.ParserError as err:
                    logging.error(f'Error parsing {file}: {err}')

    return summary

def find_header_row_csv(file, max_rows_scan):
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
        num_unnamed = sum('unnamed' in str(name).lower() for name in columns)
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
        summary[file]['header row'] = find_header_row_csv(file, max_rows_scan)

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
    logging.basicConfig(filename='summary.log', level=logging.INFO)

    _csv_summary = summarize_csvs(DATA_FOLDER, MAX_ROWS_SCAN, MAX_COLS_SUMMARY)
    csv_summary = ''
    for i, (key, val) in enumerate(dict(_csv_summary).items()):
        if i != len(dict(_csv_summary)) - 1:
            csv_summary += f"'{str(key)}'" + ': ' + str(val) + ', '
        else:
            csv_summary += f"'{str(key)}'" + ': ' + str(val)
    csv_summary = '{' + csv_summary + '}'

    _xlsx_summary = summarize_excels(DATA_FOLDER, MAX_ROWS_SCAN, MAX_COLS_SUMMARY)
    xlsx_summary = ''
    for i, (key, val) in enumerate(dict(_xlsx_summary).items()):
        if i != len(dict(_xlsx_summary)) - 1:
            xlsx_summary += f"'{str(key)}'" + ': ' + str(val) + ', '
        else:
            xlsx_summary += f"'{str(key)}'" + ': ' + str(val)
    xlsx_summary = '{' + xlsx_summary + '}'

    summary = "{'CSV': " + csv_summary + ', ' + "'XLSX': " + xlsx_summary + '}'
    summary = eval(summary)

    return summary

def get_natural_language_summary():
    _csv_summary = summarize_csvs(DATA_FOLDER, MAX_ROWS_SCAN, MAX_COLS_SUMMARY)
    csv_summary = ''
    for key, val in dict(_csv_summary).items():
        csv_summary += f"The file {key} has columns {val['columns']}. For this file, {key}, use header = {val['header row']}.\n"
        csv_summary += '\n'
    
    _xlsx_summary = summarize_excels(DATA_FOLDER, MAX_ROWS_SCAN, MAX_COLS_SUMMARY)
    xlsx_summary = ''
    for key, val in dict(_xlsx_summary).items():
        if len(val.keys()) > 1: # More than one sheet
            xlsx_summary += f'The file {key} has sheets named {list(val.keys())}.\n'
        else:
            xlsx_summary += f'The file {key} has a sheet named {val.keys()[0]}'
        for sheet_name, subdict in val.items():
            xlsx_summary += f"The sheet called {sheet_name} has columns {subdict['columns']}. For sheet {sheet_name}, use header = {subdict['header row']}.\n"
        xlsx_summary += '\n'
    
    return csv_summary + xlsx_summary
