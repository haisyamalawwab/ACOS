"""Simulasi eksekusi sel-sel torch-free notebook V4 di mesin tanpa torch.

Menjalankan sel nyata (diambil dari .ipynb, bukan salinan) di satu namespace
bersama, dengan stub minimal untuk torch/seaborn dan helper colab_utils yang
menyentuh GPU/Drive. Tujuannya menangkap kesalahan urutan variabel — jenis bug
yang lolos pemeriksaan AST karena setiap nama *ada* di suatu sel, hanya di sel
yang dilewati.

Khusus tata letak dua-root, yang diverifikasi: `indo_root` menunjuk
`ACOS-IndoBERT/`, `acos_root` menunjuk repo upstream, `tokenized_base` mengarah
ke `indo_root` untuk domain Indonesia, dan `results_base`/`bert_cache_dir`/folder
sesi semuanya di bawah `indo_root` sehingga repo upstream tidak menerima artefak.

Pemakaian: python build/_sim_v4_cells.py
"""
import io
import json
import os
import shutil
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
INDO_ROOT = os.path.dirname(HERE)
ACOS_ROOT = os.path.dirname(INDO_ROOT)
NB = os.path.join(INDO_ROOT, "notebooks",
                  "00_ACOS_Master_Pipeline_Colab_V4_INDOBERT.ipynb")
WORK = os.path.join(HERE, "_sim_v4")


def install_seaborn_stub():
    """Stub seaborn: hanya diimpor di sel setup, tidak dipakai jalur Indonesia.

    `acos_id.eda` sengaja tidak memakai seaborn (heatmap-nya dibuat dengan
    matplotlib), jadi stub kosong cukup untuk simulasi.
    """
    if "seaborn" in sys.modules:
        return
    sns = types.ModuleType("seaborn")
    sns.__version__ = "0.0.0-stub"
    sns.heatmap = lambda *a, **k: None
    sns.barplot = lambda *a, **k: None
    sns.set_theme = lambda *a, **k: None
    sys.modules["seaborn"] = sns


def install_torch_stub():
    """Stub torch secukupnya untuk sel setup, seeding, dan cek CUDA."""
    if "torch" in sys.modules:
        return sys.modules["torch"]
    torch = types.ModuleType("torch")
    torch.__version__ = "0.0.0-stub"

    class _Cuda:
        @staticmethod
        def is_available():
            return False

        @staticmethod
        def manual_seed_all(seed):
            pass

        @staticmethod
        def empty_cache():
            pass

        @staticmethod
        def get_device_name(i=0):
            return "stub"

        @staticmethod
        def get_device_properties(i=0):
            return types.SimpleNamespace(total_memory=0)

        @staticmethod
        def memory_allocated(dev=None):
            return 0

    torch.cuda = _Cuda()
    torch.manual_seed = lambda seed: None
    torch.device = lambda spec: f"device:{spec}"
    torch.backends = types.SimpleNamespace(
        cudnn=types.SimpleNamespace(benchmark=False, version=lambda: 0))
    torch.long = "long"
    torch.float = "float"
    torch.tensor = lambda *a, **k: None
    torch.save = lambda *a, **k: None
    torch.load = lambda *a, **k: {}
    torch.no_grad = lambda: types.SimpleNamespace(
        __enter__=lambda s: None, __exit__=lambda s, *a: False)
    utils = types.ModuleType("torch.utils")
    data = types.ModuleType("torch.utils.data")
    for name in ("TensorDataset", "DataLoader", "RandomSampler", "SequentialSampler"):
        setattr(data, name, type(name, (), {}))
    utils.data = data
    torch.utils = utils
    sys.modules["torch"] = torch
    sys.modules["torch.utils"] = utils
    sys.modules["torch.utils.data"] = data
    return torch


def load_cells():
    with io.open(NB, encoding="utf-8") as fh:
        return json.load(fh)["cells"]


