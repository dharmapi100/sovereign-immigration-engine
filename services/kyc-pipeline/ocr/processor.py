"""
OCR Processor (Korean + English)
================================
Wraps easyocr. The heavy dependency is imported lazily so the core
compliance pipeline (audit ledger, PIPA DSL) runs on machines where the
OCR stack is not installed — OCR is only needed when an image is supplied.
"""


class OCRProcessor:
    def __init__(self):
        self._reader = None

    def _ensure_reader(self):
        if self._reader is None:
            try:
                import easyocr  # lazy: heavy dep
            except ImportError as exc:  # pragma: no cover
                raise RuntimeError(
                    "easyocr is required for image OCR. "
                    "Install with: pip install easyocr"
                ) from exc
            self._reader = easyocr.Reader(["ko", "en"])
        return self._reader

    def extract_text(self, image_path: str) -> str:
        reader = self._ensure_reader()
        results = reader.readtext(image_path, detail=0)
        return " ".join(results)
