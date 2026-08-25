import easyocr

class OCRProcessor:
    def __init__(self):
        # Initialize easyocr reader (supports Korean: 'ko')
        self.reader = easyocr.Reader(['ko', 'en'])

    def extract_text(self, image_path: str) -> str:
        results = self.reader.readtext(image_path, detail=0)
        return " ".join(results)
