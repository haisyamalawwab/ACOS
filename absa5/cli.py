"""Command line entry point.

Data commands run without torch; ``train`` and ``prepare-backbone`` need it.

    python -m absa5 gates
    python -m absa5 inspect --schema quint --category resto_id --emotion emot_id
    python -m absa5 extend-emotion --in data/Restaurant-ACOS/rest16_quad_train.tsv --out work/rest16_train_quint.tsv
    python -m absa5 annotate --in work/rest16_train_quint.tsv --out work/tasks.csv
    python -m absa5 prepare --config configs/quint.json
    python -m absa5 train --config configs/quint.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import List, Optional, Sequence

from .config import RunConfig, list_presets, preset
from .data import read_records, write_records
from .schema import QUAD, QUINT, get_schema
from .taxonomy import CATEGORIES, EMOTIONS, SENTIMENTS


def _add_config_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--config", help="path to a RunConfig JSON file")
    parser.add_argument("--preset", help=f"preset name ({', '.join(list_presets())})")
    parser.add_argument(
        "--set",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="dotted override, e.g. --set train.epochs=3",
    )


def _load_config(args) -> RunConfig:
    if args.config:
        cfg = RunConfig.from_json(args.config)
    elif args.preset:
        cfg = preset(args.preset)
    else:
        raise SystemExit("pass either --config or --preset")
    overrides = {}
    for item in args.set:
        if "=" not in item:
            raise SystemExit(f"--set expects KEY=VALUE, got {item!r}")
        key, value = item.split("=", 1)
        overrides[key] = _coerce(value)
    return cfg.merged(**overrides) if overrides else cfg


def _coerce(value: str):
    for caster in (int, float):
        try:
            return caster(value)
        except ValueError:
            continue
    if value.lower() in ("true", "false"):
        return value.lower() == "true"
    if value.lower() in ("none", "null"):
        return None
    return value


# -- commands --------------------------------------------------------------
def cmd_gates(args) -> int:
    from .selftest import main as selftest_main

    argv = ["--repo", args.repo]
    if args.only:
        argv += ["--only", *args.only]
    if args.json_path:
        argv += ["--json", args.json_path]
    if args.verbose:
        argv.append("--verbose")
    return selftest_main(argv)


def cmd_inspect(args) -> int:
    """Print the label-space arithmetic that decides joint vs factored."""
    from .taxonomy import build_label_spaces

    schema = get_schema(args.schema)
    kwargs = {}
    if "category" in schema.labels:
        kwargs["category"] = args.category
    if "sentiment" in schema.labels:
        kwargs["sentiment"] = args.sentiment
    if "emotion" in schema.labels:
        kwargs["emotion"] = args.emotion
    spaces = build_label_spaces(schema, **kwargs)

    observed = None
    if args.data:
        records = read_records(args.data, schema, strict=False)
        observed = [v for r in records for v in r.label_values()]
    report = spaces.report(observed)

    print(f"schema        {schema.name} (arity {schema.arity})")
    print(f"elements      {', '.join(schema.names)}")
    print(f"span slots    {', '.join(schema.spans)}")
    print(f"label slots   {', '.join(schema.labels)}")
    for element, size in report["sizes"].items():
        print(f"  {element:<12} {size}")
    print(f"joint head    {report['joint_size']} outputs")
    print(f"factored head {report['factored_size']} outputs")
    if observed is not None:
        print()
        print(f"observed tuples        {report['observed_tuples']}")
        print(
            f"joint cells seen       {report['joint_cells_seen']}/{report['joint_size']} "
            f"({report['joint_coverage']:.1%})"
        )
        print(f"cells with under 10    {report['joint_cells_below_10']}")
        print(f"per element seen       {report['per_element_seen']}")
        print(f"per element min supp   {report['per_element_min_support']}")
    if args.json_path:
        with open(args.json_path, "w", encoding="utf-8") as fh:
            json.dump(report, fh, indent=2, ensure_ascii=False)
        print(f"\nwrote {args.json_path}")
    return 0


def cmd_extend_emotion(args) -> int:
    from .emotion import TAGGERS, extend_file

    tagger = TAGGERS.build(args.tagger)
    report = extend_file(
        args.input,
        args.output,
        quad_schema=args.from_schema,
        quint_schema=args.to_schema,
        tagger=tagger,
        report_path=args.report,
    )
    print(f"{report['rows']} rows, {report['tuples']} tuples -> {report['output']}")
    print(f"distribution: {report['distribution']}")
    print(
        f"{report['unambiguous_ratio']:.1%} of tuples matched exactly one cue; "
        f"the rest fell back to sentiment"
    )
    print(f"\nredundancy check: {report['redundancy_verdict']}")
    print(f"emotion given sentiment: {report['emotion_given_sentiment']}")
    print(f"\n{report['warning']}")
    return 0


def cmd_annotate(args) -> int:
    from .emotion import TAGGERS, export_annotation_tasks

    schema = get_schema(args.schema)
    records = read_records(args.input, schema, strict=False)
    if args.limit:
        records = records[: args.limit]
    report = export_annotation_tasks(
        records,
        args.output,
        tagger=TAGGERS.build(args.tagger),
        emotion_set=args.emotion,
    )
    print(f"{report['rows']} rows to annotate -> {report['output']}")
    print(f"guideline -> {report['guideline']}")
    print(f"labels: {', '.join(report['labels'])}")
    return 0


def cmd_import_annotations(args) -> int:
    from .emotion import import_annotations

    records = read_records(args.input, get_schema(args.from_schema), strict=False)
    extended, report = import_annotations(
        args.tasks,
        records,
        args.to_schema,
        emotion_set=args.emotion,
        require_complete=not args.allow_incomplete,
    )
    write_records(args.output, extended, get_schema(args.to_schema))
    print(f"{report['annotated']} annotated, {report['missing']} missing -> {args.output}")
    print(f"status: {report['status']}")
    return 0


def cmd_prepare(args) -> int:
    from .pipeline import prepare_data

    cfg = _load_config(args)
    artifacts = prepare_data(cfg, strict=not args.lenient)
    print(f"work dir: {artifacts.work_dir}")
    for split, path in artifacts.tokenized.items():
        report = artifacts.reports[split]
        print(
            f"  {split:<6} {report['rows']} rows, {report['tuples']} tuples, "
            f"unknown-token ratio {report['unk_ratio']:.2%}, "
            f"{report['rows_over_limit']} rows over the subword limit"
        )
    label = artifacts.label_report
    print(
        f"joint space: {label['joint_cells_seen']}/{label['joint_size']} cells observed "
        f"({label['joint_coverage']:.1%}); {label['joint_cells_below_10']} under 10 examples"
    )
    return 0


def cmd_prepare_backbone(args) -> int:
    from .encoders import ENCODERS, prepare_checkpoint

    report = prepare_checkpoint(
        args.encoder, args.output, force=args.force,
        report_path=os.path.join(args.output, "_prepare.json"),
    )
    print(f"{report.model_name} -> {report.target_dir}")
    print(
        f"{report.keys_before} keys in, {report.keys_after} out, "
        f"{report.keys_reprefixed} re-prefixed, {len(report.dropped_keys)} dropped"
    )
    for warning in report.warnings:
        print(f"  warning: {warning}")
    return 0


def cmd_train(args) -> int:
    from .pipeline import run, summarize_run

    cfg = _load_config(args)
    result = run(
        cfg,
        checkpoint_dir=args.checkpoint,
        prepare=not args.skip_prepare,
        stages=args.stages,
        verify_weights=not args.no_verify,
    )
    print(summarize_run(result))
    return 0


def cmd_references(args) -> int:
    """Print the bibliography, optionally filtered or as BibTeX."""
    from .references import (
        CROSSREF_CHECKED,
        all_references,
        bibliography,
        bibtex,
        for_module,
        markdown_table,
        without_doi,
    )

    if args.bibtex:
        print(bibtex(*args.keys) if args.keys else bibtex())
        return 0

    if args.table:
        print(markdown_table())
        return 0

    if args.module:
        refs = for_module(args.module)
        if not refs:
            print(f"no references registered for absa5.{args.module}")
            return 1
        print(f"references cited by absa5.{args.module}:\n")
        for ref in refs:
            print(f"- {ref.full()}")
        return 0

    if args.grouped:
        print(bibliography(group_by_module=True))
        return 0

    refs = all_references()
    missing = without_doi()
    print(bibliography())
    print()
    print(
        f"{len(refs)} references, {len(refs) - len(missing)} with DOIs verified against "
        f"the Crossref API on {CROSSREF_CHECKED}."
    )
    if missing:
        print(f"{len(missing)} have no DOI: {', '.join(r.key for r in missing)}")
    return 0


def cmd_registries(args) -> int:
    from .emotion import TAGGERS
    from .features import TAGGING
    from .schema import SCHEMAS
    from .taxonomy import source_of
    from .tokenizers import TOKENIZERS

    rows = [
        ("schema", SCHEMAS.names()),
        ("category set", CATEGORIES.names()),
        ("sentiment set", SENTIMENTS.names()),
        ("emotion set", EMOTIONS.names()),
        ("tokenizer", TOKENIZERS.names()),
        ("tagging", TAGGING.names()),
        ("emotion tagger", TAGGERS.names()),
        ("preset", list_presets()),
    ]
    for kind, names in rows:
        print(f"{kind:<16} {', '.join(names)}")

    print("\nlabel set sources:")
    for name in CATEGORIES.names() + SENTIMENTS.names() + EMOTIONS.names():
        ref = source_of(name)
        print(f"  {name:<16} {ref.cite() if ref else '(none)'}")

    print("\nheads and models register on first use (they need torch)")
    return 0


def cmd_write_config(args) -> int:
    cfg = _load_config(args)
    cfg.to_json(args.output)
    print(f"wrote {args.output}")
    print(json.dumps(cfg.summary(), indent=2, ensure_ascii=False))
    return 0


# -- parser ----------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="absa5", description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("gates", help="run the verification gates")
    p.add_argument("--repo", default=".")
    p.add_argument("--only", nargs="*")
    p.add_argument("--json", dest="json_path")
    p.add_argument("--verbose", action="store_true")
    p.set_defaults(func=cmd_gates)

    p = sub.add_parser("inspect", help="show label-space sizes and, with --data, coverage")
    p.add_argument("--schema", default="quint")
    p.add_argument("--category", default="resto_id")
    p.add_argument("--sentiment", default="acos")
    p.add_argument("--emotion", default="emot_id")
    p.add_argument("--data", help="tsv file to measure observed coverage against")
    p.add_argument("--json", dest="json_path")
    p.set_defaults(func=cmd_inspect)

    p = sub.add_parser("extend-emotion", help="add a suggested emotion column to quad data")
    p.add_argument("--in", dest="input", required=True)
    p.add_argument("--out", dest="output", required=True)
    p.add_argument("--from-schema", default="quad")
    p.add_argument("--to-schema", default="quint")
    p.add_argument("--tagger", default="lexicon")
    p.add_argument("--report")
    p.set_defaults(func=cmd_extend_emotion)

    p = sub.add_parser("annotate", help="export a CSV for human emotion annotation")
    p.add_argument("--in", dest="input", required=True)
    p.add_argument("--out", dest="output", required=True)
    p.add_argument("--schema", default="quad")
    p.add_argument("--tagger", default="lexicon")
    p.add_argument("--emotion", default="emot_id")
    p.add_argument("--limit", type=int)
    p.set_defaults(func=cmd_annotate)

    p = sub.add_parser("import-annotations", help="merge a completed annotation CSV back in")
    p.add_argument("--in", dest="input", required=True)
    p.add_argument("--tasks", required=True)
    p.add_argument("--out", dest="output", required=True)
    p.add_argument("--from-schema", default="quad")
    p.add_argument("--to-schema", default="quint")
    p.add_argument("--emotion", default="emot_id")
    p.add_argument("--allow-incomplete", action="store_true")
    p.set_defaults(func=cmd_import_annotations)

    p = sub.add_parser("prepare", help="retokenize, remap spans, build pair files")
    _add_config_args(p)
    p.add_argument("--lenient", action="store_true", help="skip bad rows instead of failing")
    p.set_defaults(func=cmd_prepare)

    p = sub.add_parser("prepare-backbone", help="download and re-key a checkpoint (needs torch)")
    p.add_argument("--encoder", default="indobert")
    p.add_argument("--output", required=True)
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_prepare_backbone)

    p = sub.add_parser("train", help="run the full pipeline (needs torch)")
    _add_config_args(p)
    p.add_argument("--checkpoint", help="prepared backbone directory")
    p.add_argument("--skip-prepare", action="store_true")
    p.add_argument("--no-verify", action="store_true", help="skip the weight-loading gate")
    p.add_argument(
        "--stages",
        nargs="*",
        default=["extraction", "classification", "end_to_end"],
    )
    p.set_defaults(func=cmd_train)

    p = sub.add_parser("registries", help="list every pluggable name")
    p.set_defaults(func=cmd_registries)

    p = sub.add_parser("references", help="bibliography with DOIs")
    p.add_argument("keys", nargs="*", help="restrict BibTeX output to these keys")
    p.add_argument("--module", help="only references cited by absa5.<module>")
    p.add_argument("--grouped", action="store_true", help="group by citing module")
    p.add_argument("--bibtex", action="store_true")
    p.add_argument("--table", action="store_true", help="markdown table of keys and DOIs")
    p.set_defaults(func=cmd_references)

    p = sub.add_parser("write-config", help="materialise a preset as JSON")
    _add_config_args(p)
    p.add_argument("--output", required=True)
    p.set_defaults(func=cmd_write_config)

    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    legacy = os.path.join(repo, "Extract-Classify-ACOS")
    if os.path.isdir(legacy) and legacy not in sys.path:
        sys.path.insert(0, legacy)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
