> **⚠️ ARCHIVED — 2026-06-10**
>
> This repository is **outdated and no longer actively maintained**.
>
> **What changed:** LAIS has evolved substantially. The current system includes CSI-Fusion (WiFi sensing security system), Hermes Agent (multi-platform CLI with MCP), LAIS Desktop (Electron app), and a 4-agent architecture with production deployments. None of these are reflected here.
>
> **Why archived:** The public code no longer represents the actual system. This repo is preserved as a **historical reference only**.
>
> **Status:** Read-only. No further updates, issues, or PRs will be accepted.
>
> ---

# LAIS — Multi-Agent Integration Proofs

Li ve-validated integration tests for the **LAIS  (Local AI System)** multi-agent architecture . Each test was executed against real running  components and confirmed passing end-to-end. 

## What These Tests Prove

### 1. ACP Bus � �� Real-Time Agent Handoff (`test_acp_handoff .py`)
- Two agents (OpenCode + Claude) commun icated across **separate processes** over a J SON-persisted message bus
- Task dispatched � �� agent receives via `_sync()` (cross-proces s bus polling) → processes → result retur ned → ack
- Proves: **live multi-agent task ing works without a centralized server**

###  2. CoComm — Cross-Agent Persistent State ( `test_cocomm.py`)
- **Shared Memory**: agents  store/retrieve key-value data visible to all 
- **Cross-Agent Search**: semantic category  filtering across all agent memories
- **Role  Registry**: agents assigned roles (orchestrat or, executor) at runtime
- **Trust Scoring**:  interaction history drives automated trust s cores
- **Knowledge Graph**: agent relationsh ip nodes added to evolving graph
- Proves: ** agents share durable state and build reputati on over time**

### 3. Qdrant — Local Vecto r Storage (`test_qdrant.py`)
- In-memory vect or database using `qdrant-client` (no Docker  required)
- Stored text vectors → semantic  search returns ranked results
- Proves: **LAI S can run local semantic search without exter nal infrastructure**

### 4. A2A — Agent-to -Agent HTTP Protocol (`test_a2a.py`)
- Agent  Card discovery endpoint (`.well-known/agent-c ard`) returns 9 registered agents
- Task dele gation via `POST /a2a/tasks` → task execute d locally
- Status endpoint exposes protocol  layer state + CoComm bridge
- Proves: **LAIS  exposes a standards-compatible A2A API for ex ternal tools**

## Results Summary

| Test |  System | What It Confirms | Details |
|------ |--------|-----------------|---------|
| `tes t_acp_handoff.py` | ACP Bus | Cross-process t ask round-trip | Task → sync → receive � � process → result → ack |
| `test_cocomm .py` | CoComm | Persistent shared state | Sto re, retrieve, search, session, roles, trust,  graph — 8 features |
| `test_qdrant.py` | Q drant | Local vector search | 3 vectors store d, semantic search with cosine similarity |
|  `test_a2a.py` | A2A Server | HTTP agent comm unication | Agent Card (9 agents), task deleg ation, status endpoint |

## Architecture

`` `
┌─────────────� ��┐     ACP Bus (JSON)     ┌────� ��─────────┐
│   OpenCo de   │ ◄─────────── ──────────► │   Claud e     │
│  (orchestrator)│   task → r esult        │  (executor)  │
└──� �───┬───────┘                          └──────┬─� ��─────┘
       │                                        │
       │           CoComm (Shared Memory)        │
        ├────────────── ─────────────── ──────────┤
       │   memory · sessions · roles · trust    │
        └───────────� �──────────────� �────────────┘
               │             │
       ┌─� �────┴──┐   ┌────� �┴─────┐
       │  A2A    │    │  Qdrant   │
       │  HTTP   │    │  Vector   │
       │  API    │   � ��  Storage  │
       └────── ───┘   └───────── ──┘
```

## Running

```bash
# Set LAIS _ROOT to point at your LAIS installation
expo rt LAIS_ROOT=/path/to/LAIS

# Run individuall y
python tests/test_acp_handoff.py
python tes ts/test_cocomm.py
python tests/test_qdrant.py 
python tests/test_a2a.py

# Or all at once
f or t in tests/test_*.py; do python "$t"; done 
```

## License

© 2026 LAIS Contributors � �� Apache 2.0. See [LICENSE](LICENSE).

## Ba ckground

These tests validate the integratio n of 23 researched projects into LAIS across  three implementation phases:
- **Phase 1**: A IOS scheduler, spec-kit, 22 new skills, OpenR outer routing, Karpathy principles
- **Phase  2**: Qdrant vector storage, CLI-Anything brid ge, Rowboat/Paseo daemons, Docker compose
- * *Phase 3**: Ruflo stream parsing, ACP bus pro tocol, Fabric patterns skill

All integration s were confirmed working before proceeding to  the next phase, with API mismatches fixed as  discovered (qdrant-client `search` → `quer y_points`, TrustManager `get_reputation` →  `get_trust_score`, relative imports converted  to absolute).
 