#!/usr/bin/env python3
"""EDA Apps-ACOS: data sumber (reviews_clean) + hasil (appsid_quad_*.tsv) + replikasi cakupan span.

Stdlib murni. Deterministik. Tidak mengunduh apa pun, tidak menjalankan notebook.

Keluaran (semua di reports/044_data/):
  eda_summary.json              ringkasan seluruh metrik
  split_stats.csv               statistik per split (hasil)
  category_counts.csv           13 kategori x sentimen
  sentiment_counts.csv          distribusi sentimen
  span_length_dist.csv          distribusi panjang span aspek/opini
  top_aspect_terms.csv          frekuensi istilah aspek (untuk wordcloud)
  top_opinion_terms.csv         frekuensi istilah opini (wordcloud)
  opinion_terms_by_sentiment.csv
  review_stats.csv              statistik per aplikasi (sumber)
  coverage_replication.csv      replikasi cakupan span: 4 definisi tokenisasi

Jalankan: python3 scripts/eda_044_appsid.py
"""
from __future__ import annotations

import collections
import csv
import json
import os
import re
import statistics

csv.field_size_limit(2 ** 31 - 1)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "ACOS-IndoBERT", "data", "Apps-ACOS", "processed")
QUAD = os.path.join(ROOT, "ACOS-IndoBERT", "data", "Apps-ACOS")
OUT = os.path.join(ROOT, "reports", "044_data")
os.makedirs(OUT, exist_ok=True)

TOK = re.compile(r"\w+|[^\w\s]")
SENT_CODE = {"0": "negative", "1": "neutral", "2": "positive"}
SPLIT = ("[NULL]", "", "-1")


def toks_punct(s: str) -> list[str]:
    return TOK.findall(s.lower())


def toks_split(s: str) -> list[str]:
    return s.lower().split()


def subseq_found(sub: str, seq: list[str], mode: str) -> bool:
    toks = toks_split(sub) if mode == "split" else toks_punct(sub)
    n = len(toks)
    if n == 0:
        return False
    for i in range(len(seq) - n + 1):
        if seq[i:i + n] == toks:
            return True
    return False


def pct(a: int, b: int) -> float:
    return round(100.0 * a / b, 2) if b else 0.0


def quantiles(vals: list[int]) -> dict:
    if not vals:
        return {}
    s = sorted(vals)
    q = lambda p: s[min(len(s) - 1, int(p * len(s)))]
    return {"n": len(s), "min": s[0], "p25": q(.25), "median": statistics.median(s),
            "mean": round(statistics.mean(s), 2), "p75": q(.75), "p95": q(.95), "max": s[-1]}


# ============================================================== 1. DATA SUMBER
src = {
    "reviews": 0, "uniq_ids": 0,
    "platform": collections.Counter(), "apps": collections.Counter(),
    "years": collections.Counter(), "ratings": collections.Counter(),
    "polarity": collections.Counter(), "n_words": [], "emoji": [],
    "helpful_pos": 0, "dup_text": 0,
}
texts = collections.Counter()
rows_clean = {}
with open(os.path.join(SRC, "reviews_clean.csv"), encoding="utf-8") as fh:
    for r in csv.DictReader(fh):
        src["reviews"] += 1
        rows_clean[r["review_id"]] = (r["review_text"], r["text_norm"])
        src["platform"][r["platform"]] += 1
        src["apps"][r["app_slug"]] += 1
        src["years"][r["review_year"]] += 1
        src["ratings"][r["rating"]] += 1
        src["polarity"][r["polarity_rating"]] += 1
        try:
            src["n_words"].append(int(r["n_words"]))
        except ValueError:
            pass
        try:
            src["emoji"].append(int(r["emoji_count"]))
        except ValueError:
            pass
        if r["helpful"] not in ("", "0"):
            src["helpful_pos"] += 1
        texts[r["text_norm"].strip().lower()] += 1
src["uniq_ids"] = len(rows_clean)
src["dup_text"] = sum(c - 1 for c in texts.values() if c > 1)

app_stats = collections.Counter()
app_rating = collections.defaultdict(list)
with open(os.path.join(SRC, "reviews_labeled.csv"), encoding="utf-8") as fh:
    for r in csv.DictReader(fh):
        app_stats[r["app_slug"]] += 1
        try:
            app_rating[r["app_slug"]].append(float(r["rating"]))
        except ValueError:
            pass

# ============================================================== 2. DATA HASIL
cat = collections.Counter()
cat_by_sent = collections.defaultdict(collections.Counter)
sent = collections.Counter()
asp_terms = collections.Counter()
opn_terms = collections.Counter()
opn_by_sent = collections.defaultdict(collections.Counter)
asp_by_cat = collections.defaultdict(collections.Counter)
asp_len, opn_len = [], []
impl_a = impl_o = 0
quad_total = 0
split_stats = {}
seen_text = {}
leak_lines = 0
clause_texts = collections.Counter()

