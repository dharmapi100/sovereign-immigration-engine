class DocumentClassifier:
    def __init__(self):
        # mock local classification: hash-based document type detection
        self.signature_map = {
            "passport": "sig_01",
            "visa": "sig_02",
            "contract": "sig_03"
        }

    def classify(self, document_content: str) -> str:
        # returns document category for routing
        if "passport" in document_content.lower():
            return "passport"
        return "other"
