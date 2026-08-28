# -*- coding: utf-8 -*-
"""Perbaikan tiga bug pipeline di notebook 00 PRO / PRO_Resume.

1. eval_gold_1 memakai id token mentah, bukan aspect_input_ids hasil feature,
   sehingga teks di pred4pipeline.txt bergeser satu token (dan kosong untuk
   kalimat satu kata). Itu yang membocorkan tag 'a--1,-1' ke kolom teks dan
   memicu KeyError di step 2.
2. Parser pasangan kandidat memisahkan teks/tag berdasarkan posisi kolom tab.
   Diganti pencocokan pola tag agar tag tidak pernah masuk kolom teks.
3. auto_find_file mengembalikan checkpoint pertama yang ditemukan, sehingga
   fallback step 2 sering mendapat checkpoint step 1 lalu diabaikan diam-diam.
"""
import json
import sys

CELL_CONFIG, CELL_STEP1, CELL_PAIR = 6, 12, 20
CELL_STEP2, CELL_EVAL, CELL_INFER = 22, 24, 26

OLD_GOLD_HEAD = (
    '    # 2. Muat Ground Truth (Gold)\n'
    '    eval_gold_1 = []\n'
    '    with open(os.path.join(extract_dir, "tokenized_data", f"{DOMAIN}_test_quad_bert.tsv"), "r", encoding="utf-8") as f:\n'
    '        for line in f:\n'
    '            line = line.strip().split("\\t")\n'
    '            cur_text = tokenizer.convert_tokens_to_ids(line[0].split(" "))\n'
    '            aspect_labels'
)
NEW_GOLD_HEAD = (
    '    # 2. Muat Ground Truth (Gold)\n'
    '    # input_text wajib memakai aspect_input_ids hasil feature ([CLS] .. [CLS]\n'
    '    # + zero-pad). pred_eval menulis pred4pipeline.txt dari\n'
    '    # ids_to_token[1:tokens_len-1]; id token mentah menggeser teks satu token\n'
    '    # dan mengosongkannya untuk kalimat satu kata.\n'
    '    eval_gold_labels = []\n'
    '    with open(os.path.join(extract_dir, "tokenized_data", f"{DOMAIN}_test_quad_bert.tsv"), "r", encoding="utf-8") as f:\n'
    '        for line in f:\n'
    '            line = line.strip().split("\\t")\n'
    '            aspect_labels'
)

OLD_GOLD_TAIL = (
    '            eval_gold_1.append([cur_text, [aspect_labels, cur_imp_a, cur_imp_o]])\n'
    '    eval_gold_1 = [[e[0] for e in eval_gold_1], [item for e in eval_gold_1 for item in e[1]]]'
)
NEW_GOLD_TAIL = (
    '            eval_gold_labels += [aspect_labels, cur_imp_a, cur_imp_o]\n'
    '    eval_gold_1 = [ev_ids.numpy().tolist(), eval_gold_labels]'
)

OLD_PARSE = (
    "    pair_records = []\n"
    "    os.makedirs(os.path.dirname(target_tokenized_tsv), exist_ok=True)\n"
    "    with cs.open(target_tokenized_tsv, 'w', encoding='utf-8') as wf:\n"
    "        for idx, line in enumerate(lines):\n"
    "            asp, opi = [], []\n"
    "            parts = line.strip().split('\\t')\n"
    "            if len(parts) <= 1: continue\n"
    "            text = parts[0]\n"
    "            for ele in parts[1:]:\n"
    "                if ele.startswith('a'): asp.append(ele[2:])\n"
    "                else: opi.append(ele[2:])\n"
    "            if not asp: asp.append('-1,-1')\n"
    "            if not opi: opi.append('-1,-1')"
)
NEW_PARSE = (
    "    # Tag dikenali dari polanya, bukan dari posisi kolom tab. Baris yang\n"
    "    # kehilangan tab tidak lagi menyelundupkan tag seperti 'a--1,-1' ke\n"
    "    # kolom teks (penyebab KeyError saat tokenisasi step 2).\n"
    "    TAG_RE = re.compile(r'^(a|o)-(-?\\d+,-?\\d+)$')\n"
    "    pair_records = []\n"
    "    os.makedirs(os.path.dirname(target_tokenized_tsv), exist_ok=True)\n"
    "    with cs.open(target_tokenized_tsv, 'w', encoding='utf-8') as wf:\n"
    "        for line in lines:\n"
    "            asp, opi, text_parts = [], [], []\n"
    "            for tok in line.strip().split():\n"
    "                m = TAG_RE.match(tok)\n"
    "                if m:\n"
    "                    (asp if m.group(1) == 'a' else opi).append(m.group(2))\n"
    "                else:\n"
    "                    text_parts.append(tok)\n"
    "            if not text_parts: continue\n"
    "            text = ' '.join(text_parts)\n"
    "            if not asp: asp.append('-1,-1')\n"
    "            if not opi: opi.append('-1,-1')"
)

OLD_FIND_SIG = (
    'def auto_find_file(filename, search_roots=None):\n'
    '    """Mencari berkas di dalam direktori sesi aktif atau direktori sesi terdahulu."""'
)
NEW_FIND_SIG = (
    'def auto_find_file(filename, search_roots=None, must_contain=None):\n'
    '    """Mencari berkas di direktori sesi aktif atau sesi terdahulu.\n'
    '    must_contain menyaring hasil berdasarkan potongan path (mis. "step2_best")\n'
    '    agar checkpoint step 1 tidak terambil saat yang dicari checkpoint step 2."""'
)