for split in ("train", "dev", "test"):
    path = os.path.join(QUAD, f"appsid_quad_{split}.tsv")
    lines = 0
    tuples = 0
    il_a = il_o = 0
    tok_len = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if not line.strip():
                continue
            parts = line.split("\t")
            if len(parts) < 2:
                continue
            lines += 1
            text = parts[0]
            clause_texts[text.strip().lower()] += 1
            tok_len.append(len(text.split()))
            if split in ("train",):
                seen_text[text.strip().lower()] = True
            for q in parts[1:]:
                f = q.split()
                if len(f) < 4:
                    continue
                tuples += 1
                quad_total += 1
                a_st, a_ed = (int(x) for x in f[0].split(","))
                c = f[1]
                s = SENT_CODE.get(f[2], f[2])
                o_st, o_ed = (int(x) for x in f[3].split(","))
                cat[c] += 1
                sent[s] += 1
                cat_by_sent[c][s] += 1
                a_tokens = text.split()
                if a_st < 0:
                    il_a += 1
                    impl_a += 1
                else:
                    asp_len.append(a_ed - a_st)
                    term = " ".join(a_tokens[a_st:a_ed]).strip().lower()
                    if term:
                        asp_terms[term] += 1
                        asp_by_cat[c][term] += 1
                if o_st < 0:
                    il_o += 1
                    impl_o += 1
                else:
                    opn_len.append(o_ed - o_st)
                    term = " ".join(a_tokens[o_st:o_ed]).strip().lower()
                    if term:
                        opn_terms[term] += 1
                        opn_by_sent[s][term] += 1
    if split == "test":
        for line in open(path, encoding="utf-8"):
            t = line.split("\t")[0].strip().lower()
            if t in seen_text:
                leak_lines += 1
    split_stats[split] = {
        "baris": lines, "tuple": tuples,
        "tuple_per_baris": round(tuples / lines, 3) if lines else 0,
        "span_aspek_implisit": il_a, "span_opini_implisit": il_o,
        "rasio_aspek_implisit_pct": pct(il_a, tuples),
        "rasio_opini_implisit_pct": pct(il_o, tuples),
        "panjang_klausa_kata": quantiles(tok_len),
    }

# ============================================================== 3. REPLIKASI CAKUPAN
cov = {k: {"n_a": 0, "hit_a": 0, "n_o": 0, "hit_o": 0,
           "n_cl": 0, "hit_cl": 0} for k in ("raw/split", "raw/punct",
                                            "norm/split", "norm/punct")}
with open(os.path.join(SRC, "quintuples_weak.csv"), encoding="utf-8") as fh:
    for r in csv.DictReader(fh):
        rid = r["review_id"]
        if rid not in rows_clean:
            continue
        raw, norm = rows_clean[rid]
        a = r["aspect"].strip()
        o = r["opinion"].strip()
        cl = r["clause"]
        for key, source in (("raw", raw), ("norm", norm)):
            for mode in ("split", "punct"):
                k = f"{key}/{mode}"
                seq = toks_split(source) if mode == "split" else toks_punct(source)
                c = cov[k]
                if a not in SPLIT:
                    c["n_a"] += 1
                    c["hit_a"] += subseq_found(a, seq, mode)
                if o not in SPLIT:
                    c["n_o"] += 1
                    c["hit_o"] += subseq_found(o, seq, mode)
                if key == "norm":
                    c["n_cl"] += 1
                    c["hit_cl"] += subseq_found(cl, seq, mode)

cov_rows = []
for k, c in cov.items():
    cov_rows.append({
        "definisi": k,
        "aspek_pct": pct(c["hit_a"], c["n_a"]),
        "opini_pct": pct(c["hit_o"], c["n_o"]),
        "klausa_pct": pct(c["hit_cl"], c["n_cl"]),
        "n_aspek": c["n_a"], "n_opini": c["n_o"], "n_klausa": c["n_cl"],
    })

