"""PDF → DOCX 轉換核心（保留文字、版面與圖片）。"""

from __future__ import annotations

from pathlib import Path

from pdf2docx import Converter


def convert_pdf_to_docx(
    pdf_path: str | Path,
    docx_path: str | Path | None = None,
    *,
    start: int = 0,
    end: int | None = None,
    password: str | None = None,
) -> Path:
    """
    將 PDF 轉成 DOCX，並盡量保留圖片與版面。

    Args:
        pdf_path: 來源 PDF 路徑
        docx_path: 輸出 DOCX 路徑；未指定時與 PDF 同目錄、同檔名
        start: 起始頁（0-based，含）
        end: 結束頁（0-based，不含）；None 表示到最後一頁
        password: PDF 密碼（若有加密）

    Returns:
        實際輸出的 DOCX 路徑
    """
    pdf_path = Path(pdf_path).expanduser().resolve()
    if not pdf_path.is_file():
        raise FileNotFoundError(f"找不到 PDF 檔案：{pdf_path}")
    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError(f"不是 PDF 檔案：{pdf_path}")

    if docx_path is None:
        docx_path = pdf_path.with_suffix(".docx")
    else:
        docx_path = Path(docx_path).expanduser().resolve()
        if docx_path.is_dir():
            docx_path = docx_path / f"{pdf_path.stem}.docx"
        elif docx_path.suffix.lower() != ".docx":
            docx_path = docx_path.with_suffix(".docx")

    docx_path.parent.mkdir(parents=True, exist_ok=True)

    cv = Converter(str(pdf_path), password=password)
    try:
        # pdf2docx 會解析文字區塊、表格與內嵌圖片並寫入 DOCX
        cv.convert(str(docx_path), start=start, end=end)
    finally:
        cv.close()

    if not docx_path.is_file():
        raise RuntimeError(f"轉換失敗，未產生檔案：{docx_path}")

    return docx_path


def convert_many(
    pdf_paths: list[str | Path],
    output_dir: str | Path | None = None,
    *,
    password: str | None = None,
) -> list[tuple[Path, Path | None, Exception | None]]:
    """批次轉換。回傳 [(pdf, docx|None, error|None), ...]。"""
    results: list[tuple[Path, Path | None, Exception | None]] = []
    out = Path(output_dir).expanduser().resolve() if output_dir else None
    if out is not None:
        out.mkdir(parents=True, exist_ok=True)

    for pdf in pdf_paths:
        pdf_path = Path(pdf).expanduser().resolve()
        try:
            target = (out / f"{pdf_path.stem}.docx") if out else None
            docx = convert_pdf_to_docx(pdf_path, target, password=password)
            results.append((pdf_path, docx, None))
        except Exception as exc:  # noqa: BLE001 - 批次時收集錯誤
            results.append((pdf_path, None, exc))
    return results
