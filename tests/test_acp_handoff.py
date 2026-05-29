"""ACP Bus: cross-process agent-to-agent task dispatch + result return."""
import sys, json, time, uuid, os
from pathlib import Path
LAIS_ROOT = Path(os.environ.get("LAIS_ROOT", str(Path(__file__).resolve().parent.parent / "LAIS")))
sys.path.insert(0, str(LAIS_ROOT / "models" / "ai_engine" / "unified_layer"))
from agent_comms import get_comm_bus, ACPMessage

bus = get_comm_bus("lais_bus")
marker = uuid.uuid4().hex[:8]

# Phase 1: OpenCode sends task to Claude over ACP bus
task = ACPMessage("opencode", "claude", "task",
    {"prompt": f"run python -c \"print('HANDOFF_{marker}')\""})
task_id = bus.send(task)
print(f"[SEND] task={task_id[:12]} marker={marker}")

# Simulate cross-process sync: another process would call bus._sync() -> bus.receive()
time.sleep(0.5)
bus._sync()
received = bus.receive("claude", msg_type="task")
if received:
    msg = received[0]
    bus.ack(msg.id)
    result = ACPMessage("claude", "opencode", "result",
        {"result": f"HANDOFF_{marker}"}, reply_to=msg.id)
    bus.send(result)

# Phase 2: OpenCode picks up the result (cross-process sync)
time.sleep(0.5)
bus._sync()
for r in bus.receive("opencode", msg_type="result"):
    payload = r.payload if isinstance(r.payload, dict) else {"result": str(r.payload)}
    if marker in str(payload.get("result", "")):
        print(f"[RECV] result={payload['result']}")
        bus.ack(r.id)
        print("[PASS] ACP handoff round-trip confirmed")