OLD_FIND_BODY = (
    '        for root, dirs, files in os.walk(sr):\n'
    '            if filename in files:\n'
    '                return os.path.join(root, filename)\n'
    '    return None'
)
NEW_FIND_BODY = (
    '        for root, dirs, files in os.walk(sr):\n'
    '            if filename in files:\n'
    '                hit = os.path.join(root, filename)\n'
    '                if must_contain and must_contain not in hit.replace(os.sep, "/"):\n'
    '                    continue\n'
    '                return hit\n'
    '    return None'
)

OLD_IMPORT = "import codecs as cs"
NEW_IMPORT = "import codecs as cs\nimport re"

# Semua pemanggilan checkpoint memakai must_contain supaya tidak mengambil
# checkpoint tahap lain lalu diabaikan diam-diam oleh pemeriksaan sesudahnya.
CKPT_CALLS = [
    (
        CELL_STEP1,
        '    found_bin = auto_find_file("pytorch_model.bin", search_roots=[',
        '    found_bin = auto_find_file("pytorch_model.bin", must_contain="step1_best", search_roots=[',
        "fallback checkpoint step 1",
    ),
    (
        CELL_STEP2,
        '    found_bin2 = auto_find_file("pytorch_model.bin", search_roots=[',
        '    found_bin2 = auto_find_file("pytorch_model.bin", must_contain="step2_best", search_roots=[',
        "fallback checkpoint step 2",
    ),
    (
        CELL_EVAL,
        '        found_bin2 = auto_find_file("pytorch_model.bin")',
        '        found_bin2 = auto_find_file("pytorch_model.bin", must_contain="step2_best")',
        "fallback checkpoint evaluasi",
    ),
    (
        CELL_INFER,
        '    found_b1 = auto_find_file("pytorch_model.bin")',
        '    found_b1 = auto_find_file("pytorch_model.bin", must_contain="step1_best")',
        "fallback checkpoint inferensi step 1",
    ),
    (
        CELL_INFER,
        '    found_b2 = auto_find_file("pytorch_model.bin")',
        '    found_b2 = auto_find_file("pytorch_model.bin", must_contain="step2_best")',
        "fallback checkpoint inferensi step 2",
    ),
]

# SubtaskMetricCapture menyimpan kunci "micro-F1" dan nama sub-task dipisah
# spasi. Pembaca cache memakai "micro_f1" dan split('-'), jadi jalur cache
# selalu memberi Micro_F1 = 0 dan N_Elements salah.
OLD_CACHE_SUBTASK = (
    '        {"Subtask": k, "Precision": v.get("precision", 0.0), "Recall": v.get("recall", 0.0), '
    '"Micro_F1": v.get("micro_f1", 0.0), "N_Elements": len(k.split(\'-\'))}'
)
NEW_CACHE_SUBTASK = (
    '        {"Subtask": k, "Precision": v.get("precision", 0.0), "Recall": v.get("recall", 0.0),\n'
    '         "Micro_F1": v.get("micro-F1", 0.0), "N_Elements": len(k.split())}'
)


def read_source(cell):
    return "".join(cell["source"])


def write_source(cell, text):
    lines = text.split("\n")
    cell["source"] = [l + "\n" for l in lines[:-1]] + ([lines[-1]] if lines[-1] else [])


def replace_once(cell, old, new, tag):
    text = read_source(cell)
    # new diperiksa lebih dulu: beberapa new memuat old sebagai awalan, jadi
    # memeriksa old dulu akan menerapkan hunk yang sama dua kali.
    if new in text:
        print("  skip (sudah diperbaiki):", tag)
        return
    if old not in text:
        raise SystemExit("  GAGAL: pola tidak ditemukan -> " + tag)
    write_source(cell, text.replace(old, new, 1))
    print("  ok:", tag)


def patch(path):
    print(path)
    with open(path, encoding="utf-8") as f:
        nb = json.load(f)
    cells = nb["cells"]
    if len(cells) != 29:
        raise SystemExit("  GAGAL: jumlah sel tidak sesuai (%d)" % len(cells))

    replace_once(cells[CELL_CONFIG], OLD_FIND_SIG, NEW_FIND_SIG, "auto_find_file signature")
    replace_once(cells[CELL_CONFIG], OLD_FIND_BODY, NEW_FIND_BODY, "auto_find_file filter")
    replace_once(cells[CELL_STEP1], OLD_GOLD_HEAD, NEW_GOLD_HEAD, "eval_gold_1 sumber id")
    replace_once(cells[CELL_STEP1], OLD_GOLD_TAIL, NEW_GOLD_TAIL, "eval_gold_1 perakitan")
    replace_once(cells[CELL_PAIR], OLD_PARSE, NEW_PARSE, "parser pasangan kandidat")
    replace_once(cells[CELL_PAIR], OLD_IMPORT, NEW_IMPORT, "import re")
    replace_once(cells[CELL_EVAL], OLD_CACHE_SUBTASK, NEW_CACHE_SUBTASK, "pembacaan cache sub-task")
    for index, old, new, tag in CKPT_CALLS:
        replace_once(cells[index], old, new, tag)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(nb, f, ensure_ascii=False, indent=1)


for target in sys.argv[1:]:
    patch(target)
