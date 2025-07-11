import pandas as pd
import os
from PyPDF2 import PdfReader

def get_pdf_details(directory, year):
    # Create a dataframe to store the pdf file details
    df = pd.DataFrame(columns=['fileName', 'pageNumber', 'year'])
    # Walk through the directory
    for root, dirs, files in os.walk(directory):
        for f in files:
            if f.endswith(".pdf"):
                try:
                    with open(os.path.join(root, f), 'rb') as pdf_file:
                        pdf = PdfReader(pdf_file)
                        df2 = pd.DataFrame([[f, len(pdf.pages), year]], columns=['fileName', 'pageNumber', 'year'])
                        df = pd.concat([df, df2], ignore_index=True)
                except Exception as e:
                    print(f"Error reading {f}: {e}. Skipping file.")
    return df

def missing_files(df, excel_path):
    # get beginning numbers of the fileName column
    df['No.'] = df['fileName'].str.extract(r'(\d+)')
    df['No.'] = pd.to_numeric(df['No.'])
    df2 = pd.read_excel(excel_path)
    df2['No.'] = pd.to_numeric(df2['No.'])
    missing_df = df2[~df2['No.'].isin(df['No.'])]
    return missing_df

def process_pdf_files_and_find_missing(directories, excel_path, years):
    combined_df = pd.DataFrame(columns=['fileName', 'pageNumber', 'year'])
    missing_files_list = []
    
    for directory, year in zip(directories, years):
        # Get PDF details
        df = get_pdf_details(directory, year)
        combined_df = pd.concat([combined_df, df], ignore_index=True)
        
        # Find missing files
        missing_df = missing_files(df, excel_path)
        missing_files_list.append((year, missing_df))
        
    return combined_df, missing_files_list