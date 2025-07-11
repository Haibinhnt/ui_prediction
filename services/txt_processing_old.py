import re
from underthesea import word_tokenize
from services.VietnameseOcrCorrection.tool.predictor import Predictor
from langdetect import detect, DetectorFactory

# Ensure reproducibility for language detection
DetectorFactory.seed = 0

class VietnameseTextPreprocessor:
    def __init__(self, device='cpu', model_type='seq2seq', weight_path='services/VietnameseOcrCorrection/weights/seq2seq_0.pth'):
        # Initialize the Predictor
        self.model_predictor = Predictor(device=device, model_type=model_type, weight_path=weight_path)
        # Load Vietnamese dictionary from Viet74K.txt
        self.vietnamese_words = self.load_vietnamese_dictionary('data/Viet74K.txt')

    def load_vietnamese_dictionary(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            words = file.read().splitlines()
        # Store words in a list, converting them to lowercase
        return [word.lower() for word in words]

    def print_vietnamese_words(self):
            print(self.vietnamese_words)

    def to_lowercase(self, text):
        return text.lower()

    def remove_special_characters_and_numbers(self, text):
        # Loại bỏ các ký tự đặc biệt và số bằng cách thay thế bằng chuỗi rỗng
        cleaned_text = re.sub(r'[^\w\s]', '', text)  # Loại bỏ ký tự đặc biệt
        cleaned_text = re.sub(r'\d+', '', cleaned_text)  # Loại bỏ số
        return cleaned_text

    def tokenize(self, text):
        return word_tokenize(text)

    def preprocess(self, text):
        text = self.to_lowercase(text)
        text = self.remove_special_characters_and_numbers(text)
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

        # Filter characters not in the vocabulary
        filtered_paragraphs = []
        for c in cleaned_text:
            if c in self.model_predictor.vocab.c2i:
                filtered_paragraphs.append(c)
            else:
                filtered_paragraphs.append(' ')

        corrected_text = self.model_predictor.predict(''.join(filtered_paragraphs).strip(), NGRAM=ngram)

        # Tokenize after correction
        tokenized_text = self.tokenize(corrected_text)
        return ' '.join(tokenized_text)

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

    def get_tokenized_words_from_file(self, input_file_path, ngram=6):
        '''
        Function to read text from a file, clean it, correct it,
        and return the tokenized words as a list.
        Args:
        input_file_path (str): Path to the input text file.
        ngram (int): The N-gram value for prediction.
        Returns:
        List[str]: List of tokenized words.
        '''
        with open(input_file_path, 'r', encoding='utf-8') as file:
            paragraphs = file.read()

        cleaned_and_corrected_paragraphs = self.clean_and_correct_text(paragraphs, ngram)
        tokenized_words = self.tokenize(cleaned_and_corrected_paragraphs)
        return tokenized_words

    def detect_non_vietnamese_words(self, tokenized_words):
        '''
        Function to detect non-Vietnamese words in the tokenized words.
        Args:
        tokenized_words (List[str]): List of tokenized words.
        Returns:
        List[str]: List of non-Vietnamese words.
        '''
        non_vietnamese_words = []
        for word in tokenized_words:
            try:
                if detect(word) != 'vi' and word not in self.vietnamese_words:
                    non_vietnamese_words.append(word)
            except:
                # Handle cases where the language cannot be detected
                if word not in self.vietnamese_words:
                    non_vietnamese_words.append(word)
        return non_vietnamese_words

    def filter_non_vietnamese_words(self, tokenized_words):
        '''
        Function to filter out non-Vietnamese words from the tokenized words list.
        Args:
        tokenized_words (List[str]): List of tokenized words.
        Returns:
        List[str]: List of tokenized words with non-Vietnamese words removed.
        '''
        non_vietnamese_words = self.detect_non_vietnamese_words(tokenized_words)
        filtered_words = [word for word in tokenized_words if word not in non_vietnamese_words and len(word) > 1]
        return filtered_words