def cell_source(cell):
    """Sumber sel dengan magic IPython dinetralkan."""
    out = []
    for ln in "".join(cell["source"]).split("\n"):
        s = ln.lstrip()
        if s.startswith("!") or s.startswith("%"):
            out.append(ln[:len(ln) - len(s)] + "pass  # magic dinetralkan")
        else:
            out.append(ln)
    return "\n".join(out)


def find(cells, needle, nth=0):
    hits = [i for i, c in enumerate(cells)
            if c["cell_type"] == "code" and needle in "".join(c["source"])]
    if not hits:
        raise LookupError(f"sel kode dengan '{needle}' tidak ada")
    return hits[nth]


def colab_utils_stubs(ns):
    """Helper colab_utils yang menyentuh GPU/Drive/plot, distub."""

    def setup_run_dir(base_dir="results", domain="rest16"):
        dirs = {"root": os.path.join(base_dir, f"{domain}_SIM")}
        for k in ("checkpoints", "plots", "csv", "md", "logs"):
            dirs[k] = os.path.join(dirs["root"], k)
        dirs["step1_checkpoint"] = os.path.join(dirs["checkpoints"], "step1_best")
        dirs["step2_checkpoint"] = os.path.join(dirs["checkpoints"], "step2_best")
        for p in dirs.values():
            os.makedirs(p, exist_ok=True)
        return dirs

    def export_step_table(df, name, csv_dir, md_dir, title="", **kw):
        os.makedirs(csv_dir, exist_ok=True)
        os.makedirs(md_dir, exist_ok=True)
        df.to_csv(os.path.join(csv_dir, name + ".csv"), index=False)
        with open(os.path.join(md_dir, name + ".md"), "w", encoding="utf-8") as fh:
            fh.write(f"### {title}\n\n" + df.to_string(index=False))
        print(f"   [stub export_step_table] {name} ({len(df)} baris)")

    class Rep:
        def __getattr__(self, _name):
            return lambda *a, **k: self

    ns.update({
        "setup_timestamped_run_dir": setup_run_dir,
        "download_bert_pretrained": lambda target_dir=None: print(
            f"   [stub download_bert_pretrained] {target_dir}"),
        "verify_session_save_paths": lambda *a, **k: True,
        "find_resumable_session": lambda *a, **k: None,
        "auto_find_file": lambda *a, **k: None,
        "export_step_table": export_step_table,
        "update_mcp_manifest": lambda *a, **k: print(f"   [stub manifest] {a[0]}"),
        "save_pipeline_state": lambda *a, **k: "",
        "rep": Rep(),
        "analyze_and_plot_eda": lambda **k: (None, None),
        "inspect_acos_drive_structure": lambda **k: {},
    })


