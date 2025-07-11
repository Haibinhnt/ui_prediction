import cv2
import numpy as np
from array import array
import pytesseract
from fitz import Page
from operator import itemgetter
from util.util import compare_rect


class Image_PDF:
    """ 
    The object to find all tables in image of file PDF.
    """

    def __init__(self) -> None:
        pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        pass

    def extract_tables(self, image_pdf: np.ndarray) -> list:
        """ To find all table in PDF

        Parameters
        ----------
        `image_pdf`: np.ndarray
            The image of PDF to find table. 

        Returns
        -------
        List: [ position_tables, image_tables]
            - `position_tables`: This list stores all position (x,y,w,h) of tables.
            - `image_tables`: This list stores all image of tables.
        """
        in_image = image_pdf
        ##### Convert gray image into binary image (Always)
        MAX_COLOR_VAL = 255
        BLOCK_SIZE = 7
        SUBTRACT_FROM_MEAN = -20

        img_bin = cv2.adaptiveThreshold(~in_image, MAX_COLOR_VAL,
                                        cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY,
                                        BLOCK_SIZE, SUBTRACT_FROM_MEAN, )

        vertical = horizontal = img_bin.copy()
        image_width, image_height = horizontal.shape
        assert image_height > 120 , "Input image is not a image of file PDF."

        ##### Detect vertical_line of table in image
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, image_height // 120))
        eroded_image = cv2.erode(img_bin, vertical_kernel, )
        vertical_lines = cv2.morphologyEx(eroded_image, cv2.MORPH_OPEN, vertical_kernel, iterations=3)
        vertical_lines = cv2.dilate(vertical_lines, vertical_kernel, iterations=2)

        kernel_vertical_bold = np.ones((2, 20))
        kernel_vertical_thin = np.ones((1, 5))

        vertical_lines = cv2.dilate(vertical_lines, kernel_vertical_bold)
        vertical_lines = cv2.erode(vertical_lines, kernel_vertical_thin, iterations=4)

        ##### Detect horizontal_lines of table in image
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (image_width // 150, 1))
        eroded_image = cv2.erode(img_bin, horizontal_kernel)
        horizontal_lines = cv2.morphologyEx(eroded_image, cv2.MORPH_OPEN, horizontal_kernel, iterations=3)
        horizontal_lines = cv2.dilate(horizontal_lines, horizontal_kernel, iterations=2)

        kernel_horizontal_bold = np.ones((20, 2))
        kernel_horizontal_thin = np.ones((5, 1))

        horizontal_lines = cv2.dilate(horizontal_lines, kernel_horizontal_bold)
        horizontal_lines = cv2.erode(horizontal_lines, kernel_horizontal_thin, iterations=4)

        ##### Add horizontal_line and vertical_line
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        vertical_horizontal_lines = cv2.addWeighted(vertical_lines, 0.5, horizontal_lines, 0.5, 0.0)
        vertical_horizontal_lines = cv2.erode(vertical_horizontal_lines, kernel)
        thresh, vertical_horizontal_lines = cv2.threshold(vertical_horizontal_lines, 128, 255,
                                                          cv2.THRESH_BINARY | cv2.THRESH_OTSU)

        ##### Find table base on horizontal and vertical
        contours, heirarchy = cv2.findContours(vertical_horizontal_lines, 
                                               cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE, )

        MIN_TABLE_AREA = 20
        contours = [c for c in contours if cv2.contourArea(c) > MIN_TABLE_AREA]
        perimeter_lengths = [cv2.arcLength(c, True) for c in contours]
        epsilons = [0.1 * p for p in perimeter_lengths]
        approx_polys = [cv2.approxPolyDP(c, e, True) for c, e in zip(contours, epsilons)]
        bounding_rects = [cv2.boundingRect(a) for a in approx_polys]

        ##### Filter all cells in table -> only table
        pos_table = self.find_rect_tables(list_rects=bounding_rects)

        position_tables = []
        image_tables = []
        for table in pos_table:
            x, y, w, h = table
            image = in_image[max(y-10, 0) :y+h+5, max(x-10,0) :x+w+5]
            if pytesseract.image_to_string(image=image) != "":
                position_tables.append(table)
                image_tables.append(image)

        return [position_tables, image_tables]

    def extract_cells(self, table_img: np.ndarray, table_pos: tuple) -> list:
        """ To find all cell in image table
        
        Parameters
        ----------
        `table_img`: np.ndarray
            The image of table to find cells. 

        Returns
        -------
        List: [ var_bol, position_cells, image_cells]
            - `var_bol`: variable bool if True `table_img` is image table else background bounding. 
            - `position_cells`: This list stores all position (x,y,w,h) of cells.
            - `image_cells`: This list stores all image of cells.
        """
        MAX_COLOR_VAL = 255
        BLOCK_SIZE = 7
        SUBTRACT_FROM_MEAN = -20

        ##### Convert gray image into binary image (Always)
        img_bin = cv2.adaptiveThreshold(~table_img, MAX_COLOR_VAL,
                                        cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY,
                                        BLOCK_SIZE, SUBTRACT_FROM_MEAN, )

        table_height, table_width = table_img.shape
        assert table_height > 1 , "Input image is not a table."
        img_bin[5:table_height - 5, 7:10] = 255
        img_bin[7:10, 5:table_width - 5] = 255
        img_bin[5:table_height - 5, table_width - 10: table_width - 7] = 255
        img_bin[table_height - 10: table_height - 7, 5:table_width - 5] = 255

        ##### Detect horizontal_lines of cell in table
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 1))
        eroded_image = cv2.erode(img_bin, horizontal_kernel)
        horizontal_lines = cv2.morphologyEx(eroded_image, cv2.MORPH_OPEN, horizontal_kernel, iterations=3)
        horizontal_lines = cv2.dilate(horizontal_lines, horizontal_kernel, iterations=2)

        kernel_horizontal_bold = np.ones((20, 2))
        kernel_thin = np.ones((5, 1))

        horizontal_lines = cv2.dilate(horizontal_lines, kernel_horizontal_bold)
        horizontal_lines = cv2.erode(horizontal_lines, kernel_thin, iterations=4)

        ##### Detect vertical_line of cell in table
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 20))
        eroded_image = cv2.erode(img_bin, vertical_kernel, )
        vertical_lines = cv2.morphologyEx(eroded_image, cv2.MORPH_OPEN, vertical_kernel, iterations=3)
        vertical_lines = cv2.dilate(vertical_lines, vertical_kernel, iterations=2)

        kernel_vertical_bold = np.ones((2, 20))
        kernel_thin = np.ones((1, 5))

        vertical_lines = cv2.dilate(vertical_lines, kernel_vertical_bold)
        vertical_lines = cv2.erode(vertical_lines, kernel_thin, iterations=4)

        ##### Add horizontal_line and vertical_line
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))

        vertical_horizontal_lines = cv2.addWeighted(vertical_lines, 0.5, horizontal_lines, 0.5, 0.0)
        vertical_horizontal_lines = cv2.erode(~vertical_horizontal_lines, kernel, iterations=3)

        thresh, vertical_horizontal_lines = cv2.threshold(vertical_horizontal_lines, 128, 255,
                                                          cv2.THRESH_BINARY | cv2.THRESH_OTSU)

        ##### Find table base on horizontal and vertical
        contours, heirarchy = cv2.findContours(vertical_horizontal_lines, 
                                               cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE, )

        MIN_TABLE_AREA = 10
        contours = [c for c in contours if cv2.contourArea(c) > MIN_TABLE_AREA]
        perimeter_lengths = [cv2.arcLength(c, True) for c in contours]
        epsilons = [0.1 * p for p in perimeter_lengths]
        approx_polys = [cv2.approxPolyDP(c, e, True) for c, e in zip(contours, epsilons)]
        bounding_cells = [cv2.boundingRect(a) for a in approx_polys]

        ##### Filter overlaps cell in list_cells -> only unique cells
        S_table = table_pos[2] * table_pos[3]
        var_bol, pos_cells = self.find_rect_cells(list_rects=bounding_cells, S_table=S_table)

        image_cells = []
        position_cells = []
        for cell in pos_cells:
            x, y, w, h = cell
            image = table_img[max(y-10, 0) :y+h+5, max(x-10,0) :x+w+5]
            if pytesseract.image_to_string(image= image) != "":
                    position_cells.append(cell)
                    image_cells.append(image)

        return [var_bol, position_cells, image_cells]

    def convert_position_img2pdf(self, pos_img: list, page: Page, image: array) -> list:
        """ To convert position of table in Image to PDF.

        Parameters
        ----------
        `pos_img`: List
            List position of table in Image.
        `page`: Page
            Page of PDF is read by fitz.
        `image`: array
            Image of a page PDF.

        Returns
        ------
        List: `pdf_tables`
            List position of table in PDF.
        """
        h_PDF, w_PDF = page.rect.height, page.rect.width
        h_Image, w_Image = image.shape
        pdf_tables = []
        for table in pos_img:
            pos_table = table[0]
            pos_cells = table[1]

            pdf_cells = []
            for pos_cell in pos_cells:
                pdf_cells.append([[
                    round((pos_table[0] + pos_cell[0][0] - 15) * w_PDF / w_Image),
                    round((pos_table[1] + pos_cell[0][1] - 15) * h_PDF / h_Image),
                    round((pos_table[0] + pos_cell[0][0] + pos_cell[0][2]) * w_PDF / w_Image),
                    round((pos_table[1] + pos_cell[0][1] + pos_cell[0][3]) * h_PDF / h_Image)
                ], pos_cell[1]])
            pdf_tables.append([tuple([
                round(pos_table[0] * w_PDF / w_Image),
                round(pos_table[1] * h_PDF / h_Image),
                round((pos_table[0] + pos_table[2]) * w_PDF / w_Image),
                round((pos_table[1] + pos_table[3]) * h_PDF / h_Image)]),
                pdf_cells])
        return pdf_tables

    @staticmethod
    def find_rect_tables(list_rects: list) -> list:
        """Function using to find all tables in `bounding rect` 
            or filter all cells in table.

        Parameters
        ----------
        `list_rects`: List
            List of bounding rects in method `extract_table()`.

        Returns
        -------
        List table is sorted
        """
        sorted_list = sorted(list_rects, key=itemgetter(1, 0))
        list_tables = []
        for rect in sorted_list:
            bool_table = False
            if list_tables:
                for pre_rect in list_tables:
                    if compare_rect(rect, pre_rect):
                        bool_table = True
            if bool_table == False:
                if rect[2] > 20 and rect[3] > 20 and rect[0] != 0 and rect[1] != 0:
                    list_tables.append(rect)
        return sorted(list_tables, key=itemgetter(1, 0))

    @staticmethod
    def find_rect_cells(list_rects: list, S_table: int) -> list:
        """Function using to find all cells in bounding rect or filter all table.
            Only find all cells and check image table.

        Parameters
        ----------
        `list_rects`: List
            List of bounding rects in method `extract_cells()`.
        `S_table`: int
            To check image is table or not.

        Returns
        -------
        List: [[True/False, Ratio_area], list_cells]
            - `True/False`: Check image is background bounding or table.
            - `Ratio_area`: Ratio of all area cell / area table.
            - `list_cells`: A list cell is sorted.
        """
        sorted_list = sorted(list_rects, key=itemgetter(1, 0))
        list_cells = []
        for rect in sorted_list:
            bool_cell = False
            if list_cells:
                for pre_rect in list_cells:
                    if compare_rect(rect, pre_rect):
                        bool_cell = True
            if bool_cell == False:
                S_cell = rect[3] * rect[2]
                if rect[2] > 20 and rect[3] > 20 and rect[0] != 0 and rect[1] != 0 and S_cell < 0.9 * S_table:
                    list_cells.append(rect)
        S_total_cell = 0
        for cell in list_cells:
            S_total_cell += cell[2] * cell[3]

        return [[S_total_cell / S_table > 0.775, S_total_cell / S_table], sorted(list_cells, key=itemgetter(1, 0))]
