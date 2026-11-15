"""Convert a conservative subset of a self-contained LaTeX report to Proof Notes."""
import argparse
from pathlib import Path
import sys

from latex_import import convert


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="self-contained .tex source")
    parser.add_argument("-o", "--output", type=Path, required=True, help="new Markdown output file; existing files are not overwritten")
    args = parser.parse_args(argv)
    try:
        source = args.source.read_text(encoding="utf-8")
        macro_path = Path(__file__).resolve().parent / "docs/tex-macros.txt"
        macros = dict(line.split(":", 1) for line in macro_path.read_text().splitlines() if line and not line.startswith("%") and ":" in line)
        result, warnings = convert(source, macros)
        with args.output.open("x", encoding="utf-8") as out:
            out.write(result)
    except (OSError, ValueError) as error:
        print(f"Import failed: {error}", file=sys.stderr)
        return 1
    print(f"Wrote {args.output}. Review {len(warnings)} diagnostic(s):", file=sys.stderr)
    for warning in warnings:
        print(f"  {warning}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
