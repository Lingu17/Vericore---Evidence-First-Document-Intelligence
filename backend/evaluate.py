"""Run the fixed policy suite against a running server; exit nonzero for failures."""
import argparse
import json
from pathlib import Path
import httpx

parser = argparse.ArgumentParser()
parser.add_argument("--url", default="http://127.0.0.1:8000")
parser.add_argument("--output", default="evaluation-result.json")
args = parser.parse_args()
with httpx.Client(base_url=args.url, timeout=120) as client:
    ids = []
    for version in (2025, 2026):
        path = Path(__file__).parent / "sample_documents" / f"Employee_Policy_{version}.txt"
        response = client.post("/api/documents/upload", files={"file": (path.name, path.read_bytes(), "text/plain")})
        response.raise_for_status()
        ids.append(response.json()["document_id"])
    response = client.post("/api/evaluations", json={"left_id": ids[0], "right_id": ids[1]})
    response.raise_for_status()
    run = response.json()
    Path(args.output).write_text(json.dumps(run, indent=2), encoding="utf-8")
    print(f"{run['passed']}/{run['total']} cases passed; results saved to {args.output}")
    raise SystemExit(0 if run["passed"] == run["total"] else 1)
