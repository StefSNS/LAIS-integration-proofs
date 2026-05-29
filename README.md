# LAIS — Multi-Agent Integration Proofs

Validated integration tests for the LAIS (Local AI System) multi-agent architecture. Each test was run live against real components and confirmed passing.

## Systems Tested

| System | File | Key Features | Status |
|--------|------|-------------|--------|
| **ACP Bus** | `tests/test_acp_handoff.py` | Cross-process task dispatch, result return, `_sync()`, ack | ✅ |
| **CoComm** | `tests/test_cocomm.py` | Shared memory, sessions, roles, trust scoring, knowledge graph | ✅ |
| **Qdrant** | `tests/test_qdrant.py` | Local vector storage, semantic search (no Docker) | ✅ |
| **A2A** | `tests/test_a2a.py` | Agent Card discovery, task delegation, status | ✅ |

## Architecture

```
┌──────────────┐     ACP Bus (JSON)     ┌──────────────┐
│   OpenCode   │ ◄─────────────────────► │   Claude     │
│  (orchestrator)│                       │  (executor)   │
└──────┬───────┘                        └──────┬───────┘
       │                                       │
       │          CoComm Shared Memory         │
       ├───────────────────────────────────────┤
       │  memory · sessions · roles · trust    │
       └───────────────────────────────────────┘
                      │
              ┌───────┴────────┐
              │  A2A HTTP API  │
              │  (discovery,   │
              │   tasks, stat) │
              └────────────────┘
```

## Running

```bash
export LAIS_ROOT=/path/to/LAIS
python tests/test_acp_handoff.py
python tests/test_cocomm.py
python tests/test_qdrant.py
python tests/test_a2a.py
```
