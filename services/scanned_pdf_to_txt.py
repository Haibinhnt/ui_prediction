import os
from pdf2image import convert_from_path
from PIL import Image, ImageOps
import pytesseract
import string

class IMG2Txt:
    def __init__(self):
        self.custom_config = r'--psm 3 --oem 3'
        self.blocks = None
        self.image = None

    def scan_image(self, img):
        self.texts = []
        self.image = ImageOps.grayscale(img)
        info_text = pytesseract.image_to_data(self.image, config=self.custom_config, lang="vie", output_type=pytesseract.Output.DICT)
        high_image = self.image.height
        data = []

        for i in range(len(info_text['text'])):
            point_data = {}
            if self.pre_clean_word_image(str(info_text['text'][i])):
                point_data["top"] = [info_text['left'][i], high_image - info_text['top'][i]]
                point_data["bot"] = [info_text['left'][i] + info_text['width'][i], high_image - info_text['top'][i] - info_text['height'][i]]
                point_data["height"] = info_text['height'][i]
                point_data["text"] = info_text['text'][i]
                point_data["len"] = len(point_data["text"])
                data.append(point_data)

        for _ in range(5):
            c1 = data
            data = self.merge_words_line(c1)
            if len(c1) == len(data):
                break

        blocks = self.merge_lines_block(data)

        for _ in range(5):
            c2 = blocks
            blocks = self.merge_blocks_para(blocks)
            if len(c2) == len(blocks):
                break

        for block in blocks:
            img1 = self.image.crop((block["top"][0] - 5, high_image - block["top"][1] - 5, block["bot"][0] + 5, high_image - block["bot"][1] + 5))
            text_blocks = pytesseract.image_to_string(img1, lang="vie", config=self.custom_config)
            self.texts.extend([self.clean_text_blocks(line) for line in text_blocks.split("\n") if line.strip()])

        self.blocks = blocks

        if not self.texts:
            return None
        
        output = self._construct_output()
        return output

    def merge_blocks_para(self, list_blocks: list) -> list:
        unique_paras = []
        list_inter_blocks = []
        dict_blocks_copy = [block["text"] for block in list_blocks]

        for i, block in enumerate(list_blocks):
            if block["text"] in dict_blocks_copy:
                group_inter = [block]
                next_dict_block = list_blocks[i + 1:]

                for j, next_block in enumerate(next_dict_block):
                    if self.check_merge_blocks(block, next_block):
                        group_inter.append(next_block)
                        if next_block["text"] in dict_blocks_copy:
                            dict_blocks_copy.remove(next_block["text"])

                list_inter_blocks.append(group_inter)

        for inter_block in list_inter_blocks:
            para = {"top": [10000, 0], "bot": [0, 10000], "lines": []}
            for block in inter_block:
                para["top"] = [min(block["top"][0], para["top"][0]), max(block["top"][1], para["top"][1])]
                para["bot"] = [max(block["bot"][0], para["bot"][0]), min(block["bot"][1], para["bot"][1])]
                para["text"] = inter_block[0]["text"]
                para["lines"] += [line for line in block["lines"] if line not in para["lines"]]
            unique_paras.append(para)

        return unique_paras

    def merge_lines_block(self, list_lines: list) -> list:
        text_blocks = []
        dict_lines_copy = [line["text"] for line in list_lines]

        for i, line in enumerate(list_lines):
            if line["text"] in dict_lines_copy:
                block = {
                    "top": line.get("top", ""),
                    "bot": line.get("bot", ""),
                    "height": line.get("height", ""),
                    "text": line.get("text", ""),
                    "lines": [line.get("text", "")]
                }

                next_dict_lines = list_lines[i + 1:]
                for j, next_line in enumerate(next_dict_lines):
                    if j == 0:
                        bol_check = self.check_merge_lines(block, line, next_line)
                    else:
                        bol_check = self.check_merge_lines(block, next_dict_lines[j - 1], next_line)

                    if bol_check:
                        block["top"] = [min(next_line["top"][0], block["top"][0]), max(next_line["top"][1], block["top"][1])]
                        block["bot"] = [max(next_line["bot"][0], block["bot"][0]), min(next_line["bot"][1], block["bot"][1])]
                        block["height"] = block["top"][1] - next_line["bot"][1]
                        block["text"] += " " + next_line["text"]
                        block["lines"].append(next_line["text"])

                        if next_line["text"] in dict_lines_copy:
                            dict_lines_copy.remove(next_line["text"])

                text_blocks.append(block)

        return text_blocks

    def merge_words_line(self, list_words: list) -> list:
        bol_next_word = False
        n_next = 0
        lines = []

        for i, point in enumerate(list_words):
            if bol_next_word:
                if n_next > 0:
                    n_next -= 1
                    continue

            bol_next_word = False
            line = {
                "top": point.get("top", ""),
                "bot": point.get("bot", ""),
                "height": point.get("height", ""),
                "text": point.get("text", "")
            }

            next_dict_words = list_words[i + 1:]
            for j, next_point in enumerate(next_dict_words):
                if j == 0:
                    bol_check = self.check_merge_words(line, next_point)
                else:
                    bol_check = self.check_merge_words(next_dict_words[j - 1], next_point)

                if bol_check:
                    line["top"] = [min(next_point["top"][0], line["top"][0]), max(next_point["top"][1], line["top"][1])]
                    line["bot"] = [max(next_point["bot"][0], line["bot"][0]), min(next_point["bot"][1], line["bot"][1])]
                    line["height"] = max(line.get("height", ""), next_point.get("height", ""))
                    line["text"] += " " + next_point["text"]
                    n_next += 1
                    bol_next_word = True
                else:
                    break

            lines.append(line)

        return lines

    def check_merge_words(self, word1: dict, word2: dict) -> bool:
        if word2["text"] == "-":
            return abs(word2["top"][0] - word1["bot"][0]) < max(word1["height"], word2["height"])
        elif word1["text"] == "-":
            return True
        else:
            bol1 = abs(word2["top"][0] - word1["bot"][0]) < max(word1["height"], word2["height"])
            bol2 = abs(word2["bot"][1] - word1["bot"][1]) < min(word1["height"], word2["height"]) * 0.5
        return bol1 and bol2

    def check_merge_lines(self, block: dict, line1: dict, line2: dict) -> bool:
        range_line_1 = list(range(line1["top"][0], line1["bot"][0]))
        range_line_2 = list(range(line2["top"][0], line2["bot"][0]))
        range_block = list(range(block["top"][0], block["bot"][0]))

        if line1["height"] > 20:
            MAX_SPACE_2LINE = 20
        else:
            MAX_SPACE_2LINE = line1["height"]

        if self.pre_clean_word_image(line1["text"]) == "":
            return False

        bol1 = abs(line1["bot"][1] - line2["top"][1]) < MAX_SPACE_2LINE
        bol2 = abs(block["bot"][1] - line2["top"][1]) < MAX_SPACE_2LINE
        bol3 = line1["text"] in block["text"]

        if len(range_block) > len(range_line_2):
            bol4 = range_line_2[len(range_line_2) // 2] in range_block
        else:
            bol4 = range_block[len(range_block) // 2] in range_line_2

        bol5 = abs(block["bot"][1] - line2["top"][1]) < MAX_SPACE_2LINE
        if len(range_block) > len(range_line_2):
            bol6 = range_line_2[len(range_line_2) // 2] in range_block
        else:
            bol6 = range_block[len(range_block) // 2] in range_line_2

        return (bol1 and bol2 and bol3 and bol4) or (bol5 and bol6)

    def check_merge_blocks(self, block1: dict, block2: dict) -> bool:
        func_inter_2rect = lambda list1, list2: True if set(list1).intersection(list2) else False
        range_x_block1 = range(block1["top"][0] - 2, block1["bot"][0] + 1)
        range_y_block1 = range(block1["bot"][1] - 2, block1["top"][1] + 1)
        range_x_block2 = range(block2["top"][0] - 2, block2["bot"][0] + 1)
        range_y_block2 = range(block2["bot"][1] - 2, block2["top"][1] + 1)

        return func_inter_2rect(range_x_block1, range_x_block2) and func_inter_2rect(range_y_block1, range_y_block2)

    def pre_clean_word_image(self, text: str) -> str:
        if text == "nan" or len(text) > 20:
            return ""
        text = text.encode("ascii", errors='ignore').decode("utf-8")
        return text.strip()

    def clean_text_blocks(self, text: str) -> str:
        return text.strip()

    def _construct_output(self) -> str:
        output = ""
        for index in range(len(self.texts)):
            if index == 0:
                output = self.texts[index].strip()
                continue
            else:
                if not self.texts[index].strip():
                    continue
                else:
                    if output.strip()[-1] in [",", ":", ";"]:
                        output += " " + self.texts[index].strip()
                    else:
                        if self.texts[index].strip()[0] in string.punctuation:
                            output += ". " + self.texts[index].strip()
                        else:
                            if self.texts[index].strip()[0].isupper():
                                if self.texts[index].strip().split()[0].isupper():
                                    output += " " + self.texts[index].strip()
                                else:
                                    output += ". " + self.texts[index].strip()
                            else:
                                output += " " + self.texts[index].strip()
        return output

def pdf_to_images(pdf_path):
    images = convert_from_path(pdf_path)
    return images

def convert_images_to_text(images):
    img2txt = IMG2Txt()
    texts = []

    for img in images:
        text = img2txt.scan_image(img)
        if text:
            texts.append(text)

    return "\n\n".join(texts)

def pdf_to_text(pdf_path, output_folder):
    images = pdf_to_images(pdf_path)
    text = convert_images_to_text(images)
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    output_path = os.path.join(output_folder, os.path.splitext(os.path.basename(pdf_path))[0] + '.txt')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text)

def process_pdfs_to_text(input_folder, output_folder):
    for filename in os.listdir(input_folder):
        if filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(input_folder, filename)
            pdf_to_text(pdf_path, output_folder)


