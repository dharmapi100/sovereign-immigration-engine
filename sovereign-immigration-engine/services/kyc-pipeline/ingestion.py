from cryptography.fernet import Fernet
import json
import sys
import os
sys.path.insert(0, '/Users/jtjtmoney/Projects/ksgc-sovereign-ai/sovereign-immigration-engine/services/kyc-pipeline/ocr')
from processor import OCRProcessor

sys.path.insert(0, '/Users/jtjtmoney/Projects/ksgc-sovereign-ai/sovereign-immigration-engine/services/kyc-pipeline/ocr/preprocessor')
from image_cleaner import ImageCleaner
sys.path.insert(0, '/Users/jtjtmoney/Projects/ksgc-sovereign-ai/sovereign-immigration-engine/services/doc-classifier')
from classifier import DocumentClassifier
sys.path.insert(0, '/Users/jtjtmoney/Projects/ksgc-sovereign-ai/sovereign-immigration-engine/services/visa-validation')
from validator import VisaValidator
sys.path.insert(0, '/Users/jtjtmoney/Projects/ksgc-sovereign-ai/sovereign-immigration-engine/services/fleet-orchestrator')
from orchestrator import FleetOrchestrator
sys.path.insert(0, '/Users/jtjtmoney/Projects/ksgc-sovereign-ai/sovereign-immigration-engine/services/policy-matching')
from matcher import PolicyMatcher
sys.path.insert(0, '/Users/jtjtmoney/Projects/ksgc-sovereign-ai/sovereign-immigration-engine/services/audit-ledger')
from ledger import AuditLedger
sys.path.insert(0, '/Users/jtjtmoney/Projects/ksgc-sovereign-ai/sovereign-immigration-engine/services/compliance-dashboard')
from logger import AuditLogger

class KYCExtractor:
    def __init__(self, key: bytes, visa_rules: dict, policy_rules: dict):
        self.cipher = Fernet(key)
        self.ocr = OCRProcessor()
        self.classifier = DocumentClassifier()
        self.cleaner = ImageCleaner()
        self.logger = AuditLogger()
        self.validator = VisaValidator(visa_rules)
        self.matcher = PolicyMatcher(policy_rules)
        self.orchestrator = FleetOrchestrator()
        self.ledger = AuditLedger()

    def extract_pii(self, encrypted_doc: bytes, image_path: str = None) -> dict:
        # PIPA compliant local PII extraction
        decrypted = self.cipher.decrypt(encrypted_doc)
        data = json.loads(decrypted.decode('utf-8'))
        if image_path:
            doc_type = self.classifier.predict(image_path)
            data['doc_type'] = doc_type
            if doc_type != 'contract':
                cleaned_path = self.cleaner.preprocess(image_path)
                data['ocr_text'] = self.ocr.extract_text(cleaned_path)
        
        validation = self.validator.validate_application(data)
        data['validation'] = validation
        
        if validation['valid']:
            data['policy_match'] = self.matcher.match_visa(data)
            self.orchestrator.distribute_task(data)
        
        self.logger.log_access(data.get("id"), "PII_EXTRACT")
        self.ledger.record_transaction(data.get("id"), "KYC_COMPLETE" if validation['valid'] else "KYC_PENDING")
        
        return data
