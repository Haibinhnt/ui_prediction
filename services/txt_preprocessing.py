import os
import re
from services.VietnameseOcrCorrection.tool.predictor import Predictor


class VietnameseTextPreprocessor:
    def __init__(self, device='cpu', model_type='seq2seq',
                 weight_path='services/VietnameseOcrCorrection/weights/seq2seq_0.pth',
                 abbreviation_file='data/abbreviations.txt'):
        # Initialize the Predictor
        self.model_predictor = Predictor(device=device, model_type=model_type, weight_path=weight_path)
        # Load abbreviation dictionary from file
        self.abbreviation_dict = self.load_abbreviation_dictionary(abbreviation_file)

    def load_abbreviation_dictionary(self, file_path):
        abbreviation_dict = {}
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            for line in lines:
                abbreviation, full_form = line.strip().split('=')
                abbreviation_dict[abbreviation.strip()] = full_form.strip()
        return abbreviation_dict

    def to_lowercase(self, text):
        return text.lower()

    def remove_special_characters_and_numbers(self, text):
        # Loại bỏ các ký tự đặc biệt và số bằng cách thay thế bằng chuỗi rỗng
        cleaned_text = re.sub(r'[^\w\s.,]', '', text)  # Loại bỏ ký tự đặc biệt trừ dấu chấm và dấu phẩy
        cleaned_text = re.sub(r'\d+', '', cleaned_text)  # Loại bỏ số
        return cleaned_text

    def preprocess(self, text):
        text = self.to_lowercase(text)
        text = self.remove_special_characters_and_numbers(text)
        text = self.replace_abbreviations(text)
        return text

    def replace_abbreviations(self, text):
        # Sử dụng biểu thức chính quy để thay thế từ viết tắt bằng từ đầy đủ
        for abbreviation, full_form in self.abbreviation_dict.items():
            # Thay thế toàn bộ từ viết tắt không phân biệt chữ hoa chữ thường
            text = re.sub(r'\b' + re.escape(abbreviation) + r'\b', full_form, text, flags=re.IGNORECASE)
        return text

    def clean_and_correct_text(self, paragraphs, ngram=6):
        '''
        Function to remove special characters and numbers, then correct the text using a seq2seq model.
        Args:
        paragraphs (str): The input text to be cleaned and corrected.
        ngram (int): The N-gram value for prediction.
        Returns:
        str: The cleaned and corrected text.
        '''
        # Thực hiện lowercase
        paragraphs = self.to_lowercase(paragraphs)

        # Remove special characters and numbers
        cleaned_text = self.remove_special_characters_and_numbers(paragraphs)

        # Thay thế các từ viết tắt
        cleaned_text = self.replace_abbreviations(cleaned_text)

        # Filter characters not in the vocabulary
        filtered_paragraphs = []
        for c in cleaned_text:
            if c in self.model_predictor.vocab.c2i:
                filtered_paragraphs.append(c)
            else:
                filtered_paragraphs.append(' ')

        corrected_text = self.model_predictor.predict(''.join(filtered_paragraphs).strip(), NGRAM=ngram)

        return corrected_text

    def clean_and_correct_text_file(self, input_file_path, output_file_path, ngram=6):
        '''
        Function to read text from a file, clean it, correct it,
        and write the cleaned and corrected text to a new file.
        Args:
        input_file_path (str): Path to the input text file.
        output_file_path (str): Path to the output text file.
        ngram (int): The N-gram value for prediction.
        '''
        with open(input_file_path, 'r', encoding='utf-8') as file:
            paragraphs = file.read()

        cleaned_and_corrected_paragraphs = self.clean_and_correct_text(paragraphs, ngram)

        with open(output_file_path, 'w', encoding='utf-8') as file:
            file.write(cleaned_and_corrected_paragraphs)

    def clean_and_correct_texts_in_folder(self, input_folder_path, output_folder_path, ngram=6):
        '''
        Function to read all text files from a folder, clean and correct them,
        and write the cleaned and corrected texts to a new folder.
        Args:
        input_folder_path (str): Path to the input folder containing text files.
        output_folder_path (str): Path to the output folder to save cleaned and corrected text files.
        ngram (int): The N-gram value for prediction.
        '''
        if not os.path.exists(output_folder_path):
            os.makedirs(output_folder_path)

        for filename in os.listdir(input_folder_path):
            if filename.endswith('.txt'):
                input_file_path = os.path.join(input_folder_path, filename)
                output_file_path = os.path.join(output_folder_path, filename)
                self.clean_and_correct_text_file(input_file_path, output_file_path, ngram)
