"""VECTOR squire — TF-IDF semantic search over indexed files. Zero ML deps."""
from __future__ import annotations
import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .scan import FileRecord


@dataclass
class VectorMatch:
    file: str
    score: float
    snippet: str


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z_]\w*", text.lower())


def _compute_tf(tokens: list[str]) -> dict[str, float]:
    counts = Counter(tokens)
    total = max(len(tokens), 1)
    return {t: c / total for t, c in counts.items()}


class TFIDFCorpus:
    def __init__(self) -> None:
        self._docs: list[tuple[str, dict[str, float], str]] = []  # (path, tf, raw_text)
        self._df: Counter = Counter()
        self._built = False

    def add(self, path: str, text: str) -> None:
        tokens = _tokenize(text)
        tf = _compute_tf(tokens)
        self._docs.append((path, tf, text))
        for term in set(tokens):
            self._df[term] += 1
        self._built = False

    def _idf(self, term: str) -> float:
        n = len(self._docs)
        df = self._df.get(term, 0)
        if df == 0:
            return 0.0
        return math.log((n + 1) / (df + 1)) + 1.0

    def search(self, query: str, top_k: int = 10) -> list[VectorMatch]:
        qtokens = _tokenize(query)
        if not qtokens or not self._docs:
            return []
        scores: list[tuple[float, str, str]] = []
        for path, tf, raw in self._docs:
            score = sum(tf.get(t, 0.0) * self._idf(t) for t in qtokens)
            if score > 0:
                scores.append((score, path, raw))
        scores.sort(key=lambda x: -x[0])
        results = []
        for score, path, raw in scores[:top_k]:
            # Extract snippet around first query token hit
            snippet = _extract_snippet(raw, qtokens[0])
            results.append(VectorMatch(file=path, score=round(score, 4), snippet=snippet))
        return results


def _extract_snippet(text: str, term: str, window: int = 120) -> str:
    idx = text.lower().find(term.lower())
    if idx < 0:
        return text[:window].strip()
    start = max(0, idx - window // 2)
    end = min(len(text), idx + window // 2)
    snip = text[start:end].replace("\n", " ").strip()
    return f"...{snip}..." if start > 0 else snip


def build_corpus(records: Iterable[FileRecord]) -> TFIDFCorpus:
    corpus = TFIDFCorpus()
    for rec in records:
        if rec.is_binary:
            continue
        text = rec.read_text()
        if text:
            corpus.add(rec.rel, text)
    return corpus
