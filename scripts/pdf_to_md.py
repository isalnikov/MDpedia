#!/usr/bin/env python3
"""Convert PDF to markdown via pdftotext with page markers."""
import re
import subprocess
import sys
from pathlib import Path


def pdf_to_md(pdf: Path, out: Path) -> int:
    title = pdf.stem.replace("_", " ")
    raw = subprocess.check_output(
        ["pdftotext", "-layout", str(pdf), "-"],
        stderr=subprocess.DEVNULL,
    ).decode("utf-8", errors="replace")

    lines: list[str] = [
        f"# {title}",
        "",
        f"_Source: `{pdf.name}`_",
        "",
    ]
    page = 0
    for line in raw.splitlines():
        if line.strip() == "\f" or line == "\f":
            continue
        if "\f" in line:
            parts = line.split("\f")
            for i, part in enumerate(parts):
                if i > 0:
                    page += 1
                    lines.extend(["", f"<!-- page {page} -->", ""])
                if part.strip():
                    lines.append(part.rstrip())
        else:
            if not lines or lines[-1].startswith("<!-- page"):
                pass
            lines.append(line.rstrip())

    text = "\n".join(lines)
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    out.write_text(text, encoding="utf-8")
    return len(text)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    out_dir = root / "books-md"
    out_dir.mkdir(exist_ok=True)
    for pdf in sorted(root.glob("*.pdf")):
        out = out_dir / f"{pdf.stem}.md"
        size = pdf_to_md(pdf, out)
        print(f"{pdf.name} -> {out.name} ({size:,} chars)")


if __name__ == "__main__":
    main()