# ============================================================== 4. TULIS KELUARAN
def write_csv(name: str, header: list[str], rows: list[list]) -> None:
    with open(os.path.join(OUT, name), "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        w.writerows(rows)


write_csv("split_stats.csv",
          ["split", "baris", "tuple", "tuple_per_baris", "aspek_implisit",
           "opini_implisit", "rasio_aspek_implisit_pct", "rasio_opini_implisit_pct",
           "klausa_median_kata", "klausa_p95_kata", "klausa_max_kata"],
          [[s, d["baris"], d["tuple"], d["tuple_per_baris"], d["span_aspek_implisit"],
            d["span_opini_implisit"], d["rasio_aspek_implisit_pct"],
            d["rasio_opini_implisit_pct"], d["panjang_klausa_kata"]["median"],
            d["panjang_klausa_kata"]["p95"], d["panjang_klausa_kata"]["max"]]
           for s, d in split_stats.items()])

write_csv("category_counts.csv",
          ["category", "total", "positive", "negative", "neutral", "share_pct"],
          [[c, n, cat_by_sent[c]["positive"], cat_by_sent[c]["negative"],
            cat_by_sent[c]["neutral"], pct(n, quad_total)]
           for c, n in cat.most_common()])

write_csv("sentiment_counts.csv", ["sentiment", "count", "share_pct"],
          [[s, n, pct(n, quad_total)] for s, n in sent.most_common()])

def len_rows(vals: list[int], label: str) -> list[list]:
    d = collections.Counter(vals)
    return [[label, k, d[k]] for k in sorted(d)]

write_csv("span_length_dist.csv", ["span", "panjang_token", "count"],
          len_rows(asp_len, "aspek") + len_rows(opn_len, "opini"))

write_csv("top_aspect_terms.csv", ["term", "count", "share_pct"],
          [[t, n, pct(n, sum(asp_terms.values()))] for t, n in asp_terms.most_common(150)])
write_csv("top_opinion_terms.csv", ["term", "count", "share_pct"],
          [[t, n, pct(n, sum(opn_terms.values()))] for t, n in opn_terms.most_common(150)])

rows = []
for s in ("positive", "neutral", "negative"):
    for t, n in opn_by_sent[s].most_common(60):
        rows.append([s, t, n])
write_csv("opinion_terms_by_sentiment.csv", ["sentiment", "term", "count"], rows)

rows = []
for app, n in app_stats.most_common():
    rr = app_rating.get(app, [])
    rows.append([app, n, round(statistics.mean(rr), 2) if rr else 0,
                 round(100 * sum(1 for x in rr if x <= 2) / len(rr), 1) if rr else 0])
write_csv("review_stats.csv", ["app_slug", "reviews", "rating_mean", "rating_1_2_pct"], rows)

write_csv("coverage_replication.csv",
          ["definisi", "aspek_pct", "opini_pct", "klausa_pct", "n_aspek", "n_opini", "n_klausa"],
          [[r["definisi"], r["aspek_pct"], r["opini_pct"], r["klausa_pct"],
            r["n_aspek"], r["n_opini"], r["n_klausa"]] for r in cov_rows])

summary = {
    "sumber": {
        "ulasan": src["reviews"], "review_id_unik": src["uniq_ids"],
        "platform": dict(src["platform"]), "jumlah_aplikasi": len(src["apps"]),
        "tahun": dict(sorted(src["years"].items())),
        "rating": dict(sorted(src["ratings"].items())),
        "polaritas": dict(src["polarity"]),
        "kata_per_ulasan": quantiles(src["n_words"]),
        "emoji": {"total": sum(src["emoji"]), "ada_emoji": sum(1 for x in src["emoji"] if x > 0)},
        "ulasan_duplikat_teks": src["dup_text"],
    },
    "hasil": {
        "split": split_stats, "total_tuple": quad_total,
        "kategori": dict(cat.most_common()),
        "sentimen": dict(sent.most_common()),
        "aspek_implisit": impl_a, "opini_implisit": impl_o,
        "rasio_aspek_implisit_pct": pct(impl_a, quad_total),
        "rasio_opini_implisit_pct": pct(impl_o, quad_total),
        "istilah_aspek_unik": len(asp_terms), "istilah_opini_unik": len(opn_terms),
        "panjang_span_aspek": quantiles(asp_len), "panjang_span_opini": quantiles(opn_len),
        "kebocoran_baris_test_di_train": leak_lines,
        "kebocoran_pct_test": pct(leak_lines, split_stats["test"]["baris"]),
        "klausa_unik": len(clause_texts),
        "klausa_berulang": sum(c - 1 for c in clause_texts.values() if c > 1),
    },
    "replikasi_cakupan": cov_rows,
    "patokan_laporan_lama": {"aspek_pct": 61.5, "opini_pct": 48.0, "klausa_pct": 37.6,
                             "sumber": "023 §2.2 / 030 §3.3 / 035 §III-C"},
}

with open(os.path.join(OUT, "eda_summary.json"), "w", encoding="utf-8") as fh:
    json.dump(summary, fh, ensure_ascii=False, indent=2)

print(json.dumps(summary, ensure_ascii=False, indent=2)[:4000])
print("\n> berkas ditulis ke", OUT)
