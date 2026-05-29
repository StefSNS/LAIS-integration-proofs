# LAIS — Multi-Agent Integration Proofs

Live-validated integration tests for the **LAIS (Local AI System)** multi-agent architecture. Each test was executed against real running components and confirmed passing end-to-end.

## What These Tests Prove

### 1. ACP Bus — Real-Time Agent Handoff (`test_acp_handoff.py`)
- Two agents (OpenCode + Claude) communicated across **separate processes** over a JSON-persisted message bus
- Task dispatched → agent receives via `_sync()` (cross-process bus polling) → processes → result returned → ack
- Proves: **live multi-agent tasking works without a centralized server**

### 2. CoComm — Cross-Agent Persistent State (`test_cocomm.py`)
- **Shared Memory**: agents store/retrieve key-value data visible to all
- **Cross-Agent Search**: semantic category filtering across all agent memories
- **Role Registry**: agents assigned roles (orchestrator, executor) at runtime
- **Trust Scoring**: interaction history drives automated trust scores
- **Knowledge Graph**: agent relationship nodes added to evolving graph
- Proves: **agents share durable state and build reputation over time**

### 3. Qdrant — Local Vector Storage (`test_qdrant.py`)
- In-memory vector database using `qdrant-client` (no Docker required)
- Stored text vectors → semantic search returns ranked results
- Proves: **LAIS can run local semantic search without external infrastructure**

### 4. A2A — Agent-to-Agent HTTP Protocol (`test_a2a.py`)
- Agent Card discovery endpoint (`.well-known/agent-card`) returns 9 registered agents
- Task delegation via `POST /a2a/tasks` → task executed locally
- Status endpoint exposes protocol layer state + CoComm bridge
- Proves: **LAIS exposes a standards-compatible A2A API for external tools**

## Results Summary

| Test | System | What It Confirms | Details |
|------|--------|-----------------|---------|
| `test_acp_handoff.py` | ACP Bus | Cross-process task round-trip | Task → sync → receive → process → result → ack |
| `test_cocomm.py` | CoComm | Persistent shared state | Store, retrieve, search, session, roles, trust, graph — 8 features |
| `test_qdrant.py` | Qdrant | Local vector search | 3 vectors stored, semantic search with cosine similarity |
| `test_a2a.py` | A2A Server | HTTP agent communication | Agent Card (9 agents), task delegation, status endpoint |

## Architecture

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

## Running

```bash
# Set LAIS_ROOT to point at your LAIS installation
export LAIS_ROOT=/path/to/LAIS

# Run individually
python tests/test_acp_handoff.py
python tests/test_cocomm.py
python tests/test_qdrant.py
python tests/test_a2a.py

# Or all at once
for t in tests/test_*.py; do python "$t"; done
```

## Background

These tests validate the integration of 23 researched projects into LAIS across three implementation phases:
- **Phase 1**: AIOS scheduler, spec-kit, 22 new skills, OpenRouter routing, Karpathy principles
- **Phase 2**: Qdrant vector storage, CLI-Anything bridge, Rowboat/Paseo daemons, Docker compose
- **Phase 3**: Ruflo stream parsing, ACP bus protocol, Fabric patterns skill

All integrations were confirmed working before proceeding to the next phase, with API mismatches fixed as discovered (qdrant-client `search` → `query_points`, TrustManager `get_reputation` → `get_trust_score`, relative imports converted to absolute).
