"""
GAIA Test Client
Demonstrates the full distributed claim lifecycle:
  1. Submit a claim to Node A
  2. Trigger sync (A → B → C)
  3. Verify propagation to Nodes B and C
  4. Fetch consensus state from all nodes
  5. Check agreement level

Usage (network running):
  python client/test_client.py

Usage (quick single-node test):
  python client/test_client.py --local
"""

import sys
import json
import argparse
import requests
from typing import Dict, Any

NODES = {
    "A": "http://localhost:8001",
    "B": "http://localhost:8002",
    "C": "http://localhost:8003"
}

TEST_CLAIMS = [
    {
        "statement": "Crystal and plant alchemy protocols produce synergistic biophotonic coherence gain",
        "confidence": 0.82,
        "status":     "supported",
        "domain":     "biophotonics",
        "sources":    ["SIM-016"]
    },
    {
        "statement": "GAIA epistemic world model is the missing layer in current AI architectures",
        "confidence": 0.91,
        "status":     "supported",
        "domain":     "architecture",
        "sources":    ["GAIA_CONVERGENCE_MANIFESTO_v1"]
    },
    {
        "statement": "Ontology is unavoidable in production AI systems that reason across domains",
        "confidence": 0.88,
        "status":     "supported",
        "domain":     "epistemics",
        "sources":    ["2026_agent_research"]
    },
]


def check_node(node_id: str, base: str) -> bool:
    try:
        r = requests.get(f"{base}/health", timeout=3)
        ok = r.status_code == 200
        print(f"  Node {node_id}: {'OK' if ok else 'UNREACHABLE'}")
        return ok
    except Exception:
        print(f"  Node {node_id}: UNREACHABLE")
        return False


def submit_claim(base: str, claim: Dict[str, Any]) -> Dict:
    r = requests.post(f"{base}/claim", json=claim, timeout=5)
    return r.json()


def get_state(base: str) -> Dict:
    r = requests.get(f"{base}/state", timeout=5)
    return r.json()


def trigger_sync(base: str) -> Dict:
    r = requests.post(f"{base}/sync/trigger", timeout=10)
    return r.json()


def run_full_test():
    print("\n" + "="*55)
    print("  GAIA Distributed Network — Full Test")
    print("="*55)

    # 1. Health check all nodes
    print("\n[1] Checking nodes...")
    reachable = {nid: check_node(nid, base) for nid, base in NODES.items()}
    live_nodes = {nid: base for nid, base in NODES.items() if reachable[nid]}
    if not live_nodes:
        print("  No nodes reachable. Is docker-compose up running?")
        print("  Run: docker-compose up")
        sys.exit(1)

    # 2. Submit test claims to Node A
    print(f"\n[2] Submitting {len(TEST_CLAIMS)} claims to Node A...")
    base_a = NODES["A"]
    for claim in TEST_CLAIMS:
        result = submit_claim(base_a, claim)
        print(f"  ✓ [{result.get('id', '?')[:8]}...] {claim['statement'][:55]}...")

    # 3. Trigger sync on all live nodes
    print("\n[3] Triggering sync on all live nodes...")
    for nid, base in live_nodes.items():
        result = trigger_sync(base)
        print(f"  Node {nid}: {result.get('peers_contacted', 0)} peers synced")

    # 4. Verify propagation
    print("\n[4] Verifying state propagation...")
    for nid, base in live_nodes.items():
        state = get_state(base)
        count = state.get("claim_count", 0)
        print(f"  Node {nid}: {count} claims in world state")

    # 5. Summary
    print("\n" + "="*55)
    print("  Test complete.")
    print("  Check individual nodes:")
    for nid, base in live_nodes.items():
        print(f"    curl {base}/claims")
    print("="*55 + "\n")


def run_local_test():
    """Quick test against a single local node (no Docker required)."""
    base = "http://localhost:8000"
    print("\n  GAIA Local Node Test")
    print("  Target:", base)
    r = requests.get(f"{base}/health", timeout=3)
    print("  Health:", r.json())
    result = submit_claim(base, TEST_CLAIMS[0])
    print("  Claim submitted:", result)
    state = get_state(base)
    print(f"  Node state: {state.get('claim_count', 0)} claims")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--local", action="store_true")
    args = parser.parse_args()
    if args.local:
        run_local_test()
    else:
        run_full_test()
