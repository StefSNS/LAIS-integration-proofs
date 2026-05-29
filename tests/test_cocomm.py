"""CoComm shared memory, sessions, roles, trust, knowledge graph — portable."""
import sys, json, os
from pathlib import Path
LAIS_ROOT = Path(os.environ.get("LAIS_ROOT", str(Path(__file__).resolve().parent.parent / "LAIS")))
sys.path.insert(0, str(LAIS_ROOT / "models" / "ai_engine" / "unified_layer"))

from cocomm_integration import get_cocomm_integration

c = get_cocomm_integration()

print("=== CoComm Status ===")
print(json.dumps(c.get_status(), indent=2, default=str))

print("\n=== Storing Memory ===")
c.store_memory("opencode", "last_task", "ACP_HANDOFF_CONFIRMED", "handoff", "high")
c.store_memory("claude", "model_info", "openrouter/owl-alpha (1M ctx)", "config", "high")
c.store_memory("opencode", "bus_type", "ACP JSON bus with _sync()", "config")
print("OK")

print("\n=== Cross-Agent Retrieve ===")
for m in c.retrieve_memory("opencode"):
    print(f"  [{m['category']}] {m['key']} = {m['value']}")

print("\n=== Cross-Agent Search (category=config) ===")
for m in c.search_memory("config", limit=10):
    print(f"  [{m['agent']}] {m['key']}")

print("\n=== Cross-Agent Session ===")
sess = c.create_session("Live integration test", "opencode", ["handoff", "memory"])
print(f"  Session: {sess.get('session_id', 'ok')}")

print("\n=== Role Registry ===")
c.assign_role("opencode", "orchestrator")
c.assign_role("ext_claude_code", "executor")
print(f"  opencode role: {c.get_agent_role('opencode')}")
print(f"  claude role: {c.get_agent_role('ext_claude_code')}")

print("\n=== Trust System ===")
c.record_interaction("opencode", "ext_claude_code", "success", 1.0)
c.record_interaction("opencode", "ext_claude_code", "success", 0.95)
rep = c.get_agent_reputation("ext_claude_code")
if rep:
    total = rep.successful_tasks + rep.failed_tasks
    print(f"  trust score: {rep.trust_score:.2f} ({total} interactions)")
print(f"  trusted: {c.check_trust('ext_claude_code', 0.5)}")

print("\n=== Knowledge Graph ===")
nid = c.add_knowledge_node("opencode", {"fact": "handoff_proven", "method": "ACP_bus"})
print(f"  node added: {nid}")
state = c.get_graph_state("opencode")
print(f"  graph state: {state}")

print("\n[PASSED] CoComm test OK")
