from pydantic import BaseModel, Field, ValidationError
from datetime import datetime, timezone
from typing import List, Optional
import enum
import json

class RiskSeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ForensicEvidence(BaseModel):
    telemetry_hash: str
    timestamp: datetime
    verification_method: str = "AI_Tracer_v1"

class RiskReport(BaseModel):
    report_id: str
    model_version: str
    risk_score: float = Field(..., ge=0, le=1.0)
    severity: RiskSeverity
    violations: List[str]
    forensic_metadata: ForensicEvidence
    remediation_steps: Optional[str] = None

def test_valid_report():
    print("Testing valid report...")
    try:
        report = RiskReport(
            report_id="RPT-2026-X42",
            model_version="agent-titan-v2.1",
            risk_score=0.85,
            severity=RiskSeverity.HIGH,
            violations=["Bias_Threshold_Exceeded", "Data_Privacy_Leak_Detected"],
            forensic_metadata=ForensicEvidence(
                telemetry_hash="sha256:7f83b1c6e67657597579757975797579",
                timestamp=datetime.now(timezone.utc)
            ),
            remediation_steps="Rollback to v2.0 and initiate bias retuning."
        )
        print("Valid report created successfully.")
        # print(report.model_dump_json(indent=2))
    except ValidationError as e:
        print(f"Validation failed: {e}")
        exit(1)

def test_invalid_risk_score():
    print("Testing invalid risk score...")
    try:
        RiskReport(
            report_id="RPT-INV",
            model_version="v1",
            risk_score=1.5, # Should be <= 1.0
            severity=RiskSeverity.LOW,
            violations=[],
            forensic_metadata=ForensicEvidence(
                telemetry_hash="hash",
                timestamp=datetime.now(timezone.utc)
            )
        )
        print("Error: Invalid risk score was accepted.")
        exit(1)
    except ValidationError as e:
        print(f"Validation correctly caught error: {e}")

if __name__ == "__main__":
    test_valid_report()
    test_invalid_risk_score()
    print("All basic validation tests passed.")