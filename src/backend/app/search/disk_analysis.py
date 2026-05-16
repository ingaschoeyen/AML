"""
Analyse disk usage split between documents and photos in a directory tree.

Usage:
    python disk_analysis.py [root_dir]   (default: ./Files)
"""

import sys
from collections import defaultdict
from pathlib import Path

DOCUMENT_EXTS = {".pdf", ".doc", ".docx", ".txt", ".msg", ".xls", ".xlsx", ".ppt", ".pptx"}
PHOTO_EXTS    = {".jpg", ".jpeg", ".png", ".gif", ".tif", ".tiff", ".bmp", ".webp", ".heic"}


def fmt_size(n_bytes: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n_bytes < 1024:
            return f"{n_bytes:.1f} {unit}"
        n_bytes /= 1024
    return f"{n_bytes:.1f} TB"


def analyse(root: Path) -> None:
    # Per-category totals
    totals: dict[str, dict] = {
        "documents": {"count": 0, "bytes": 0, "exts": defaultdict(int)},
        "photos":    {"count": 0, "bytes": 0, "exts": defaultdict(int)},
        "other":     {"count": 0, "bytes": 0, "exts": defaultdict(int)},
    }

    # Per-subfolder breakdown (one level below root)
    folder_stats: dict[Path, dict[str, int]] = defaultdict(lambda: {"docs": 0, "photos": 0, "other": 0})

    for path in root.rglob("*"):
        if not path.is_file():
            continue

        size = path.stat().st_size
        ext  = path.suffix.lower()

        # Determine which top-level subfolder this belongs to
        try:
            rel_parts = path.relative_to(root).parts
            subfolder = root / rel_parts[0] if len(rel_parts) > 1 else root
        except ValueError:
            subfolder = root

        if ext in DOCUMENT_EXTS:
            cat = "documents"
            folder_stats[subfolder]["docs"] += size
        elif ext in PHOTO_EXTS:
            cat = "photos"
            folder_stats[subfolder]["photos"] += size
        else:
            cat = "other"
            folder_stats[subfolder]["other"] += size

        totals[cat]["count"] += 1
        totals[cat]["bytes"] += size
        totals[cat]["exts"][ext] += size

    total_bytes = sum(v["bytes"] for v in totals.values()) or 1

    # ── Summary ──────────────────────────────────────────────────────────────
    print(f"\nDisk usage analysis — {root}\n")
    print(f"{'Category':<12}  {'Files':>6}  {'Size':>10}  {'Share':>6}")
    print("─" * 42)
    for cat in ("documents", "photos", "other"):
        d = totals[cat]
        pct = d["bytes"] / total_bytes * 100
        print(f"{cat:<12}  {d['count']:>6}  {fmt_size(d['bytes']):>10}  {pct:>5.1f}%")
    print("─" * 42)
    print(f"{'TOTAL':<12}  {sum(v['count'] for v in totals.values()):>6}  "
          f"{fmt_size(total_bytes):>10}  100.0%")

    # ── Extension breakdown ───────────────────────────────────────────────────
    for cat in ("documents", "photos"):
        exts = totals[cat]["exts"]
        if not exts:
            continue
        print(f"\n  {cat.capitalize()} by extension:")
        for ext, size in sorted(exts.items(), key=lambda x: -x[1]):
            print(f"    {ext or '(none)':<10}  {fmt_size(size):>10}")

    # ── Per-subfolder breakdown ───────────────────────────────────────────────
    if len(folder_stats) > 1:
        print(f"\n{'Subfolder':<40}  {'Docs':>10}  {'Photos':>10}  {'Other':>10}")
        print("─" * 76)
        for folder in sorted(folder_stats):
            s = folder_stats[folder]
            name = folder.relative_to(root) if folder != root else Path("(root)")
            print(f"{str(name):<40}  {fmt_size(s['docs']):>10}  "
                  f"{fmt_size(s['photos']):>10}  {fmt_size(s['other']):>10}")

    # ── Potential savings ─────────────────────────────────────────────────────
    photo_bytes = totals["photos"]["bytes"]
    if photo_bytes:
        print(f"\nRemoving photos would free {fmt_size(photo_bytes)} "
              f"({photo_bytes / total_bytes * 100:.1f}% of total).")


if __name__ == "__main__":
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("./Files")
    if not root.exists():
        print(f"Directory not found: {root}", file=sys.stderr)
        sys.exit(1)
    analyse(root)
