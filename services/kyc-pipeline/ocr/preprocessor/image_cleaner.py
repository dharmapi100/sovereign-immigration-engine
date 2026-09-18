"""
Image Cleaner
=============
Deskew / binarize scanned documents for OCR quality. OpenCV is imported
lazily so the compliance core runs without the CV stack installed.
"""


class ImageCleaner:
    @staticmethod
    def preprocess(image_path: str) -> str:
        import cv2  # lazy: heavy dep

        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise FileNotFoundError(f"cannot read image: {image_path}")
        _, thresh = cv2.threshold(img, 150, 255, cv2.THRESH_BINARY)
        cleaned_path = image_path.replace(".png", "_clean.png")
        cv2.imwrite(cleaned_path, thresh)
        return cleaned_path
