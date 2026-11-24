#!/usr/bin/env python3
"""Convert PDFs in sql/ to sql/books-md/."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pdf_to_md import pdf_to_md  # noqa: E402


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    sql_dir = root / "sql"
    out_dir = sql_dir / "books-md"
    out_dir.mkdir(parents=True, exist_ok=True)
    for pdf in sorted(sql_dir.glob("*.pdf")):
        out = out_dir / f"{pdf.stem}.md"
        size = pdf_to_md(pdf, out)
        print(f"{pdf.name} -> sql/books-md/{out.name} ({size:,} chars)")


if __name__ == "__main__":
    main()