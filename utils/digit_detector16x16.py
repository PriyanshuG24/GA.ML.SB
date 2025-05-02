import cv2
import numpy as np
import os
import pytesseract
from PIL import Image, ImageEnhance
import re
import tempfile
import shutil

# Windows users only: Update if Tesseract is installed in a custom path
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

def get_valid_digit(text):
    text = re.sub(r'[^0-9]', '', text)
    if text.isdigit():
        val = int(text)
        return val if 1 <= val <= 16 else 0
    return 0

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

def warp_sudoku(image, contour, size=1440):
    reordered = reorder_points(contour)
    destination = np.array([[0, 0], [size - 1, 0], [size - 1, size - 1], [0, size - 1]], dtype=np.float32)
    matrix = cv2.getPerspectiveTransform(reordered, destination)
    return cv2.warpPerspective(image, matrix, (size, size))

def detect_digits_from_image16x16(image_file,size=16):
    temp_dir = tempfile.mkdtemp()
    image_path = os.path.join(temp_dir, 'sudoku_16x16.png')
    with open(image_path, 'wb') as f:
        f.write(image_file.read())

    original = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    thresh = cv2.adaptiveThreshold(original, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 15, 2)

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
        shutil.rmtree(temp_dir)
        raise ValueError("Sudoku grid not found")

    warped = warp_sudoku(original, biggest, size=1440)
    grid_size = 16
    cell_size = warped.shape[0] // grid_size
    crop_margin = 8
    sudoku_grid = np.zeros((grid_size, grid_size), dtype=int)

    for row in range(grid_size):
        for col in range(grid_size):
            x_start, y_start = col * cell_size, row * cell_size
            cell = warped[y_start:y_start + cell_size, x_start:x_start + cell_size]
            cropped = cell[crop_margin:-crop_margin, crop_margin:-crop_margin]

            # Preprocess twice with different enhancements
            pil1 = ImageEnhance.Contrast(Image.fromarray(cropped)).enhance(1.8)
            pil2 = ImageEnhance.Contrast(Image.fromarray(cropped)).enhance(2.0)
            cell1 = np.array(pil1)
            cell2 = np.array(pil2)

            if len(cell1.shape) == 3:
                cell1 = cv2.cvtColor(cell1, cv2.COLOR_RGB2GRAY)
            if len(cell2.shape) == 3:
                cell2 = cv2.cvtColor(cell2, cv2.COLOR_RGB2GRAY)

            cell1 = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(4, 4)).apply(cell1)
            cell2 = cv2.createCLAHE(clipLimit=6.0, tileGridSize=(4, 4)).apply(cell2)

            text1 = get_valid_digit(pytesseract.image_to_string(cell1, config="--psm 6").strip())
            text2 = get_valid_digit(pytesseract.image_to_string(cell2, config="--psm 13").strip())

            text = 0
            if 10 <= text1 <= 16:
                text = text1
            elif 10 <= text2 <= 16:
                text = text2
            elif 1 <= text1 <= 9 and 1 <= text2 <= 9:
                text = text1

            sudoku_grid[row, col] = text
            # print(f"{row},{col} => OCR: {text1}, {text2} -> Final: {text}")

    shutil.rmtree(temp_dir)
    return sudoku_grid.tolist()
