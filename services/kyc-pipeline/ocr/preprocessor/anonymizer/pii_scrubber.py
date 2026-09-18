"""
PII Scrubber
============
Masks sensitive regions (e.g. passport number area) on scanned documents
before storage. OpenCV is imported lazily so the compliance core runs
without the CV stack installed.
"""


class PIIScrubber:
    @staticmethod
    def mask_pii(image_path: str) -> str:
        import cv2  # lazy: heavy dep

        img = cv2.imread(image_path)
        if img is None:
            raise FileNotFoundError(f"cannot read image: {image_path}")
        # Black-box the ROI (mock passport-number region) — PIPA minimization
        cv2.rectangle(img, (10, 10), (100, 50), (0, 0, 0), -1)
        scrubbed_path = image_path.replace(".png", "_scrubbed.png")
        cv2.imwrite(scrubbed_path, img)
        return scrubbed_path
