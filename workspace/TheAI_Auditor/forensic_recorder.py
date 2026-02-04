import hashlib
import json
import time
from datetime import datetime, timezone

class ForensicRecorder:
    def __init__(self, model_id, version):
        self.model_metadata = {
            "model_id": model_id,
            "version": version,
            "hash": hashlib.sha256(f"{model_id}-{version}".encode()).hexdigest()
        }

    def record_inference(self, prompt, response, attention_summary, adversarial_check=None):
        """
        Captures a forensic snapshot of an inference cycle.
        """
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "model": self.model_metadata,
            "telemetry": {
                "input_hash": hashlib.sha256(prompt.encode()).hexdigest(),
                "output_hash": hashlib.sha256(response.encode()).hexdigest(),
                "attention_peek": attention_summary # Simplified for tutorial
            },
            "adversarial_baseline": adversarial_check or "untested",
            "forensic_id": hashlib.sha256(str(time.time()).encode()).hexdigest()
        }
        
        # In production, this would be written to an immutable, tamper-proof log.
        self._write_to_secure_log(entry)
        return entry['forensic_id']

    def _write_to_secure_log(self, data):
        with open("forensic_flight_recorder.log", "a") as f:
            f.write(json.dumps(data) + "\n")

if __name__ == "__main__":
    # Example Usage
    recorder = ForensicRecorder("AuditGPT-4", "v2.1.0-alpha")

    # Simulating an inference
    inference_id = recorder.record_inference(
        prompt="Explain the risk of algorithmic bias in mortgage approvals.",
        response="Algorithmic bias occurs when...",
        attention_summary={"bias_risk": 0.85, "mortgage_data": 0.12},
        adversarial_check="Passed: Fairness Baseline v1.2"
    )

    print(f"Forensic Snapshot captured: {inference_id}")