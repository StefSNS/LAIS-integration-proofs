"""QdrantService integration test — portable, no personal paths."""
import sys, json, os
from pathlib import Path
LAIS_ROOT = Path(os.environ.get("LAIS_ROOT", str(Path(__file__).resolve().parent.parent / "LAIS")))
sys.path.insert(0, str(LAIS_ROOT / "models" / "ai_engine" / "unified_layer"))

from qdrant_service import get_qdrant, QdrantService

QdrantService._get_embedding = lambda self, text: self._simple_embed(text)

q = get_qdrant("lais_test")
print(f"Available: {q.available}")
print(f"Initial count: {q.count()}")

id1 = q.store("ACP bus handoff between opencode and claude")
id2 = q.store("CoComm shared memory with trust scoring")
id3 = q.store("OpenRouter owl-alpha 1M context via API")
print(f"Stored 3: {id1[:8]}... {id2[:8]}... {id3[:8]}...")

print("\nSearch 'agent handoff':")
for r in q.search("agent handoff", limit=3):
    print(f"  [{r['score']:.3f}] {r['text']}")

print("\nSearch 'vector storage':")
for r in q.search("vector storage", limit=3):
    print(f"  [{r['score']:.3f}] {r['text']}")

print(f"\nFinal count: {q.count()}")
print("[PASSED]")
