import re
import ast
import unicodedata as ud
import os


class VietnameseTextTokenizer:
    def __init__(self):
        # Load Vietnamese dictionary from Viet74K.txt
        self.vietnamese_words = self.load_vietnamese_dictionary('data/Viet74K.txt')
        # Load N-grams
        self.bi_grams = self.load_n_grams('data/n_gram/bi_grams.txt')
        self.tri_grams = self.load_n_grams('data/n_gram/tri_grams.txt')
        self.four_grams = self.load_n_grams('data/n_gram/four_grams.txt')
        self.five_grams = self.load_n_grams('data/n_gram/five_grams.txt')
        self.six_grams = self.load_n_grams('data/n_gram/six_grams.txt')
        self.seven_grams = self.load_n_grams('data/n_gram/seven_grams.txt')

    def load_vietnamese_dictionary(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            words = file.read().splitlines()
        return [word.lower() for word in words]

    def load_n_grams(self, path):
        with open(path, encoding='utf8') as f:
            words = f.read()
            try:
                words = ast.literal_eval(words)
            except (SyntaxError, ValueError):
                raise ValueError(f"File content at {path} is not a valid Python literal")
        return words

    def syllablize(self, text):
        word = r'\w+'
        non_word = r'[^\w\s]'
        digits = r'\d+([\.,_]\d+)+'

        patterns = []
        patterns.extend([word, non_word, digits])
        patterns = f"({'|'.join(patterns)})"

        text = ud.normalize('NFC', text)
        tokens = re.findall(patterns, text, re.UNICODE)
        return [token for group in tokens for token in group if token]  # Flatten the list and remove empty strings

    def longest_matching(self, text):
        syllables = self.syllablize(text)
        syl_len = len(syllables)

        curr_id = 0
        word_list = []
        done = False

        while (curr_id < syl_len) and (not done):
            curr_word = syllables[curr_id]
            if curr_id >= syl_len - 1:
                word_list.append(curr_word)
                done = True
            else:
                next_word = syllables[curr_id + 1]
                pair_word = ' '.join([curr_word.lower(), next_word.lower()])

                if curr_id >= (syl_len - 2):
                    if pair_word in self.bi_grams:
                        word_list.append('_'.join([curr_word, next_word]))
                        curr_id += 2
                    else:
                        word_list.append(curr_word)
                        curr_id += 1
                else:
                    next_next_word = syllables[curr_id + 2]
                    triple_word = ' '.join([pair_word, next_next_word.lower()])

                    if curr_id >= (syl_len - 3):
                        if triple_word in self.tri_grams:
                            word_list.append('_'.join([curr_word, next_word, next_next_word]))
                            curr_id += 3
                        elif pair_word in self.bi_grams:
                            word_list.append('_'.join([curr_word, next_word]))
                            curr_id += 2
                        else:
                            word_list.append(curr_word)
                            curr_id += 1
                    else:
                        next_next_next_word = syllables[curr_id + 3]
                        four_word = ' '.join([triple_word, next_next_next_word.lower()])

                        if curr_id >= (syl_len - 4):
                            if self.four_grams and four_word in self.four_grams:
                                word_list.append('_'.join([curr_word, next_word, next_next_word, next_next_next_word]))
                                curr_id += 4
                            elif triple_word in self.tri_grams:
                                word_list.append('_'.join([curr_word, next_word, next_next_word]))
                                curr_id += 3
                            elif pair_word in self.bi_grams:
                                word_list.append('_'.join([curr_word, next_word]))
                                curr_id += 2
                            else:
                                word_list.append(curr_word)
                                curr_id += 1
                        else:
                            next_next_next_next_word = syllables[curr_id + 4]
                            five_word = ' '.join([four_word, next_next_next_next_word.lower()])

                            if curr_id >= (syl_len - 5):
                                if self.five_grams and five_word in self.five_grams:
                                    word_list.append('_'.join([curr_word, next_word, next_next_word, next_next_next_word, next_next_next_next_word]))
                                    curr_id += 5
                                elif self.four_grams and four_word in self.four_grams:
                                    word_list.append('_'.join([curr_word, next_word, next_next_word, next_next_next_word]))
                                    curr_id += 4
                                elif triple_word in self.tri_grams:
                                    word_list.append('_'.join([curr_word, next_word, next_next_word]))
                                    curr_id += 3
                                elif pair_word in self.bi_grams:
                                    word_list.append('_'.join([curr_word, next_word]))
                                    curr_id += 2
                                else:
                                    word_list.append(curr_word)
                                    curr_id += 1
                            else:
                                next_next_next_next_next_word = syllables[curr_id + 5]
                                six_word = ' '.join([five_word, next_next_next_next_next_word.lower()])

                                if curr_id >= (syl_len - 6):
                                    if self.six_grams and six_word in self.six_grams:
                                        word_list.append('_'.join([curr_word, next_word, next_next_word, next_next_next_word, next_next_next_next_word, next_next_next_next_next_word]))
                                        curr_id += 6
                                    elif self.five_grams and five_word in self.five_grams:
                                        word_list.append('_'.join([curr_word, next_word, next_next_word, next_next_next_word, next_next_next_next_word]))
                                        curr_id += 5
                                    elif self.four_grams and four_word in self.four_grams:
                                        word_list.append('_'.join([curr_word, next_word, next_next_word, next_next_next_word]))
                                        curr_id += 4
                                    elif triple_word in self.tri_grams:
                                        word_list.append('_'.join([curr_word, next_word, next_next_word]))
                                        curr_id += 3
                                    elif pair_word in self.bi_grams:
                                        word_list.append('_'.join([curr_word, next_word]))
                                        curr_id += 2
                                    else:
                                        word_list.append(curr_word)
                                        curr_id += 1
                                else:
                                    next_next_next_next_next_next_word = syllables[curr_id + 6]
                                    seven_word = ' '.join([six_word, next_next_next_next_next_next_word.lower()])

                                    if self.seven_grams and seven_word in self.seven_grams:
                                        word_list.append('_'.join([curr_word, next_word, next_next_word, next_next_next_word, next_next_next_next_word, next_next_next_next_next_word, next_next_next_next_next_next_word]))
                                        curr_id += 7
                                    elif self.six_grams and six_word in self.six_grams:
                                        word_list.append('_'.join([curr_word, next_word, next_next_word, next_next_next_word, next_next_next_next_word, next_next_next_next_next_word]))
                                        curr_id += 6
                                    elif self.five_grams and five_word in self.five_grams:
                                        word_list.append('_'.join([curr_word, next_word, next_next_word, next_next_next_word, next_next_next_next_word]))
                                        curr_id += 5
                                    elif self.four_grams and four_word in self.four_grams:
                                        word_list.append('_'.join([curr_word, next_word, next_next_word, next_next_next_word]))
                                        curr_id += 4
                                    elif triple_word in self.tri_grams:
                                        word_list.append('_'.join([curr_word, next_word, next_next_word]))
                                        curr_id += 3
                                    elif pair_word in self.bi_grams:
                                        word_list.append('_'.join([curr_word, next_word]))
                                        curr_id += 2
                                    else:
                                        word_list.append(curr_word)
                                        curr_id += 1
        return word_list

    def remove_punctuation(self, words):
        return [word.replace(',', '').replace('.', '') for word in words]

    def process_text(self, text):
        word_list = self.longest_matching(text)
        cleaned_word_list = self.remove_punctuation(word_list)
        cleaned_word_list = [word for word in cleaned_word_list if len(word) > 2 and word != '_']
        return cleaned_word_list
    def process_text_file(self, input_file_path, output_file_path):
        with open(input_file_path, 'r', encoding='utf-8') as file:
            text = file.read()
        processed_text = ' '.join(self.process_text(text))
        with open(output_file_path, 'w', encoding='utf-8') as file:
            file.write(processed_text)

    def process_files_in_folder(self, input_folder, output_folder):
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        for filename in os.listdir(input_folder):
            if filename.endswith('.txt'):
                input_file_path = os.path.join(input_folder, filename)
                output_file_path = os.path.join(output_folder, filename)
                self.process_text_file(input_file_path, output_file_path)

