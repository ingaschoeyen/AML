"""
CLI entry point for the Dutch Engineering Drawing IR system.

Usage:
    python main.py [options]

Options:
    --mode       Search mode: bm25 | hybrid  (default: hybrid)
    --top-k      Number of results to return  (default: 10)
    --index-dir  Path to the saved index      (default: config.INDEX_DIR)
    --road       Filter results to this road  (e.g. N338)
    --hm         Filter results near this hectometer position
    --hm-radius  Hectometer tolerance for --hm filter (default: 1.0)

After startup, enter queries interactively. Quit with Ctrl+C or Ctrl+D.
Output: JSON array per query printed to stdout.
"""

import argparse
import json
import sys
from pathlib import Path

import config
from coordinates import geocode_place
from preprocessing import download_nltk_data
from searcher import Searcher


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Search OCR'd engineering drawings (Dutch)."
    )
    p.add_argument("--mode",      choices=["bm25", "hybrid"],
                                  default="hybrid",                         help="Search mode (default: hybrid)")
    p.add_argument("--top-k",     type=int,   default=config.DEFAULT_TOP_K, help="Number of results")
    p.add_argument("--index-dir", type=Path,  default=config.INDEX_DIR,     help="Directory containing saved index files")
    p.add_argument("--road",      type=str,   default=None,                 help="Filter results to this road (e.g. N338)")
    p.add_argument("--hm",        type=float, default=None,                 help="Filter results near this hectometer position")
    p.add_argument("--hm-radius", type=float, default=1.0,                  help="Hectometer tolerance in km (default: 1.0)")
    return p.parse_args()


def main() -> None:
    download_nltk_data()
    args = parse_args()

    index_dir = Path(args.index_dir)
    if not index_dir.exists():
        print(
            f"Index directory not found: {index_dir}\n"
            "Run index_builder.py first.",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        searcher = Searcher(index_dir)
    except Exception as exc:
        print(f"Failed to load index: {exc}", file=sys.stderr)
        sys.exit(1)

    # Warm up models before the query loop
    if args.mode == "hybrid":
        searcher._load_bge_model()

    filters: dict = dict(
        road=args.road, hm=args.hm, hm_radius=args.hm_radius,
        place_x=None, place_y=None, place_radius=2000.0,
    )

    def print_status() -> None:
        parts = []
        if filters["road"]:
            parts.append(f"road={filters['road']}" + (f" hm={filters['hm']}±{filters['hm_radius']}" if filters["hm"] is not None else ""))
        if filters["place_x"] is not None:
            parts.append(f"place=({filters['place_x']}, {filters['place_y']}) radius={filters['place_radius']:.0f}m")
        print(f"Filters: {', '.join(parts) or '(none)'}", file=sys.stderr)

    def handle_command(line: str) -> bool:
        """Handle :set / :clear / :status commands. Returns True if handled."""
        parts = line.strip().split()
        cmd = parts[0].lower()

        if cmd == ":status":
            print_status()
            return True

        if cmd == ":clear":
            if len(parts) < 2:
                filters.update(road=None, hm=None, place_x=None, place_y=None)
                print("Filters cleared.", file=sys.stderr)
            else:
                key = parts[1].lower()
                if key in ("road", "hm"):
                    filters[key] = None
                elif key == "place":
                    filters.update(place_x=None, place_y=None)
                else:
                    print(f"Unknown filter '{key}'. Options: road, hm, place", file=sys.stderr)
                    return True
                print(f"Cleared {key}.", file=sys.stderr)
            return True

        if cmd == ":set":
            if len(parts) < 3:
                print("Usage: :set <road|hm|hm-radius|place|place-radius> <value>", file=sys.stderr)
                return True
            key, val = parts[1].lower(), " ".join(parts[2:])
            if key == "road":
                filters["road"] = val.upper()
            elif key == "hm":
                try:
                    filters["hm"] = float(val)
                except ValueError:
                    print(f"Invalid hm value: {val}", file=sys.stderr)
            elif key in ("hm-radius", "hm_radius"):
                try:
                    filters["hm_radius"] = float(val)
                except ValueError:
                    print(f"Invalid hm-radius value: {val}", file=sys.stderr)
            elif key == "place":
                print(f"Geocoding '{val}' ...", file=sys.stderr)
                result = geocode_place(val)
                if result:
                    filters["place_x"], filters["place_y"] = result
                    print(f"Resolved to RD ({filters['place_x']}, {filters['place_y']})", file=sys.stderr)
                else:
                    print(f"Could not geocode '{val}'.", file=sys.stderr)
                    return True
            elif key in ("place-radius", "place_radius"):
                try:
                    filters["place_radius"] = float(val)
                except ValueError:
                    print(f"Invalid place-radius value: {val}", file=sys.stderr)
            else:
                print(f"Unknown filter '{key}'. Options: road, hm, hm-radius, place, place-radius", file=sys.stderr)
                return True
            print_status()
            return True

        return False

    if filters["road"]:
        print_status()
    print("Ready. Enter a query, or :set/:clear/:status to manage filters. Ctrl+C/D to quit.", file=sys.stderr)

    try:
        while True:
            try:
                print("\nQuery> ", end="", flush=True, file=sys.stderr)
                query = input()
            except EOFError:
                break

            if not query.strip():
                continue

            if query.lstrip().startswith(":"):
                handle_command(query.strip())
                continue

            if args.mode == "bm25":
                results = searcher.search_bm25(query, top_k=args.top_k, **filters)
            else:
                results = searcher.search_hybrid(query, top_k=args.top_k, **filters)

            print(json.dumps(results, ensure_ascii=False, indent=2))
            sys.stdout.flush()

    except KeyboardInterrupt:
        pass

    print("\nBye.", file=sys.stderr)


if __name__ == "__main__":
    main()
