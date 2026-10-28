"""命令列：PDF → DOCX。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from converter import convert_many, convert_pdf_to_docx


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="將 PDF 轉成 DOCX（保留文字、版面與圖片）",
    )
    parser.add_argument(
        "pdf",
        nargs="+",
        help="一個或多個 PDF 檔案路徑",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="輸出路徑：單檔時可為 .docx；多檔時為輸出資料夾",
    )
    parser.add_argument(
        "-p",
        "--password",
        default=None,
        help="PDF 開啟密碼（若有加密）",
    )
    parser.add_argument(
        "--start",
        type=int,
        default=0,
        help="起始頁（從 0 開始，預設 0）",
    )
    parser.add_argument(
        "--end",
        type=int,
        default=None,
        help="結束頁（不含；預設轉到最後一頁）",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    pdfs = [Path(p) for p in args.pdf]

    missing = [str(p) for p in pdfs if not p.is_file()]
    if missing:
        print("找不到檔案：", file=sys.stderr)
        for m in missing:
            print(f"  - {m}", file=sys.stderr)
        return 1

    if len(pdfs) == 1:
        try:
            out = convert_pdf_to_docx(
                pdfs[0],
                args.output,
                start=args.start,
                end=args.end,
                password=args.password,
            )
        except Exception as exc:  # noqa: BLE001
            print(f"轉換失敗：{exc}", file=sys.stderr)
            return 1
        print(f"完成：{out}")
        return 0

    if args.start != 0 or args.end is not None:
        print("多檔批次時不支援 --start / --end，請逐檔指定。", file=sys.stderr)
        return 1

    results = convert_many(pdfs, args.output, password=args.password)
    failed = 0
    for pdf, docx, err in results:
        if err is None:
            print(f"完成：{pdf.name} → {docx}")
        else:
            failed += 1
            print(f"失敗：{pdf.name} — {err}", file=sys.stderr)

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
