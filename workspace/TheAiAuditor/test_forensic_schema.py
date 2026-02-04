from pydantic import BaseModel, Field, ValidationError, HttpUrl
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
import enum
import json

class RiskSeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ComplianceScope(str, enum.Enum):
    EU_AI_ACT_ART_12 = "EU_AI_Act_Art_12_Logging"
    EU_AI_ACT_ART_13 = "EU_AI_Act_Art_13_Transparency"
    ISO_42001 = "ISO_42001_AI_Management"
    NIST_AI_RMF = "NIST_AI_RMF"

class ForensicEvidence(BaseModel):
    telemetry_hash: str = Field(..., description="SHA-256 hash of the full telemetry trace")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    verification_method: str = "AI_Tracer_v1"
    state_reconstruction_uri: Optional[HttpUrl] = Field(None, description="Secure URI to replay the inference state")
    adversarial_baseline_id: Optional[str] = Field(None, description="Reference to the Red Team baseline tested against")

class RiskReport(BaseModel):
    report_id: str = Field(..., pattern=r"^RPT-202[5-9]-[A-Z0-9]+$")
    model_version: str
    risk_score: float = Field(..., ge=0, le=1.0)
    severity: RiskSeverity
    compliance_articles: List[ComplianceScope] = Field(default_factory=list)
    violations: List[str]
    forensic_metadata: ForensicEvidence
    remediation_steps: Optional[str] = None
    chain_of_custody_signature: Optional[str] = Field(None, description="Digital signature for record integrity")

def test_forensic_validation():
    print("Testing 2026 Forensic Regulatory Validation...")
    try:
        # Valid forensic report
        report = RiskReport(
            report_id="RPT-2026-X42",
            model_version="agent-titan-v2.1",
            risk_score=0.85,
            severity=RiskSeverity.HIGH,
            compliance_articles=[ComplianceScope.EU_AI_ACT_ART_12, ComplianceScope.ISO_42001],
            violations=["Bias_Threshold_Exceeded"],
            forensic_metadata=ForensicEvidence(
                telemetry_hash="sha256:7f83b1c6e67657597579757975797579",
                state_reconstruction_uri="https://forensics.internal.enterprise/traces/X42",
                adversarial_baseline_id="RED-TEAM-2026-Q1-BIAS"
            ),
            remediation_steps="Initiating automated rollback.",
            chain_of_custody_signature="sig:ed25519:base64..."
        )
        print("✅ Forensic report validated successfully.")
        
        # Test pattern validation for report_id
        try:
            RiskReport(
                report_id="INVALID-ID",
                model_version="v1",
                risk_score=0.1,
                severity=RiskSeverity.LOW,
                violations=[],
                forensic_metadata=ForensicEvidence(telemetry_hash="hash")
            )
            print("❌ Failed: Accepted invalid report_id pattern")
        except ValidationError:
            print("✅ Correctly rejected invalid report_id pattern")

    except ValidationError as e:
        print(f"❌ Validation failed: {e}")
        exit(1)

if __name__ == "__main__":
    test_forensic_validation()