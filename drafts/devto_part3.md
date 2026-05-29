---
title: "Vector Search Without Docker — Running Semantic Search In-Process"
published: false
description: "Part 3 of the LAIS series: Qdrant vector search in local mode, no Docker required. Embedding pipelines, semantic search, and the API drift we caught in testing."
tags: [ai, python, architecture, semsearch]
series: "Building LAIS"
---

## The Vector Search Problem

Semantic search is essential for AI agents — finding relevant information by meaning rather than keyword matching. But most solutions require infrastructure: a running Qdrant server, Pinecone API keys, or a self-hosted Milvus cluster.

What if you want vector search in a local-first, single-machine system?

## Qdrant in Local Mode

Qdrant has a **local mode** that runs entirely in-process using the same `qdrant-client` library. No server. No Docker. No cloud.

```python
from qdrant_client import QdrantClient
from qdrant_client.http import models

client = QdrantClient(path="/path/to/storage")
client.create_collection(
    collection_name="lais_memory",
    vectors_config=models.VectorParams(
        size=384,
        distance=models.Distance.COSINE
    ),
)
```

The `path` parameter points to a directory on disk. Qdrant handles persistence automatically. The API is identical whether you connect to a remote server or run locally.

## Our Integration

We built a `QdrantService` wrapper that adds embedding and search on top of the local client:

```python
from qdrant_service import get_qdrant

q = get_qdrant("lais_memory")

# Store text with embedding
id1 = q.store("ACP bus handoff between opencode and claude")
id2 = q.store("CoComm shared memory with trust scoring")
id3 = q.store("OpenRouter owl-alpha 1M context via API")

# Semantic search
results = q.search("agent handoff", limit=3)
for r in results:
    print(f"  [{r['score']:.3f}] {r['text']}")
```

The embedding pipeline has two modes:

1. **sentence-transformers** (`all-MiniLM-L6-v2`) — higher quality, downloads ~80MB model on first use
2. **Simple hash-based fallback** — zero dependencies, works instantly, reasonable for testing

## Live Test Results

We stored 3 vectors and ran semantic searches:

```
Search 'agent handoff':
  [0.781] OpenRouter owl-alpha 1M context via API
  [0.579] ACP bus handoff between opencode and claude
  [0.536] CoComm shared memory with trust scoring

Search 'vector storage':
  [0.705] CoComm shared memory with trust scoring
  [0.664] OpenRouter owl-alpha 1M context via API
  [0.548] ACP bus handoff between opencode and claude
```

The scores show cosine similarity — 1.0 means identical direction, 0.0 means orthogonal. The results are ranked correctly even with the simple embedding fallback.

## The API Drift We Caught

Between the time the integration code was written and when we ran the live test, `qdrant-client` had updated its API:

- **Old**: `client.search(collection_name=..., query_vector=...)`
- **New**: `client.query_points(collection_name=..., query=...)`

The return type also changed — `search()` returned a list of `ScoredPoint` directly, while `query_points()` returns a `QueryResponse` with a `.points` attribute.

This only surfaced when we ran the actual test. Documentation hadn't caught up, and static analysis couldn't detect it because the API change was at the network boundary.

## Why Local Vector Search Matters

Running vector search locally means:

1. **No infrastructure costs** — Qdrant local mode is free
2. **Privacy** — embeddings never leave your machine
3. **Offline capability** — the system works without internet
4. **Simplicity** — one pip package, no Docker Compose, no config

For a local-first multi-agent system, this is the difference between "it works on my laptop" and "it requires a cloud account."

## Next in This Series

- **Part 4**: A2A HTTP protocol — standards-compatible agent discovery and task delegation
- **Part 5**: What live testing taught us — the 3 API mismatches that documentation missed

---

*All test code is open source under Apache 2.0: [https://github.com/StefSNS/LAIS-integration-proofs](https://github.com/StefSNS/LAIS-integration-proofs)*
