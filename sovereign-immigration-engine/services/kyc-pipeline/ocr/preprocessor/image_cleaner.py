import cv2
import numpy as np

class ImageCleaner:
    @staticmethod
    def preprocess(image_path: str) -> str:
        # Load, deskew, and binarize for OCR quality
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        _, thresh = cv2.threshold(img, 150, 255, cv2.THRESH_BINARY)
        cleaned_path = image_path.replace(".png", "_clean.png")
        cv2.imwrite(cleaned_path, thresh)
        return cleaned_path
