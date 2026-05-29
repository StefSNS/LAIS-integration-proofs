---
title: "Shared Memory for AI Agents — How We Made 5 Agents Talk to Each Other"
published: false
description: "Part 2 of the LAIS series: cross-agent shared memory with CoComm — store, retrieve, search, role registry, trust scoring, and knowledge graphs, all tested live."
tags: [ai, agents, python, architecture]
series: "Building LAIS"
---

## The Memory Problem

In Part 1, we solved cross-process agent handoff with the ACP bus — a JSON file that agents use to send tasks and receive results. But task messages are ephemeral. Once delivered and acknowledged, they're gone.

Real multi-agent systems need **persistent shared state**. Agent A discovers a useful fact and Agent B needs to read it later — possibly hours later, possibly while Agent A is offline.

This is the memory problem: how do you give multiple AI agents a shared, durable, searchable memory that survives restarts and works across processes?

Enter **CoComm** — a cross-agent communication and memory system we integrated from 16 modules into LAIS. Every module was tested live.

## What CoComm Provides

CoComm gives agents five memory capabilities:

| Feature | What It Does | Test Status |
|---------|-------------|-------------|
| **Shared Memory** | Store/retrieve/search key-value data | ✅ |
| **Cross-Agent Search** | Search all agents' memories by category | ✅ |
| **Role Registry** | Assign and query agent roles at runtime | ✅ |
| **Trust Scoring** | Track agent reliability over time | ✅ |
| **Knowledge Graph** | Build evolving agent relationship graphs | ✅ |

## Shared Memory: Store, Retrieve, Search

The core operation is simple: an agent stores a value under a key, optionally tagged with a category and priority. Any other agent can retrieve it.

```python
from cocomm_integration import get_cocomm_integration

c = get_cocomm_integration()

# Agent stores data
c.store_memory("opencode", "last_task", "ACP_HANDOFF_CONFIRMED", "handoff", "high")
c.store_memory("claude", "model_info", "openrouter/owl-alpha (1M ctx)", "config")

# Another agent retrieves everything from opencode
for m in c.retrieve_memory("opencode"):
    print(f"  [{m['category']}] {m['key']} = {m['value']}")

# Cross-agent search by category
for m in c.search_memory("config"):
    print(f"  [{m['agent']}] {m['key']}")
```

In our live test, we stored memories from both `opencode` and `claude` agents, then retrieved and searched across them. The bus now has 6 entries across 5 registered agents:

| Agent | Memory | Category |
|-------|--------|----------|
| test_agent | test_key | test |
| search_agent | search_key | search |
| ext_claude_code | task_result | results |
| opencode | last_task, bus_type | handoff, config |
| claude | model_info | config |

## Sessions: Grouping Work Across Agents

Sometimes you need to group multiple tasks into a single unit of work. CoComm's session system does this:

```python
sess = c.create_session("Live integration test", "opencode", ["handoff", "memory"])
# Returns a session with unique ID, agents can add tasks to it
# Later: c.update_task(task_id, "completed", result)
```

This is useful for tracking multi-step workflows: a research agent gathers data, a planning agent creates a strategy, a coding agent implements it — all under one session.

## Roles: Who Does What

In any multi-agent system, you need to know which agent is responsible for what. CoComm's role registry lets you assign roles at runtime:

```python
c.assign_role("opencode", "orchestrator")
c.assign_role("ext_claude_code", "executor")
c.assign_role("ext_claude_code", "specialist")

print(c.get_agent_role("opencode"))  # "orchestrator"
print(c.get_agent_role("ext_claude_code"))  # "executor"
```

Roles are queryable — any agent can ask "who is the executor?" and route tasks accordingly.

## Trust: Separating Reliable Agents from the Rest

This is the feature I want to highlight because it's rarely discussed in multi-agent demos, but it's critical for production.

If you run autonomous agents that make decisions and execute code, some will be more reliable than others. A buggy agent, a misconfigured provider, or a hallucination-prone model should be automatically deprioritized.

CoComm's trust system tracks every interaction and computes a trust score:

```python
# After each task, record the outcome
c.record_interaction("opencode", "ext_claude_code", "success", 1.0)
c.record_interaction("opencode", "ext_claude_code", "success", 0.95)

# Query reputation
rep = c.get_agent_reputation("ext_claude_code")
print(f"Trust score: {rep.trust_score:.2f}")
print(f"Total interactions: {rep.successful_tasks + rep.failed_tasks}")
print(f"Trusted?: {c.check_trust('ext_claude_code', 0.5)}")
```

Trust scores are based on ratio of successful to total tasks. You set a threshold — agents below it are routed around until they prove themselves again.

## Knowledge Graph: Agent Relationships

Finally, CoComm builds an evolving graph of agent relationships. Each agent is a node, and connections form as agents interact:

```python
nid = c.add_knowledge_node("opencode", {"fact": "handoff_proven", "method": "ACP_bus"})
state = c.get_graph_state("opencode")
```

The graph can be used to discover optimal communication paths — if Agent A trusts Agent B, and Agent B trusts Agent C, Agent A can safely delegate through B to C.

## What We Caught in Testing

CoComm was the integration that surfaced the most API drift. Of its 16 modules, two had mismatches between the wrapper and the actual implementation:

1. **TrustManager**: the wrapper called `get_reputation()` but the real method is `get_trust_score()`
2. **GraphEvolutionEngine**: the wrapper called `add_node(agent_id, knowledge_dict)` but the real method is `graph.add_node(agent_id, capabilities_list)`

Both were caught because we wrote live tests against the running modules rather than relying on documentation or static analysis.

## Next in This Series

- **Part 3**: Vector search without Docker — Qdrant in-memory mode with semantic ranking (coming soon)
- **Part 4**: A2A HTTP protocol — standards-compatible agent discovery and task delegation
- **Part 5**: What live testing taught us — the 3 API mismatches that documentation missed

---

*All test code is open source under Apache 2.0: [https://github.com/StefSNS/LAIS-integration-proofs](https://github.com/StefSNS/LAIS-integration-proofs)*
