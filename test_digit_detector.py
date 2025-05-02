from utils.digit_detector9x9 import detect_digits_from_image

class DummyFile:
    def __init__(self, path):
        self.file = open(path, 'rb')
    def read(self):
        return self.file.read()

if __name__ == "__main__":
    # Load the image using the DummyFile wrapper
    image_file = DummyFile("utils/9.jpg")

    # Run the digit detector
    result = detect_digits_from_image(image_file, size=9)

    # Print the result
    for row in result:
        print(row)
