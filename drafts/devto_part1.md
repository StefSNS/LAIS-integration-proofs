---
title: "Building a Multi-Agent System from 23 Open-Source Projects — What Worked, What Broke"
published: true
description: "Part 1 of a series on integrating 23 projects into a coordinated multi-agent architecture with live-tested integration proofs."
tags: [ai, agents, python, architecture]
series: "Building LAIS"
---

## The Single-Agent Ceiling

One LLM, one context window, one shot. That is the constraint every AI agent operates under today.

You can give an agent more tokens — 200K, 1M, even 2M context windows exist now — but that only pushes the ceiling higher, it does not remove it. A single agent still has to hold everything in one head: research, planning, coding, debugging, deployment. When context runs out, it forgets what it knew three turns ago.

The obvious solution is **multiple agents that hand off work to each other**. But multi-agent systems face their own problems:
- How do agents in different processes find each other?
- How do they share state without a shared database?
- How do you know which agent to trust with a critical task?

This series documents how we built **LAIS (Local AI System)** — a multi-agent architecture that solves these problems using 23 integrated open-source projects. Every integration was tested live against real running components, and the complete test suite is published.

In this part: the cross-process agent handoff that breaks through the single-agent ceiling.

## The Architecture

```
┌──────────────┐     ACP Bus (JSON)     ┌──────────────┐
│   OpenCode   │ ◄─────────────────────► │   Claude     │
│  (orchestrator)│   task → result        │  (executor)  │
└──────┬───────┘                         └──────┬───────┘
       │                                       │
       │          CoComm (Shared Memory)        │
       ├───────────────────────────────────────┤
       │  memory · sessions · roles · trust    │
       └───────────────────────────────────────┘
              │             │
       ┌──────┴──┐   ┌─────┴─────┐
       │  A2A    │   │  Qdrant   │
       │  HTTP   │   │  Vector   │
       │  API    │   │  Storage  │
       └─────────┘   └───────────┘
```

Four integrated systems, all tested live:

| System | Purpose | Test Status |
|--------|---------|-------------|
| **ACP Bus** | Cross-process agent tasking | ✅ Confirmed |
| **CoComm** | Shared memory, roles, trust | ✅ Confirmed |
| **Qdrant** | Local vector search | ✅ Confirmed |
| **A2A** | HTTP agent discovery & tasks | ✅ Confirmed |

## The ACP Bus: Cross-Process Agent Handoff

The core idea is simple: a JSON file on disk acts as the message bus. Agent A writes a task, Agent B reads it, processes it, writes the result back, and Agent A picks it up.

The message structure:

```python
@dataclass
class ACPMessage:
    id: str           # UUID
    sender: str       # who sent it
    recipient: str    # who should receive it
    msg_type: str     # "task", "result", "ack"
    payload: Any      # the actual data
    status: str       # "pending", "delivered", "failed"
    ttl: int          # time-to-live in seconds
    timestamp: float  # unix timestamp
```

The handoff flow has five steps:

1. **Send** — Agent A writes a task message to the bus
2. **Sync** — Agent B reloads the bus file from disk (cross-process sync)
3. **Receive** — Agent B picks up pending messages addressed to it
4. **Process** — Agent B executes the task (in our case, via OpenRouter)
5. **Result** — Agent B writes the result back to the bus

This was tested live with two real processes: OpenCode (the orchestrator) dispatched a task to Claude (the executor), which processed it via the OpenRouter API and returned the result. Full round-trip confirmed.

```python
bus = get_comm_bus("lais_bus")
marker = uuid.uuid4().hex[:8]

# OpenCode sends task
task = ACPMessage("opencode", "claude", "task",
    f"Run `python -c \"print('HANDOFF_OK_{marker}')\"`")
bus.send(task)

# Claude picks up, processes, returns result
bus._sync()
received = bus.receive("claude", msg_type="task")
# ... process via OpenRouter ...
result = ACPMessage("claude", "opencode", "result", output)
bus.send(result)

# OpenCode receives
bus._sync()
for r in bus.receive("opencode", msg_type="result"):
    print(f"Result: {r.payload}")
```

No message broker. No shared database. No server process. Just a JSON file and a polling loop.

## Why This Matters

Most multi-agent demos require cloud infrastructure: a hosted message queue, a vector database service, serverless functions. The ACP bus proves you can have reliable cross-process agent communication on a single machine with **zero infrastructure**.

This matters for three reasons:
1. **Privacy** — everything stays local
2. **Cost** — no cloud services to pay for
3. **Simplicity** — you can understand the entire system by reading one JSON file

## Next in This Series

- **Part 2**: Shared memory for agents — CoComm's store/retrieve/search, role registry, and trust scoring
- **Part 3**: Vector search without Docker — Qdrant in-memory mode with semantic ranking
- **Part 4**: A2A HTTP protocol — standards-compatible agent discovery and task delegation
- **Part 5**: What live testing taught us — the 3 API mismatches that documentation missed

---

*All test code is open source under Apache 2.0: [https://github.com/StefSNS/LAIS-integration-proofs](https://github.com/StefSNS/LAIS-integration-proofs)*
