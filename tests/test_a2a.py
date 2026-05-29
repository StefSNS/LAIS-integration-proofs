"""A2A server smoke test — agent card, status, task delegation."""
import sys, json, time, os, urllib.request, urllib.error
from pathlib import Path
LAIS_ROOT = Path(os.environ.get("LAIS_ROOT", str(Path(__file__).resolve().parent.parent / "LAIS")))
sys.path.insert(0, str(LAIS_ROOT / "models" / "ai_engine" / "unified_layer"))

from protocol_layer import ProtocolLayer
from a2a_server import start_a2a_server, DEFAULT_PORT

proto = ProtocolLayer()
proto.register_local_agent("lais", "LAIS", "Main agent", ["orchestrate", "search"])
proto.register_local_agent("opencode", "OpenCode", "CLI agent", ["code", "shell"])
proto.register_local_agent("claude", "Claude Code", "Remote agent", ["code", "research"])

port = DEFAULT_PORT + 1
server = start_a2a_server(proto, port=port)
time.sleep(0.5)

def get(path):
    r = urllib.request.urlopen(f"http://127.0.0.1:{port}{path}")
    return json.loads(r.read())

def post(path, data):
    body = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(f"http://127.0.0.1:{port}{path}",
        data=body, headers={"Content-Type": "application/json"}, method="POST")
    return json.loads(urllib.request.urlopen(req).read())

card = get("/.well-known/agent-card")
print(f"Agent Card: {card['name']} v{card['version']} — {len(card['agents'])} agents")

status = get("/status")
print(f"Status: {status.get('a2a_agents', 0)} a2a agents, {status.get('a2a_tasks', 0)} tasks")

task = post("/a2a/tasks", {
    "from_agent": "test", "to_agent": "opencode",
    "task_type": "code_review", "payload": {"file": "test.py"}
})
print(f"Task: {task.get('task_id', '?')} ({task.get('status', '?')})")

tasks = get("/a2a/tasks")
print(f"Task list: {len(tasks['tasks'])} tasks")

server.stop()
print("[PASSED] A2A server test OK")
