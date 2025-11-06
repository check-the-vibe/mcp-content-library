from __future__ import annotations
import json
import math
import random
import re
from collections import defaultdict
from typing import Dict, Any, List, Optional
from pathlib import Path
from schemas import STYLE_ENUM
from storage import INDEX_DIR, NODE_DIRS

STOP = {"the", "and", "a", "to", "of", "in", "it", "is", "that", "on", "for", "as", "with", "this", "be"}

INV_PATH = INDEX_DIR / "inverted.json"
LEN_PATH = INDEX_DIR / "doclens.json"
META_PATH = INDEX_DIR / "meta.json"


def _tokenize(text: str) -> List[str]:
    if not text:
        return []
    lowered = text.lower()
    tokens = re.findall(r"[a-z0-9]+", lowered)
    return [t for t in tokens if t not in STOP]


def index_document(doc_id: str, node: Dict[str, Any]):
    inv = json.loads(INV_PATH.read_text()) if INV_PATH.exists() else {}
    lens = json.loads(LEN_PATH.read_text()) if LEN_PATH.exists() else {}
    meta = json.loads(META_PATH.read_text()) if META_PATH.exists() else {}

    text = (node.get("title") or "") + "\n" + (node.get("content") or "")
    toks = _tokenize(text)
    tf: Dict[str, int] = defaultdict(int)
    for t in toks:
        tf[t] += 1
    for t, cnt in tf.items():
        inv.setdefault(t, {})[doc_id] = cnt
    lens[doc_id] = len(toks) or 1
    meta[doc_id] = {
        "date": node.get("date", ""),
        "title": node.get("title"),
        "style": node.get("style", []),
        "tags": node.get("tags", []),
        "authors": node.get("authors", []),
    }
    INV_PATH.write_text(json.dumps(inv))
    LEN_PATH.write_text(json.dumps(lens))
    META_PATH.write_text(json.dumps(meta))


def rebuild_index():
    inv: Dict[str, Dict[str, int]] = {}
    lens: Dict[str, int] = {}
    meta: Dict[str, Dict[str, Any]] = {}
    for p in NODE_DIRS["content"].glob("*.json"):
        node = json.loads(p.read_text())
        doc_id = node["id"]
        text = (node.get("title") or "") + "\n" + (node.get("content") or "")
        toks = _tokenize(text)
        tf: Dict[str, int] = defaultdict(int)
        for t in toks:
            tf[t] += 1
        for t, cnt in tf.items():
            inv.setdefault(t, {})[doc_id] = cnt
        lens[doc_id] = len(toks) or 1
        meta[doc_id] = {
            "date": node.get("date", ""),
            "title": node.get("title"),
            "style": node.get("style", []),
            "tags": node.get("tags", []),
            "authors": node.get("authors", []),
        }
    INV_PATH.write_text(json.dumps(inv))
    LEN_PATH.write_text(json.dumps(lens))
    META_PATH.write_text(json.dumps(meta))


def _idf(inv: Dict[str, Dict[str, int]], token: str) -> float:
    doc_ids = {doc for postings in inv.values() for doc in postings}
    total_docs = max(1, len(doc_ids))
    df = len(inv.get(token, {}))
    return math.log((1 + total_docs) / (1 + df)) + 1.0


def _score(inv: Dict[str, Dict[str, int]], lens: Dict[str, int], q_toks: List[str]) -> Dict[str, float]:
    scores = defaultdict(float)
    idf_cache = {t: _idf(inv, t) for t in set(q_toks)}
    for t in q_toks:
        postings = inv.get(t, {})
        for doc, tf in postings.items():
            scores[doc] += (tf * idf_cache[t]) / math.sqrt(lens.get(doc, 1))
    return scores


def _load_indexes():
    inv = json.loads(INV_PATH.read_text()) if INV_PATH.exists() else {}
    lens = json.loads(LEN_PATH.read_text()) if LEN_PATH.exists() else {}
    meta = json.loads(META_PATH.read_text()) if META_PATH.exists() else {}
    return inv, lens, meta


def search(
    query: Optional[str],
    filters: Dict[str, Any],
    sort: str = "relevance",
    page: int = 1,
    page_size: int = 10,
    seed: Optional[int] = None,
) -> Dict[str, Any]:
    inv, lens, meta = _load_indexes()
    q_toks = _tokenize(query or "")
    docset = set(meta.keys())

    if filters.get("style"):
        styles = [s for s in filters["style"] if s in STYLE_ENUM]
        docset &= {doc for doc, info in meta.items() if any(s in info.get("style", []) for s in styles)}

    if filters.get("tag"):
        tags = set(filters["tag"])
        docset &= {doc for doc, info in meta.items() if any(t in info.get("tags", []) for t in tags)}

    if filters.get("author"):
        authors = set(filters["author"])
        docset &= {doc for doc, info in meta.items() if any(a in info.get("authors", []) for a in authors)}

    if filters.get("title"):
        substr = filters["title"].lower()
        docset &= {doc for doc, info in meta.items() if (info.get("title") or "").lower().find(substr) >= 0}

    if filters.get("content"):
        content_dir = NODE_DIRS["content"]
        substr = filters["content"].lower()
        keep = set()
        for doc in list(docset):
            path = content_dir / f"{doc}.json"
            if path.exists():
                text = json.loads(path.read_text()).get("content", "").lower()
                if substr in text:
                    keep.add(doc)
        docset &= keep

    if filters.get("relates"):
        rels = set(filters["relates"])
        rel_path = NODE_DIRS["content"].parent.parent / "edges" / "relates.jsonl"
        keep = set()
        if rel_path.exists():
            for line in rel_path.read_text().splitlines():
                try:
                    obj = json.loads(line)
                except Exception:
                    continue
                if obj.get("src") in docset or obj.get("dst") in docset:
                    if obj.get("src") in rels or obj.get("dst") in rels:
                        keep.add(obj.get("src"))
                        keep.add(obj.get("dst"))
        docset &= keep

    candidates = list(docset)

    if sort == "relevance":
        scores = _score(inv, lens, q_toks) if q_toks else {doc: 0.0 for doc in candidates}
        candidates.sort(key=lambda doc: scores.get(doc, 0.0), reverse=True)
    elif sort == "date":
        candidates.sort(key=lambda doc: (meta.get(doc, {}).get("date") or ""), reverse=True)
    elif sort == "random":
        rnd = random.Random(seed)
        rnd.shuffle(candidates)

    total = len(candidates)
    start = max(0, (page - 1) * page_size)
    page_items = candidates[start : start + page_size]

    items: List[Dict[str, Any]] = []
    for doc in page_items:
        path = NODE_DIRS["content"] / f"{doc}.json"
        if path.exists():
            items.append(json.loads(path.read_text()))
    return {"items": items, "total": total, "page": page, "page_size": page_size}
