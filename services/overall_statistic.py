import os
import pandas as pd
from services.word_tokenize import VietnameseTextTokenizer

class SumWord:
    def __init__(self):
        # Initialize tokenizer
        self.tokenizer = VietnameseTextTokenizer()

    def process_file(self, file_path):
        # Read file, tokenize text, and calculate the length of tokenized list
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                text = file.read()
            tokenized_list = self.tokenizer.process_text(text)
            return len(tokenized_list)
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
            return 0

    def process_folder_for_year(self, folder_path, year):
        # Process all files in the specified year's folder and save results to a dataframe
        if not os.path.exists(folder_path):
            print(f"Year folder {folder_path} does not exist.")
            return pd.DataFrame()  # Return empty DataFrame if folder does not exist

        results = []
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            if os.path.isfile(file_path):
                sumword = self.process_file(file_path)
                results.append({'file_name': file_name, 'sumword': sumword, 'year': year})
        df = pd.DataFrame(results)
        df['no.'] = df['file_name'].str.extract(r'(\d+)')
        df.dropna(inplace=True)
        df['no.'] = df['no.'].astype(int)
        df = df.sort_values(by=['no.']).reset_index(drop=True)
        sample_list = pd.read_excel('data/sample_list.xlsx')
        df = sample_list.merge(df[['no.', 'sumword', 'year']], on='no.', how='left')
        return df

    def process_all_years(self, start_year, end_year, base_folder_path):
        all_results = pd.DataFrame()
        for year in range(start_year, end_year + 1):
            folder_path = os.path.join(base_folder_path, str(year))
            yearly_df = self.process_folder_for_year(folder_path, year)
            all_results = pd.concat([all_results, yearly_df], ignore_index=True)
        return all_results

class SummarizePosNeg:
    def __init__(self, folder_path):
        self.folder_path = folder_path

    def process_file(self, file_path):
        try:
            df = pd.read_csv(file_path)
            sum_count = df['count'].sum()
            return sum_count
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
            return 0

    def process_folder_for_year(self, year):
        year_folder_path = os.path.join(self.folder_path, str(year))
        if not os.path.exists(year_folder_path):
            print(f"Year folder {year_folder_path} does not exist.")
            return pd.DataFrame()  # Return empty DataFrame if folder does not exist

        results = []
        for file_name in os.listdir(year_folder_path):
            file_path = os.path.join(year_folder_path, file_name)
            if os.path.isfile(file_path):
                sum_count = self.process_file(file_path)
                results.append({'file_name': file_name, 'sum_count': sum_count, 'year': year})
        df = pd.DataFrame(results)
        df['no.'] = df['file_name'].str.extract(r'(\d+)')
        df.dropna(inplace=True)
        df['no.'] = df['no.'].astype(int)
        df = df.sort_values(by=['no.']).reset_index(drop=True)
        sample_list = pd.read_excel('data/sample_list.xlsx')
        df = sample_list.merge(df[['no.', 'sum_count', 'year']], on='no.', how='left')
        return df


    def process_all_years(self, start_year, end_year):
        all_results = pd.DataFrame()
        for year in range(start_year, end_year + 1):
            yearly_df = self.process_folder_for_year(year)
            all_results = pd.concat([all_results, yearly_df], ignore_index=True)
        return all_results

def load_excel_files(directory_path):
    dataframes = {}
    for filename in os.listdir(directory_path):
        if filename.endswith(".xlsx") or filename.endswith(".xls"):
            file_path = os.path.join(directory_path, filename)
            df = pd.read_excel(file_path)
            dataframes[filename] = df
    return dataframes

def transform_cdkt_data(df):
    df = df.iloc[4:].reset_index(drop=True).iloc[:130]
    df.columns = df.iloc[0]
    df = df.iloc[1:].dropna(how='all').fillna(0)
    return df

def filter_and_transform_year(df, year):
    stock_code = df.columns[0]
    filtered_df = df[[stock_code, str(year)]].T.reset_index()
    filtered_df.iloc[1, 0] = filtered_df.iloc[0, 0]
    filtered_df.columns = filtered_df.iloc[0]
    filtered_df = filtered_df.iloc[1:]
    filtered_df.rename(columns={filtered_df.columns[0]: 'stock_code'}, inplace=True)
    return filtered_df
def process_folders(base_folder, year):
    all_data = []
    for folder_name in os.listdir(base_folder):
        folder_path = os.path.join(base_folder, folder_name)
        if os.path.isdir(folder_path):
            excel_files = load_excel_files(folder_path)
            for filename, df in excel_files.items():
                transformed_df = transform_cdkt_data(df)
                filtered_df = filter_and_transform_year(transformed_df, year)
                all_data.append(filtered_df)
    concatenated_df = pd.concat(all_data, ignore_index=True)
    return concatenated_df

import os
import pandas as pd