def main():
    os.makedirs(WORK, exist_ok=True)
    install_torch_stub()
    install_seaborn_stub()

    cells = load_cells()
    ns = {"__name__": "__main__"}

    for label, needle in [
        ("impor pustaka", "import pandas as pd"),
        ("diagnostik GPU", "GPU Hardware Diagnostics"),
        ("1b pelacak progres", "class step_stage"),
    ]:
        idx = find(cells, needle)
        print(f"\n=== sel {idx}: {label} " + "=" * 28)
        exec(compile(cell_source(cells[idx]), f"cell{idx}", "exec"), ns)

    # Sel 2 aslinya mendeteksi Drive dan meng-clone repo bila perlu; di sini
    # base_project_dir ditetapkan langsung ke repo upstream, seperti hasil deteksi
    # lokal. Sel 2c berikutnya yang menghitung indo_root/acos_root.
    ns.update({
        "base_project_dir": ACOS_ROOT,
        "save_dir": WORK,
        "extract_dir": os.path.join(ACOS_ROOT, "Extract-Classify-ACOS"),
        "notebooks_dir": os.path.join(ACOS_ROOT, "notebooks"),
        "data_root": os.path.join(ACOS_ROOT, "data"),
    })
    print(f"\n[sim] base_project_dir = {ACOS_ROOT} (pengganti deteksi Drive)")

    idx = find(cells, "ACOS_ID_MODULES")
    print(f"\n=== sel {idx}: 2c dua root + acos_id " + "=" * 20)
    exec(compile(cell_source(cells[idx]), f"cell{idx}", "exec"), ns)

    colab_utils_stubs(ns)

    for label, needle in [
        ("3 konfigurasi (DOMAIN/BACKBONE)", 'BACKBONE = "indobert"'),
        ("session_dirs_from_root", "def session_dirs_from_root"),
        ("session_cache_score", "def session_cache_score"),
        ("sesi + bert_cache_dir", "candidate_result_roots"),
    ]:
        idx = find(cells, needle)
        print(f"\n=== sel {idx}: {label} " + "=" * 28)
        exec(compile(cell_source(cells[idx]), f"cell{idx}", "exec"), ns)

    # Sel 4c butuh torch (torch.load/save pada state_dict), jadi bagian rekey-nya
    # tidak bisa disimulasikan. Yang dipastikan tersedia di sini hanya vocab.txt —
    # satu-satunya keluaran 4c yang dipakai sel 4d.
    vocab_src = os.path.join(INDO_ROOT, "backbones", "indobert_base_p1", "vocab.txt")
    if not os.path.exists(vocab_src):
        print(f"\n[sim] ⚠️ vocab IndoBERT tidak ada di {vocab_src}")
        return 1
    os.makedirs(ns["bert_cache_dir"], exist_ok=True)
    vocab_dst = os.path.join(ns["bert_cache_dir"], "vocab.txt")
    if os.path.abspath(vocab_src) != os.path.abspath(vocab_dst):
        shutil.copy(vocab_src, vocab_dst)
    print(f"\n[sim] vocab.txt IndoBERT tersedia di {ns['bert_cache_dir']} "
          f"(pengganti sel 4c; rekey state_dict butuh torch)")

    idx = find(cells, "id_gate_results")
    print(f"\n=== sel {idx}: 4d gerbang data " + "=" * 28)
    exec(compile(cell_source(cells[idx]), f"cell{idx}", "exec"), ns)

    print("\n" + "=" * 62)
    print("HASIL SIMULASI")
    print("=" * 62)
    for k in ("DOMAIN", "BACKBONE", "indo_root", "acos_root", "extract_dir",
              "tokenized_base", "tokenized_dir", "bert_cache_dir", "results_base"):
        print(f"{k:16s}: {ns.get(k)}")
    print(f"{'session root':16s}: {ns.get('session_dirs', {}).get('root')}")

    def di_bawah(nilai, root):
        return os.path.abspath(str(nilai or "")).startswith(root)

    cek = [
        ("indo_root benar", os.path.abspath(ns.get("indo_root", "")) == INDO_ROOT),
        ("acos_root benar", os.path.abspath(ns.get("acos_root", "")) == ACOS_ROOT),
        ("tokenized_base = indo_root",
         os.path.abspath(ns.get("tokenized_base", "")) == INDO_ROOT),
        ("results_base di bawah indo_root", di_bawah(ns.get("results_base"), INDO_ROOT)),
        ("bert_cache_dir di bawah indo_root",
         di_bawah(ns.get("bert_cache_dir"), INDO_ROOT)),
        ("folder sesi di bawah indo_root",
         di_bawah(ns.get("session_dirs", {}).get("root"), INDO_ROOT)),
        ("extract_dir menunjuk repo upstream",
         os.path.abspath(ns.get("extract_dir", "")) ==
         os.path.join(ACOS_ROOT, "Extract-Classify-ACOS")),
    ]
    print()
    ok = True
    for nama, hasil in cek:
        print(f"  {'✅' if hasil else '❌'} {nama}")
        ok &= hasil

    gates = ns.get("id_gate_results", {})
    print(f"\ngate: {[(k, v['ok']) for k, v in gates.items()]}")
    if not gates:
        print("❌ id_gate_results kosong — sel 4d tidak menjalankan gate")
        return 1
    ok &= all(v["ok"] for v in gates.values())

    print("\n" + ("✅ Semua sel torch-free berjalan, path dua-root benar, gate hijau."
                  if ok else "❌ Ada yang salah, lihat tanda ❌ di atas."))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
