import os
import pandas as pd
from services.word_tokenize import VietnameseTextTokenizer

class Word_Frequency:
    def __init__(self, input_folder, positive_output_folder, negative_output_folder):
        self.input_folder = input_folder
        self.positive_word_list_path = 'data/positive_word_list.xlsx'
        self.negative_word_list_path = 'data/negative_word_list.xlsx'
        self.positive_output_folder = positive_output_folder
        self.negative_output_folder = negative_output_folder
        self.tokenizer = VietnameseTextTokenizer()
        self._create_output_folders()

    def _create_output_folders(self):
        os.makedirs(self.positive_output_folder, exist_ok=True)
        os.makedirs(self.negative_output_folder, exist_ok=True)

    def _read_file(self, input_file_path):
        with open(input_file_path, 'r', encoding='utf-8') as f:
            return f.read()

    def _process_word_list(self, word_list_path, tokenized_text):
        # Load word list
        word_list = pd.read_excel(word_list_path)
        word_list['tokenized_word'] = word_list[word_list.columns[0]].apply(lambda x: self.tokenizer.process_text(x))
        word_list['tokenized_word'] = word_list['tokenized_word'].apply(lambda x: ' '.join(x))
        word_list['count'] = word_list['tokenized_word'].apply(lambda x: tokenized_text.count(x))
        word_list = word_list[word_list['count'] > 0]
        word_list = word_list.sort_values(by='count', ascending=False)
        return word_list

    def _save_word_list(self, word_list, output_folder, filename):
        output_file_path = os.path.join(output_folder, filename + '.csv')
        word_list.to_csv(output_file_path, index=False)
        print(f"Word list saved to {output_file_path}")

    def process_text(self, input_file_path):
        self.filename_with_ext = os.path.basename(input_file_path)
        self.filename, _ = os.path.splitext(self.filename_with_ext)
        self.text = self._read_file(input_file_path)
        tokenized_text = self.tokenizer.process_text(self.text)

        positive_word_list = self._process_word_list(self.positive_word_list_path, tokenized_text)
        self._save_word_list(positive_word_list, self.positive_output_folder, self.filename)

        negative_word_list = self._process_word_list(self.negative_word_list_path, tokenized_text)
        self._save_word_list(negative_word_list, self.negative_output_folder, self.filename)

    def process_all_files_in_folder(self):
        for filename in os.listdir(self.input_folder):
            file_path = os.path.join(self.input_folder, filename)
            if os.path.isfile(file_path) and file_path.endswith('.txt'):
                self.process_text(file_path)