class BalancesheetDataProcessor:
    def __init__(self, directory_path):
        self.directory_path = directory_path
        self.dataframes = self.load_excel_files()

    def load_excel_files(self):
        dataframes = {}
        for filename in os.listdir(self.directory_path):
            if filename.endswith(".xlsx") or filename.endswith(".xls"):
                file_path = os.path.join(self.directory_path, filename)
                try:
                    df = pd.read_excel(file_path, engine='openpyxl' if filename.endswith('.xlsx') else 'xlrd')
                    dataframes[filename] = df
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
        return dataframes

    def find_and_transform_cdkt_data(self):
        for key in self.dataframes.keys():
            if 'CDKT' in key:
                df = self.transform_cdkt_data(self.dataframes[key])
                return df
        return None

    def transform_cdkt_data(self, df):
        df = df.iloc[4:].reset_index(drop=True).iloc[:130]
        df.columns = df.iloc[0]
        df = df.iloc[1:].dropna(how='all').fillna(0)
        return df

    def filter_and_transform_year(self, df, year):
        stock_code = df.columns[0]
        year_str = str(year)
        if year_str in df.columns:
            filtered_df = df[[stock_code, year_str]].T.reset_index()
            filtered_df.iloc[1, 0] = filtered_df.iloc[0, 0]
            filtered_df.columns = filtered_df.iloc[0]
            filtered_df = filtered_df.iloc[1:]
            filtered_df.rename(columns={filtered_df.columns[0]: 'stock_code'}, inplace=True)
            return filtered_df
        else:
            return None

def process_balance_sheet_base_folder(base_folder, year):
    all_filtered_dfs = []

    for folder_name in os.listdir(base_folder):
        folder_path = os.path.join(base_folder, folder_name)
        if os.path.isdir(folder_path):
            processor = BalancesheetDataProcessor(folder_path)
            cdkt_df = processor.find_and_transform_cdkt_data()
            if cdkt_df is not None:
                filtered_df = processor.filter_and_transform_year(cdkt_df, year)
                if filtered_df is not None:
                    filtered_df = filtered_df.loc[:, ~filtered_df.columns.duplicated()]
                    all_filtered_dfs.append(filtered_df)

    if all_filtered_dfs:
        concatenated_df = pd.concat(all_filtered_dfs, ignore_index=True)
        return concatenated_df
    else:
        return pd.DataFrame()




class IncomestatementDataProcessor:
    def __init__(self, directory_path):
        self.directory_path = directory_path
        self.dataframes = self.load_excel_files()

    def load_excel_files(self):
        dataframes = {}
        for filename in os.listdir(self.directory_path):
            if filename.endswith(".xlsx") or filename.endswith(".xls"):
                file_path = os.path.join(self.directory_path, filename)
                try:
                    df = pd.read_excel(file_path, engine='openpyxl')  # Specify the engine here
                    dataframes[filename] = df
                except (ValueError, pd.errors.EmptyDataError, FileNotFoundError) as e:
                    print(f"Error reading {file_path}: {e}")
                except Exception as e:
                    print(f"An unexpected error occurred while reading {file_path}: {e}")
        return dataframes

    def find_and_transform_kqkd_data(self):
        for key in self.dataframes.keys():
            if 'KQKD' in key:
                df = self.transform_kqkd_data(self.dataframes[key])
                return df
        return None

    def transform_kqkd_data(self, df):
        df = df.iloc[4:].reset_index(drop=True).iloc[:31]
        df.columns = df.iloc[0]
        df = df.iloc[1:].dropna(how='all').fillna(0)
        return df

    def filter_and_transform_year(self, df, year):
        if str(year) not in df.columns:
            return None
        stock_code = df.columns[0]
        filtered_df = df[[stock_code, str(year)]].T.reset_index()
        filtered_df.iloc[1, 0] = filtered_df.iloc[0, 0]
        filtered_df.columns = filtered_df.iloc[0]
        filtered_df = filtered_df.iloc[1:]
        filtered_df.rename(columns={filtered_df.columns[0]: 'stock_code'}, inplace=True)
        return filtered_df


def process_income_statement_base_folder(base_folder, year):
    all_filtered_dfs = []

    for folder_name in os.listdir(base_folder):
        folder_path = os.path.join(base_folder, folder_name)
        if os.path.isdir(folder_path):
            processor = IncomestatementDataProcessor(folder_path)
            kqkd_df = processor.find_and_transform_kqkd_data()
            if kqkd_df is not None:
                filtered_df = processor.filter_and_transform_year(kqkd_df, year)
                if filtered_df is not None:
                    filtered_df = filtered_df.loc[:, ~filtered_df.columns.duplicated()]
                    all_filtered_dfs.append(filtered_df)

    if all_filtered_dfs:
        concatenated_df = pd.concat(all_filtered_dfs, ignore_index=True)
        return concatenated_df
    else:
        return pd.DataFrame()







