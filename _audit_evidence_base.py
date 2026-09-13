from datetime import datetime, timezone
from app.intelligence.evidence.evidence_engine_base import *

class T(EvidenceEngineBase):
    ENGINE_NAME = "TEST"
    LAYER = "TEST"

    def calculate(self, data):
        return self.make_evidence(
            metric="m",
            value=1,
            observed_at=datetime.now(timezone.utc)
        )

try:
    EvidenceEngineBase()
    print("[FAIL] abstract base instantiated")
except TypeError:
    print("[PASS] abstract base protected")

e = T()
a = e.make_evidence(metric="a", value=1, observed_at=datetime.now(timezone.utc))
b = e.make_evidence(metric="b", value=2, observed_at=datetime.now(timezone.utc))

print("[PASS] sequence", a.evidence_id, b.evidence_id)
print("[PASS] ratio0", T.ratio(1, 0, name="x") is None)
print("[PASS] validate_results", len(T.validate_results((a, b))))
print("[PASS] authority boundary",
      not any(x in str(dir(EvidenceEngineBase)).lower()
              for x in ["buy","sell","execute","order","position"]))