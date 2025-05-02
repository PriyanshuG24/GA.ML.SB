import cv2
import numpy as np
import os
import pytesseract
from PIL import Image, ImageEnhance
import re
import tempfile
import shutil
import platform  # for OS detection

pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

def get_valid_digit(text):
    text = re.sub(r'[^0-9]', '', text)
    return int(text) if text.isdigit() and 1 <= int(text) <= 9 else 0

def detect_digits_from_image(image_file, size=9):
    temp_dir = tempfile.mkdtemp()
    try:
        image_path = os.path.join(temp_dir, 'sudoku.png')
        with open(image_path, 'wb') as f:
            f.write(image_file.read())

        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            raise ValueError("Failed to load image")

        thresh = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY_INV, 15, 2)

        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        biggest = None
        max_area = 0
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 50000:
                peri = cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
                if len(approx) == 4 and area > max_area:
                    biggest = approx
                    max_area = area

        if biggest is None:
            raise ValueError("Sudoku grid not found")

        def reorder_points(points):
            points = points.reshape(4, 2)
            new_points = np.zeros((4, 2), dtype=np.float32)
            sum_pts = points.sum(axis=1)
            diff_pts = np.diff(points, axis=1)
            new_points[0] = points[np.argmin(sum_pts)]
            new_points[2] = points[np.argmax(sum_pts)]
            new_points[1] = points[np.argmin(diff_pts)]
            new_points[3] = points[np.argmax(diff_pts)]
            return new_points

        def warp_sudoku(image, contour, size=540):
            reordered = reorder_points(contour)
            destination = np.array([[0, 0], [size - 1, 0], [size - 1, size - 1], [0, size - 1]], dtype=np.float32)
            matrix = cv2.getPerspectiveTransform(reordered, destination)
            return cv2.warpPerspective(image, matrix, (size, size))

        warped_grid = warp_sudoku(image, biggest)
        grid_size = size
        cell_size = warped_grid.shape[0] // grid_size
        crop_margin = 5

        sudoku_grid = np.zeros((grid_size, grid_size), dtype=int)

        for row in range(grid_size):
            for col in range(grid_size):
                x_start, y_start = col * cell_size, row * cell_size
                cell = warped_grid[y_start:y_start + cell_size, x_start:x_start + cell_size]
                cropped_cell = cell[crop_margin:-crop_margin, crop_margin:-crop_margin]

                pil_image = Image.fromarray(cropped_cell)
                enhancer = ImageEnhance.Contrast(pil_image)
                enhanced = enhancer.enhance(1.5)
                cell_np = np.array(enhanced)

                if len(cell_np.shape) == 3:
                    cell_np = cv2.cvtColor(cell_np, cv2.COLOR_RGB2GRAY)

                clahe = cv2.createCLAHE(clipLimit=6.0, tileGridSize=(4, 4))
                cell_np = clahe.apply(cell_np)

                text1 = get_valid_digit(pytesseract.image_to_string(cell_np, config="--psm 6"))
                text2 = get_valid_digit(pytesseract.image_to_string(cell_np, config="--psm 13"))

                sudoku_grid[row][col] = text1 if text1 else text2

        return sudoku_grid.tolist()

    finally:
        shutil.rmtree(temp_dir)
