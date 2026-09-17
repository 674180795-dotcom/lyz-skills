#!/usr/bin/env python3
"""Render each PDF page to a PNG for mandatory visual inspection."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="将 PDF 逐页转换为 PNG，供视觉验收。")
    parser.add_argument("input", help="PDF 文件")
    parser.add_argument("--output-dir", "-o", required=True, help="PNG 输出目录")
    parser.add_argument("--dpi", type=int, default=160, help="渲染 DPI，默认 160")
    args = parser.parse_args()

    source = Path(args.input).expanduser().resolve()
    if not source.is_file() or source.read_bytes()[:5] != b"%PDF-":
        parser.error(f"输入不是有效 PDF：{source}")
    if not 96 <= args.dpi <= 300:
        parser.error("DPI 必须在 96–300 之间")
    pdftoppm = shutil.which("pdftoppm")
    if not pdftoppm:
        parser.error("未找到 pdftoppm，无法生成逐页 PNG")

    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    prefix = output_dir / "page"
    completed = subprocess.run(
        [pdftoppm, "-png", "-r", str(args.dpi), str(source), str(prefix)],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        parser.error(completed.stderr.strip() or "pdftoppm 执行失败")
    pages = sorted(output_dir.glob("page-*.png"))
    if not pages:
        parser.error("没有生成任何页面图片")
    print(
        json.dumps(
            {"ok": True, "pdf": str(source), "dpi": args.dpi, "pages": [str(page) for page in pages]},
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
