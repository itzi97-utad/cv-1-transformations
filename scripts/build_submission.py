#!/usr/bin/env python3
"""Merge the per-section notebooks into the single .ipynb to upload to Blackboard.

    python scripts/build_submission.py            # check + merge + execute
    python scripts/build_submission.py --check    # only run the checks
    python scripts/build_submission.py --no-exec  # merge without executing

Order: notebooks/00_title, 00_setup, then 01_... 09_10_... (sorted by name).
Cells tagged `dev-only` (the `%run ./00_setup.ipynb` lines) are dropped.
The merged notebook is executed so it ships with all outputs visible.

Checks (from the statement's penalty list):
  * forbidden library calls in the sections that must be implemented by hand
  * colour -> greyscale conversions (all 10 images are colour; converting one
    means that image is not graded)
  * TODO placeholders left in group names / justification cells
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import nbformat

ROOT = Path(__file__).resolve().parent.parent
NB_DIR = ROOT / "notebooks"
OUT_DIR = ROOT / "submission"
DEFAULT_NAME = "P1_Transformations.ipynb"

# section prefix -> patterns that must not appear in its code cells
FORBIDDEN = {
    "01": [r"createCLAHE", r"equalize_adapthist"],
    "04": [r"GaussianBlur", r"getGaussianKernel", r"filters\.gaussian", r"ndimage\.gaussian",
           r"from\s+scipy\.ndimage\s+import.*gaussian", r"from\s+skimage\.filters\s+import.*gaussian"],
    "05": [r"(?i)pykuwahara", r"(?i)import\s+.*kuwahara", r"(?i)from\s+\S*kuwahara"],
}
# allowed-but-ask patterns: library convolution with your own kernel etc.
RISKY = {
    "01": [r"equalizeHist", r"exposure\.equalize_hist"],
    "04": [r"filter2D", r"sepFilter2D", r"ndimage\.convolve", r"signal\.convolve"],
    "05": [r"filter2D", r"boxFilter", r"\bblur\s*\("],
}
GREY = [r"COLOR_BGR2GRAY", r"COLOR_RGB2GRAY", r"COLOR_BGRA2GRAY", r"COLOR_RGBA2GRAY",
        r"IMREAD_GRAYSCALE", r"rgb2gray", r"\.convert\(\s*['\"]L['\"]"]


def section_notebooks() -> list[Path]:
    nbs = sorted(NB_DIR.glob("*.ipynb"))
    head = [NB_DIR / "00_title.ipynb", NB_DIR / "00_setup.ipynb"]
    return head + [p for p in nbs if p not in head and not p.name.startswith("_")]


def strip_comments(src: str) -> str:
    return "\n".join(line.split("#", 1)[0] for line in src.splitlines())


def check(nbs: list[Path]) -> tuple[list[str], list[str]]:
    errors, warnings = [], []
    for path in nbs:
        nb = nbformat.read(path, as_version=4)
        prefix = path.name[:2]
        for i, cell in enumerate(nb.cells):
            where = f"{path.name} cell {i}"
            if cell.cell_type == "code":
                src = strip_comments(cell.source)
                if "raise NotImplementedError" in src:
                    warnings.append(f"{where}: still raises NotImplementedError")
                for pat in FORBIDDEN.get(prefix, []):
                    if re.search(pat, src):
                        errors.append(f"{where}: forbidden library call /{pat}/ (image won't be graded)")
                for pat in RISKY.get(prefix, []):
                    if re.search(pat, src):
                        warnings.append(f"{where}: /{pat}/ is a library op on a hand-made section; "
                                        "make sure it isn't doing the graded transformation")
                for pat in GREY:
                    if re.search(pat, src):
                        warnings.append(f"{where}: colour->grey conversion /{pat}/: all images are colour, "
                                        "converting the result means it isn't graded. Fine only if internal "
                                        "and the shown result stays in colour; justify it")
            elif "TODO" in cell.source:
                warnings.append(f"{where}: markdown still contains TODO")
    return errors, warnings


def merge(nbs: list[Path]) -> nbformat.NotebookNode:
    merged = nbformat.v4.new_notebook()
    first = nbformat.read(nbs[0], as_version=4)
    merged.metadata = first.metadata
    for path in nbs:
        nb = nbformat.read(path, as_version=4)
        for cell in nb.cells:
            if "dev-only" in cell.metadata.get("tags", []):
                continue
            cell["id"] = f"cell-{len(merged.cells):03d}"
            if cell.cell_type == "code":
                cell.outputs, cell.execution_count = [], None
            merged.cells.append(cell)
    return merged


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="only run the checks")
    ap.add_argument("--no-exec", action="store_true", help="merge without executing")
    ap.add_argument("-o", "--output", default=DEFAULT_NAME, help=f"file name in submission/ (default {DEFAULT_NAME})")
    ap.add_argument("--timeout", type=int, default=1800, help="per-cell timeout in seconds")
    args = ap.parse_args()

    nbs = section_notebooks()
    missing = [p for p in nbs if not p.exists()]
    if missing:
        print("Missing:", *missing, sep="\n  ")
        return 1

    errors, warnings = check(nbs)
    for w in warnings:
        print("WARN ", w)
    for e in errors:
        print("ERROR", e)
    print(f"{len(errors)} error(s), {len(warnings)} warning(s)")
    if args.check:
        return 1 if errors else 0
    if errors:
        print("Fix the errors before building.")
        return 1

    merged = merge(nbs)
    OUT_DIR.mkdir(exist_ok=True)
    out = OUT_DIR / args.output
    if not args.no_exec:
        from nbclient import NotebookClient

        print(f"Executing {len(merged.cells)} cells…")
        NotebookClient(merged, timeout=args.timeout, kernel_name="python3",
                       resources={"metadata": {"path": str(NB_DIR)}}).execute()
    nbformat.write(merged, out)
    print("Wrote", out.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
