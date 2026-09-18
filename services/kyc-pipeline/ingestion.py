from cryptography.fernet import Fernet
import json
import os
import sys

# Resolve sibling services relative to this file — no hardcoded machine paths.
_SERVICES = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _add(*parts):
    p = os.path.join(_SERVICES, *parts)
    if p not in sys.path:
        sys.path.insert(0, p)


_add("kyc-pipeline", "ocr")
_add("kyc-pipeline", "ocr", "preprocessor")
_add("doc-classifier")
_add("visa-validation")
_add("fleet-orchestrator")
_add("policy-matching")
_add("audit-ledger")
_add("compliance-dashboard")
_add("pipa-dsl")

from processor import OCRProcessor
from image_cleaner import ImageCleaner
from classifier import DocumentClassifier
from validator import VisaValidator
from orchestrator import FleetOrchestrator
from matcher import PolicyMatcher
from ledger import AuditLedger
from evidence import EvidenceService
from kisa_client import KISATimestampClient
from compiler import Outcome, PIPACompiler
from logger import AuditLogger

from concurrent.futures import ThreadPoolExecutor


class KYCExtractor:
    def __init__(self, key: bytes, visa_rules: dict, policy_rules: dict,
                 kisa_client=None):
        self.cipher = Fernet(key)
        self.ocr = OCRProcessor()
        self.classifier = DocumentClassifier()
        self.cleaner = ImageCleaner()
        self.logger = AuditLogger()
        self.validator = VisaValidator(visa_rules)
        self.matcher = PolicyMatcher(policy_rules)
        self.orchestrator = FleetOrchestrator()
        self.ledger = AuditLedger()
        self.evidence = EvidenceService(
            self.ledger, kisa_client or KISATimestampClient(enabled=False)
        )
        self.pipa = PIPACompiler()
        self.executor = ThreadPoolExecutor(max_workers=4)

    def extract_pii(self, encrypted_doc: bytes, image_path: str = None) -> dict:
        decrypted = self.cipher.decrypt(encrypted_doc)
        data = json.loads(decrypted.decode("utf-8"))
        if image_path:
            doc_type = self.classifier.predict(image_path)
            data["doc_type"] = doc_type
            if doc_type != "contract":
                # parallel pre-processing/OCR
                future = self.executor.submit(self._process_image, image_path)
                data["ocr_text"] = future.result()

        # --- PIPA enforcement (Art.21 consent, Art.39 retention, Art.22 redact) --
        ctx = {
            "consent": data.get("consent", False),
            "output": data.get("ocr_text") or json.dumps(data, default=str),
            "stored_at": data.get("stored_at"),
            "retention_days": data.get("retention_days", 1825),
        }
        decisions = self.pipa.enforce_plan(ctx)
        data["pipa"] = [d.to_dict() for d in decisions]

        blocked = next((d for d in decisions if d.outcome == Outcome.BLOCK), None)
        if blocked:
            self.evidence.record(
                data.get("id", "unknown"), "PIPA_BLOCK", "pipeline",
                payload={"article": blocked.article}, purpose=blocked.reason,
                pii_detected=True,
            )
            data["validation"] = {"valid": False, "reason": blocked.reason,
                                  "article": blocked.article}
            return data

        redaction = next((d for d in decisions if d.outcome == Outcome.REDACT), None)
        if redaction:
            data["ocr_text"] = redaction.redactions.get("clean", data.get("ocr_text"))

        validation = self.validator.validate_application(data)
        data["validation"] = validation

        if validation["valid"]:
            data["policy_match"] = self.matcher.match_visa(data)
            self.orchestrator.distribute_task(data)

        self.logger.log_access(data.get("id"), "PII_EXTRACT")
        self.evidence.record(
            data.get("id", "unknown"),
            "KYC_COMPLETE" if validation["valid"] else "KYC_PENDING",
            "pipeline",
            payload={"doc_type": data.get("doc_type")},
            pii_detected=bool(redaction),
        )

        return data

    def _process_image(self, image_path):
        cleaned = self.cleaner.preprocess(image_path)
        return self.ocr.extract_text(cleaned)