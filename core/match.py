"""Matchmaking bez AI: BM25 + prosty polski stemming + słownik pojęć + premia za pokrycie słów.

Wynik jest wyjaśnialny: zwracamy wspólne słowa i wspólne tematy („dlaczego pasuje”)."""
import math
import re
from collections import Counter
from dataclasses import dataclass, field

from data.slownik import STOPWORDS, TOPIC_AREA, TOPICS

_FOLD = str.maketrans("ąćęłńóśźż", "acelnoszz")
_WORD = re.compile(r"[a-ząćęłńóśźż]+")
_SUFFIXES = sorted([
    "owania", "owanie", "ościami", "ości", "ość", "ami", "ach", "ego", "emu", "ych", "ymi", "imi", "owi",
    "owa", "owe", "owy", "iem", "ów", "om", "em", "ie", "ia", "iu", "ka", "ko", "a", "e", "i", "o", "u", "y",
], key=len, reverse=True)
_SUFFIXES = [s.translate(_FOLD) for s in _SUFFIXES]
_STOP = {w.translate(_FOLD) for w in STOPWORDS}

K1, B = 1.5, 0.75
SATURATION = 8.0  # bm25 / (bm25 + SATURATION) → 0..1
W_BM25 = 0.5


def stem(word):
    """Polski stemming na skróty: zdejmij jedną końcówkę, utnij do 6 znaków.
    ponytail: heurystyka; jeśli trafność spadnie – podmienić na pystempel/Morfeusz."""
    for s in _SUFFIXES:
        if word.endswith(s) and len(word) - len(s) >= 4:
            word = word[: -len(s)]
            break
    return word[:6]


def words(text):
    """Pary (oryginał, rdzeń) dla słów znaczących."""
    out = []
    for w in _WORD.findall(text.lower()):
        f = w.translate(_FOLD)
        if len(f) >= 3 and f not in _STOP:
            out.append((w, stem(f)))
    return out


_STEM_TOPICS = {}
for _key, (_label, _words) in TOPICS.items():
    for _w in _words:
        _STEM_TOPICS.setdefault(stem(_w.translate(_FOLD)), set()).add(_key)


def terms(text):
    """Rdzenie + tokeny tematów (#temat) – jedna lista do indeksu."""
    stems = [s for _, s in words(text)]
    topic_tokens = [f"#{t}" for s in stems for t in _STEM_TOPICS.get(s, ())]
    return stems + topic_tokens


def topics_of(text):
    return Counter(t[1:] for t in terms(text) if t.startswith("#"))


def detect_area(text):
    """Najczęstszy obszar wynikający z tematów; None, gdy brak sygnału."""
    votes = Counter()
    for topic, n in topics_of(text).items():
        if topic in TOPIC_AREA:
            votes[TOPIC_AREA[topic]] += n
    return votes.most_common(1)[0][0] if votes else None


def innovation_text(d):
    """Tekst innowacji do indeksu; tytuł liczy się podwójnie."""
    return " ".join([d["title"], d["title"], d["summary"], d["description"], d["keywords"], d["audience"]])


def label(score):
    if score >= 0.6:
        return "Bardzo pasuje"
    if score >= 0.45:
        return "Pasuje"
    if score >= 0.35:
        return "Może pasować"
    return "Słabe dopasowanie"


@dataclass
class Result:
    doc_id: int
    score: float
    words: list = field(default_factory=list)   # wspólne słowa (w formie z opisu użytkownika)
    topics: list = field(default_factory=list)  # wspólne tematy (czytelne etykiety)

    @property
    def label(self):
        return label(self.score)

    @property
    def percent(self):
        return round(self.score * 100)


class Index:
    def __init__(self, docs):
        """docs: lista (id, tekst)."""
        self.ids = [d for d, _ in docs]
        self.tfs = [Counter(terms(t)) for _, t in docs]
        self.lens = [sum(tf.values()) for tf in self.tfs]
        self.avgdl = (sum(self.lens) / len(self.lens)) if self.lens else 1
        self.df = Counter(t for tf in self.tfs for t in tf)
        self.n = len(docs)

    def _idf(self, t):
        df = self.df.get(t, 0)
        return math.log(1 + (self.n - df + 0.5) / (df + 0.5))

    def search(self, query, k=5, exclude=()):
        q_words = words(query)
        q_terms = set(terms(query))
        if not q_terms or not self.n:
            return []
        original = {}
        for w, s in q_words:
            original.setdefault(s, w)
        q_stems = {t for t in q_terms if not t.startswith("#")}
        results = []
        for i, tf in enumerate(self.tfs):
            if self.ids[i] in exclude:
                continue
            bm, word_hits = 0.0, 0
            for t in q_terms:
                f = tf.get(t, 0)
                if f:
                    word_hits += t in q_stems
                    bm += self._idf(t) * f * (K1 + 1) / (f + K1 * (1 - B + B * self.lens[i] / self.avgdl))
            if not bm:
                continue
            # Pokrycie liczymy tylko z konkretnych słów: same wspólne tematy nie dają „dobrego” dopasowania.
            coverage = word_hits / len(q_stems) if q_stems else 0
            score = W_BM25 * bm / (bm + SATURATION) + (1 - W_BM25) * coverage
            shared_words = [original[s] for s in original if s in tf]
            shared_topics = [TOPICS[t[1:]][0] for t in sorted(q_terms) if t.startswith("#") and t in tf]
            results.append(Result(self.ids[i], round(min(score, 1.0), 3), shared_words[:8], shared_topics))
        results.sort(key=lambda r: r.score, reverse=True)
        return results[:k]
